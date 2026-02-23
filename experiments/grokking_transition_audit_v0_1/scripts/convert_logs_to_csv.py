"""
Convert grokking logs.jsonl to audit CSV format.

Extracts PT-MSS proxy signals:
- d_force: grad_norm change (force redistribution proxy)
- d_info: H_spec change (information re-encoding proxy)
- d_constraint: correction_rate change (constraint reorganization proxy)
"""
import argparse
import csv
import json
import os
from pathlib import Path


def extract_grad_norm_total(log_entry):
    grad_norms = log_entry.get("grad_norm_by_layer", {})
    total = sum(v for v in grad_norms.values() if isinstance(v, (int, float)))
    return total


def extract_h_spec(log_entry, layer="unembed.weight"):
    h_spec = log_entry.get("H_spec_by_layer", {})
    return h_spec.get(layer, 0.0)


def extract_correction_rate(log_entry):
    return log_entry.get("correction_rate", 0.0)


def compute_diff(series):
    diffs = [0.0]
    for i in range(1, len(series)):
        diffs.append(abs(series[i] - series[i - 1]))
    return diffs


def compute_smoothed_diff(series, window=3):
    smoothed = []
    for i in range(len(series)):
        lo = max(0, i - window + 1)
        smoothed.append(sum(series[lo:i+1]) / (i - lo + 1))
    diffs = [0.0]
    for i in range(1, len(smoothed)):
        diffs.append(abs(smoothed[i] - smoothed[i - 1]))
    return diffs


def convert_log_to_csv(log_path, output_path, alt_layer=None):
    with open(log_path, "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]
    
    if not entries:
        return False
    
    steps = []
    grad_norms = []
    h_specs = []
    correction_rates = []
    test_accs = []
    r_effs = []
    
    for e in entries:
        steps.append(int(e.get("step", 0)))
        grad_norms.append(extract_grad_norm_total(e))
        h_specs.append(extract_h_spec(e))
        correction_rates.append(extract_correction_rate(e))
        test_accs.append(float(e.get("test_acc", 0.0)))
        r_effs.append(float(e.get("r_eff_by_layer", {}).get("unembed.weight", 0.0)))
    
    d_force = compute_diff(grad_norms)
    d_info = compute_diff(h_specs)
    d_constraint = compute_diff(correction_rates)
    
    d_force_alt = compute_smoothed_diff(grad_norms, window=5)
    d_info_alt = compute_diff(r_effs)
    d_constraint_alt = compute_smoothed_diff(correction_rates, window=5)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fieldnames = [
        "step", "d_force", "d_info", "d_constraint",
        "d_force_alt", "d_info_alt", "d_constraint_alt", "acc_test"
    ]
    
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for i in range(len(steps)):
            w.writerow({
                "step": steps[i],
                "d_force": d_force[i],
                "d_info": d_info[i],
                "d_constraint": d_constraint[i],
                "d_force_alt": d_force_alt[i],
                "d_info_alt": d_info_alt[i],
                "d_constraint_alt": d_constraint_alt[i],
                "acc_test": test_accs[i],
            })
    
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to logs.jsonl or directory")
    parser.add_argument("--output", required=True, help="Output CSV path or directory")
    parser.add_argument("--alt-layer", default=None, help="Alternative layer for alt family")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if input_path.is_file():
        convert_log_to_csv(str(input_path), str(output_path), args.alt_layer)
        print(f"Converted {input_path} -> {output_path}")
    elif input_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)
        converted = 0
        for log_file in sorted(input_path.glob("**/logs.jsonl")):
            seed_dir = log_file.parent.name
            out_file = output_path / f"{seed_dir}.csv"
            if convert_log_to_csv(str(log_file), str(out_file), args.alt_layer):
                converted += 1
        print(f"Converted {converted} log files to {output_path}")
    else:
        raise FileNotFoundError(f"Input not found: {input_path}")


if __name__ == "__main__":
    main()
