"""
Training script for Li² scaling law verification experiments
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from tqdm import tqdm

# Add parent to path for imports
import sys
sys.path.append(str(Path(__file__).parent))

from data.generate_data import generate_modular_addition_data, get_dataloader
from models.grok_net import create_model


def evaluate(model, dataloader, device):
    """Evaluate model accuracy"""
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for x, y in dataloader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            preds = logits.argmax(dim=-1)
            correct += (preds == y).sum().item()
            total += len(y)
            
    return correct / total if total > 0 else 0.0


def compute_gradient_stats(model, dataloader, criterion, device):
    """
    Compute gradient statistics for analysis
    Following Li² paper: track ||G_F||
    """
    model.train()
    
    # Get a batch
    x, y = next(iter(dataloader))
    x, y = x.to(device), y.to(device)
    
    model.zero_grad()

    # Prefer a feature-level G_F proxy when available (TwoLayerGrokNet).
    gf_norm = None
    gf_align_target_w_mean = None
    gf_align_target_w_std = None
    if hasattr(model, "get_hidden_activations") and hasattr(model, "output"):
        h = model.get_hidden_activations(x)
        h.retain_grad()
        logits = model.output(h)
        loss = criterion(logits, y)
        loss.backward()
        if h.grad is not None:
            gf_norm = h.grad.norm().item()
            try:
                # Alignment proxy: cosine similarity between dL/dh and the target-class output weight.
                # This is a crude but operational “structure” measure for G_F beyond its norm.
                g = h.grad.detach()  # [B, K]
                w = model.output.weight.detach()  # [M, K]
                w_y = w[y]  # [B, K]
                g_n = g / (g.norm(dim=-1, keepdim=True) + 1e-12)
                w_n = w_y / (w_y.norm(dim=-1, keepdim=True) + 1e-12)
                cos = (g_n * w_n).sum(dim=-1)  # [B]
                gf_align_target_w_mean = cos.mean().item()
                gf_align_target_w_std = cos.std(unbiased=False).item()
            except Exception:
                gf_align_target_w_mean = None
                gf_align_target_w_std = None
    else:
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()

    # Collect parameter gradient norms + feature-level proxy if available
    grad_norms = {
        "gf_norm": gf_norm,
        "gf_align_target_w_mean": gf_align_target_w_mean,
        "gf_align_target_w_std": gf_align_target_w_std,
    }
    for name, param in model.named_parameters():
        if param.grad is not None:
            grad_norms[name] = param.grad.norm().item()

    return grad_norms


def train_epoch(model, dataloader, optimizer, criterion, device):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    n_batches = 0
    
    for x, y in dataloader:
        x, y = x.to(device), y.to(device)
        
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        n_batches += 1
        
    return total_loss / n_batches if n_batches > 0 else 0.0


def train(config):
    """
    Main training function
    
    Args:
        config: dict with training configuration
        
    Returns:
        dict with training results
    """
    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Data
    data = generate_modular_addition_data(
        M=config['M'],
        train_ratio=config['train_ratio'],
        seed=config['seed']
    )
    
    train_loader = get_dataloader(
        data['train'], 
        batch_size=config.get('batch_size', 512),
        shuffle=True
    )
    test_loader = get_dataloader(
        data['test'],
        batch_size=config.get('batch_size', 512),
        shuffle=False
    )
    
    print(f"M = {config['M']}, Train: {data['train_size']}, Test: {data['test_size']}")
    
    # Model
    model = create_model(
        M=config['M'],
        hidden_dim=config.get('hidden_dim', 2048),
        n_layers=config.get('n_layers', 2),
        activation=config.get('activation', 'quadratic'),
        zero_init_output=config.get('zero_init_output', False)
    )
    model = model.to(device)
    
    # Optimizer
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config.get('lr', 1e-3),
        weight_decay=config.get('weight_decay', 2e-4)
    )
    
    criterion = nn.CrossEntropyLoss()
    
    # Training history
    history = {
        'train_loss': [],
        'train_acc': [],
        'test_acc': [],
        'grad_norms': [],
        'epochs': [],
    }
    
    # Grokking detection
    grok_epoch = None
    grok_threshold = config.get('grok_threshold', 0.95)
    
    # Training loop
    epochs = config.get('epochs', 50000)
    log_interval = config.get('log_interval', 100)
    grad_log_interval = config.get('grad_log_interval', 1000)
    
    pbar = tqdm(range(epochs), desc="Training")
    for epoch in pbar:
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device)
        
        # Evaluate periodically
        if epoch % log_interval == 0 or epoch == epochs - 1:
            train_acc = evaluate(model, train_loader, device)
            test_acc = evaluate(model, test_loader, device)
            
            history['epochs'].append(epoch)
            history['train_loss'].append(train_loss)
            history['train_acc'].append(train_acc)
            history['test_acc'].append(test_acc)
            
            # Gradient stats (feature-level proxy + parameter norms)
            if grad_log_interval and epoch % grad_log_interval == 0:
                grad_norms = compute_gradient_stats(model, train_loader, criterion, device)
                history['grad_norms'].append({'epoch': epoch, **grad_norms})
            
            pbar.set_postfix({
                'loss': f'{train_loss:.4f}',
                'train': f'{train_acc:.2%}',
                'test': f'{test_acc:.2%}'
            })
            
            # Grokking detection
            if grok_epoch is None and test_acc >= grok_threshold:
                grok_epoch = epoch
                print(f"\n[GROK] Detected at epoch {epoch} (test_acc={test_acc:.2%})")
            
            # Early stopping
            if train_acc > 0.99 and test_acc > 0.99:
                print(f"\n[OK] Converged at epoch {epoch}")
                break
    
    # Results
    results = {
        'config': config,
        'grok_happened': grok_epoch is not None,
        'grok_epoch': grok_epoch,
        'final_train_acc': history['train_acc'][-1] if history['train_acc'] else 0,
        'final_test_acc': history['test_acc'][-1] if history['test_acc'] else 0,
        'total_epochs': epoch + 1,
        'history': history,
    }
    
    return results


def save_results(results, output_dir):
    """Save results to JSON file"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = results['config']
    # Use 3 decimals to avoid collisions when sweeping around log(M)/M (often ~0.0x).
    filename = f"M{config['M']}_ratio{config['train_ratio']:.3f}_seed{config['seed']}.json"
    filepath = output_dir / filename
    
    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    results_json = json.loads(json.dumps(results, default=convert))
    
    with open(filepath, 'w') as f:
        json.dump(results_json, f, indent=2)
        
    print(f"Results saved to {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description='Train grokking model')
    parser.add_argument('--M', type=int, default=71, help='Group size')
    parser.add_argument('--ratio', type=float, default=0.4, help='Training data ratio')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--hidden_dim', type=int, default=2048, help='Hidden layer width')
    parser.add_argument('--activation', type=str, default='quadratic', 
                        choices=['quadratic', 'relu', 'gelu', 'silu'])
    parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--weight_decay', type=float, default=2e-4, help='Weight decay')
    parser.add_argument('--epochs', type=int, default=50000, help='Max epochs')
    parser.add_argument('--log_interval', type=int, default=100, help='Log metrics every N epochs')
    parser.add_argument('--grad_log_interval', type=int, default=1000, help='Log gradient stats every N epochs')
    parser.add_argument('--output_dir', type=str, default='results', help='Output directory')
    parser.add_argument('--zero_init', action='store_true', help='Use zero-init for output layer')
    
    args = parser.parse_args()
    
    config = {
        'M': args.M,
        'train_ratio': args.ratio,
        'seed': args.seed,
        'hidden_dim': args.hidden_dim,
        'activation': args.activation,
        'lr': args.lr,
        'weight_decay': args.weight_decay,
        'epochs': args.epochs,
        'log_interval': args.log_interval,
        'grad_log_interval': args.grad_log_interval,
        'zero_init_output': args.zero_init,
        'timestamp': datetime.now().isoformat(),
    }
    
    print("=" * 60)
    print("Li² Scaling Law Verification Experiment")
    print("=" * 60)
    print(f"Config: {json.dumps(config, indent=2)}")
    print("=" * 60)
    
    results = train(config)
    
    print("\n" + "=" * 60)
    print("Results Summary")
    print("=" * 60)
    print(f"Grok happened: {results['grok_happened']}")
    print(f"Grok epoch: {results['grok_epoch']}")
    print(f"Final train acc: {results['final_train_acc']:.2%}")
    print(f"Final test acc: {results['final_test_acc']:.2%}")
    
    save_results(results, args.output_dir)


if __name__ == "__main__":
    main()
