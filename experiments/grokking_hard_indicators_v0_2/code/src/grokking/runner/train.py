from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

import torch
from tqdm import tqdm

from grokking.datasets.modular_addition import make_loaders
from grokking.estimators.cleanup_correction import correction_rate_on_corrupted
from grokking.estimators.spectral import spectral_metrics_from_weight
from grokking.models.tiny_transformer import TinyTransformer
from grokking.runner.checkpoint import save_checkpoint
from grokking.runner.device import pick_device
from grokking.utils.config import dump_yaml, load_yaml, make_run_paths
from grokking.utils.jsonl import append_jsonl
from grokking.utils.seed import set_seed


@torch.no_grad()
def evaluate(
    *,
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    device: torch.device,
) -> tuple[float, float]:
    model.eval()
    total = 0
    correct = 0
    total_loss = 0.0
    loss_fn = torch.nn.CrossEntropyLoss()
    for batch in loader:
        x = batch["x"].to(device)
        y = batch["y_true"].to(device)
        logits = model(x)
        loss = loss_fn(logits, y)
        total_loss += float(loss.item()) * x.shape[0]
        pred = torch.argmax(logits, dim=-1)
        correct += int((pred == y).sum().item())
        total += int(x.shape[0])
    return total_loss / max(total, 1), correct / max(total, 1)


def _get_weight_by_name(model: torch.nn.Module, name: str) -> torch.Tensor:
    for n, p in model.named_parameters():
        if n == name:
            return p
    raise KeyError(f"Parameter not found: {name}")


def train_one_run(*, spec: dict[str, Any], out_dir: str | Path, seed: int) -> Path:
    set_seed(seed)
    device = pick_device()

    boundary = spec["boundary"]
    p = int(boundary["modulus_p"])
    dataset = boundary["dataset"]
    model_cfg = boundary["model"]
    train_cfg = boundary["training"]
    time_cfg = spec["time"]

    batch_size = int(train_cfg["batch_size"])
    train_loader, test_loader = make_loaders(
        p=p,
        train_size=int(dataset["train_size"]),
        test_size=int(dataset["test_size"]),
        batch_size=batch_size,
        seed=seed,
        corruption=dataset.get("corruption", {}),
    )

    model = TinyTransformer(
        vocab_size=p,
        d_model=int(model_cfg["width"]),
        n_heads=int(model_cfg["heads"]),
        n_layers=int(model_cfg["layers"]),
        dropout=float(model_cfg.get("dropout", 0.0)),
        n_classes=p,
    ).to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(train_cfg["lr"]),
        weight_decay=float(train_cfg["weight_decay"]),
    )
    loss_fn = torch.nn.CrossEntropyLoss()

    max_steps = int(train_cfg["max_steps"])
    checkpoint_every = int(time_cfg["checkpoint_every_steps"])

    paths = make_run_paths(out_dir, seed)
    paths.run_dir.mkdir(parents=True, exist_ok=True)
    paths.checkpoints_dir.mkdir(parents=True, exist_ok=True)

    resolved = dict(spec)
    resolved.setdefault("run", {})
    resolved["run"]["seed"] = seed
    resolved["run"]["device"] = str(device)
    dump_yaml(resolved, paths.resolved_config_path)

    spectral_cfg = spec.get("estimators", {}).get("H_spec", {})
    normalize_entropy = bool(spectral_cfg.get("normalize", True))
    matrices = spec.get("state", {}).get("spectral_matrices", ["unembed.weight"])
    corr_cfg = spec.get("estimators", {}).get("Correction_Rate", {})

    data_iter = iter(train_loader)
    pbar = tqdm(range(1, max_steps + 1), desc=f"seed={seed} ({device})", ncols=100)
    for step in pbar:
        try:
            batch = next(data_iter)
        except StopIteration:
            data_iter = iter(train_loader)
            batch = next(data_iter)

        model.train()
        x = batch["x"].to(device)
        y = batch["y"].to(device)
        logits = model(x)
        loss = loss_fn(logits, y)

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        if step % checkpoint_every != 0 and step != 1 and step != max_steps:
            continue

        train_loss = float(loss.item())
        test_loss, test_acc = evaluate(model=model, loader=test_loader, device=device)

        h_spec_by_layer: dict[str, float] = {}
        r_eff_by_layer: dict[str, float] = {}
        for name in matrices:
            w = _get_weight_by_name(model, name)
            sm = spectral_metrics_from_weight(w, normalize_entropy=normalize_entropy)
            h_spec_by_layer[name] = sm.h_spec
            r_eff_by_layer[name] = sm.r_eff

        correction_rate = correction_rate_on_corrupted(
            model=model,
            train_loader=train_loader,
            device=device,
            samples=int(corr_cfg.get("samples", 2048)),
            batch_size=int(corr_cfg.get("batch_size", batch_size)),
        )

        weight_norm_by_layer = {n: float(p.detach().float().norm().item()) for n, p in model.named_parameters()}
        grad_norm_by_layer = {
            n: float((p.grad.detach().float().norm().item()) if p.grad is not None else 0.0)
            for n, p in model.named_parameters()
        }

        record = {
            "step": step,
            "train_loss": train_loss,
            "test_loss": float(test_loss),
            "test_acc": float(test_acc),
            "H_spec_by_layer": h_spec_by_layer,
            "r_eff_by_layer": r_eff_by_layer,
            "correction_rate": float(correction_rate),
            "weight_norm_by_layer": weight_norm_by_layer,
            "grad_norm_by_layer": grad_norm_by_layer,
            "ts": time.time(),
        }
        append_jsonl(paths.logs_path, record)
        save_checkpoint(
            path=paths.checkpoints_dir / f"step_{step}.pt",
            step=step,
            model=model,
            optimizer=optimizer,
            extra={"test_acc": test_acc, "test_loss": test_loss},
        )
        pbar.set_postfix({"loss": f"{train_loss:.4f}", "test_acc": f"{test_acc:.3f}", "corr": f"{correction_rate:.3f}"})

    return paths.run_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, help="Path to estimator_spec.yaml")
    parser.add_argument("--out", required=True, help="Output directory for runs/")
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    spec = load_yaml(args.spec)
    train_one_run(spec=spec, out_dir=args.out, seed=args.seed)


if __name__ == "__main__":
    main()

