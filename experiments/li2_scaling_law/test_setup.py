"""
Quick test script to verify experiment setup works
Run this before starting the full sweep
"""

import torch
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent))

from data.generate_data import generate_modular_addition_data, get_dataloader
from models.grok_net import create_model, TwoLayerGrokNet


def test_data_generation():
    """Test data generation"""
    print("Testing data generation...")
    
    M = 23
    train_ratio = 0.4
    
    data = generate_modular_addition_data(M, train_ratio, seed=42)
    
    assert data['train_size'] == int(M * M * train_ratio)
    assert data['test_size'] == M * M - data['train_size']
    
    # Test a sample
    x, y = data['train'][0]
    assert x.shape == (2 * M,)
    assert 0 <= y < M
    
    print(f"  [OK] Data generation works: M={M}, train={data['train_size']}, test={data['test_size']}")
    return True


def test_model():
    """Test model creation and forward pass"""
    print("Testing model...")
    
    M = 23
    hidden_dim = 256
    batch_size = 8
    
    model = create_model(M, hidden_dim, n_layers=2, activation='quadratic')
    
    # Random input
    x = torch.zeros(batch_size, 2 * M)
    for i in range(batch_size):
        a, b = i % M, (i * 3) % M
        x[i, a] = 1.0
        x[i, M + b] = 1.0
    
    # Forward pass
    logits = model(x)
    
    assert logits.shape == (batch_size, M)
    
    # Check gradients flow
    loss = logits.sum()
    loss.backward()
    
    for name, param in model.named_parameters():
        assert param.grad is not None, f"No gradient for {name}"
    
    print(f"  [OK] Model works: params={sum(p.numel() for p in model.parameters()):,}")
    return True


def test_training_step():
    """Test a single training step"""
    print("Testing training step...")
    
    M = 23
    hidden_dim = 256
    
    # Data
    data = generate_modular_addition_data(M, 0.4, seed=42)
    loader = get_dataloader(data['train'], batch_size=32)
    
    # Model
    model = create_model(M, hidden_dim, n_layers=2, activation='quadratic')
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=2e-4)
    criterion = torch.nn.CrossEntropyLoss()
    
    # One step
    x, y = next(iter(loader))
    
    model.train()
    optimizer.zero_grad()
    logits = model(x)
    loss = criterion(logits, y)
    loss.backward()
    optimizer.step()
    
    print(f"  [OK] Training step works: loss={loss.item():.4f}")
    return True


def test_short_training():
    """Test a short training run"""
    print("Testing short training run...")
    
    M = 23
    hidden_dim = 256
    
    # Data
    data = generate_modular_addition_data(M, 0.5, seed=42)
    train_loader = get_dataloader(data['train'], batch_size=64)
    test_loader = get_dataloader(data['test'], batch_size=64, shuffle=False)
    
    # Model
    model = create_model(M, hidden_dim, n_layers=2, activation='quadratic')
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=2e-4)
    criterion = torch.nn.CrossEntropyLoss()
    
    # Train for a few epochs
    for epoch in range(10):
        model.train()
        for x, y in train_loader:
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
    
    # Evaluate
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in test_loader:
            logits = model(x)
            preds = logits.argmax(dim=-1)
            correct += (preds == y).sum().item()
            total += len(y)
    
    acc = correct / total
    print(f"  [OK] Short training works: test_acc={acc:.2%} after 10 epochs")
    return True


def test_activations():
    """Test different activation functions"""
    print("Testing activation functions...")
    
    M = 23
    hidden_dim = 256
    batch_size = 8
    
    x = torch.randn(batch_size, 2 * M)
    
    for activation in ['quadratic', 'relu', 'gelu', 'silu']:
        model = create_model(M, hidden_dim, activation=activation)
        logits = model(x)
        assert logits.shape == (batch_size, M)
        print(f"  [OK] {activation} works")
    
    return True


def main():
    print("=" * 60)
    print("Li² Scaling Law Experiment - Quick Test")
    print("=" * 60)
    
    tests = [
        test_data_generation,
        test_model,
        test_training_step,
        test_short_training,
        test_activations,
    ]
    
    all_passed = True
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"  [FAIL] {e}")
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("All tests passed! [OK]")
        print("\nReady to run experiments:")
        print("  python train.py --M 71 --ratio 0.4 --seed 42")
        print("  python sweep.py --estimate")
    else:
        print("Some tests failed! [FAIL]")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
