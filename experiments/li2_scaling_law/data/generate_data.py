"""
Data generation for modular arithmetic tasks
Matches Li² paper experimental setup
"""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader


class ModularAdditionDataset(Dataset):
    """
    Dataset for modular addition task: (a, b) -> (a + b) mod M
    Uses one-hot encoding for inputs
    """
    
    def __init__(self, M, pairs, labels):
        self.M = M
        self.pairs = pairs
        self.labels = labels
        
    def __len__(self):
        return len(self.pairs)
    
    def __getitem__(self, idx):
        a, b = self.pairs[idx]
        label = self.labels[idx]
        
        # One-hot encoding: [one_hot(a), one_hot(b)]
        x = torch.zeros(2 * self.M)
        x[a] = 1.0
        x[self.M + b] = 1.0
        
        return x, label


def generate_modular_addition_data(M, train_ratio, seed=42):
    """
    Generate train/test split for modular addition
    
    Args:
        M: modulus (group size)
        train_ratio: fraction of M^2 samples for training
        seed: random seed for reproducibility
        
    Returns:
        dict with train/test datasets
    """
    np.random.seed(seed)
    
    # All possible (a, b) pairs
    all_pairs = [(a, b) for a in range(M) for b in range(M)]
    all_labels = [(a + b) % M for a, b in all_pairs]
    
    # Random split
    n_total = len(all_pairs)
    n_train = int(n_total * train_ratio)
    
    indices = np.random.permutation(n_total)
    train_idx = indices[:n_train]
    test_idx = indices[n_train:]
    
    train_pairs = [all_pairs[i] for i in train_idx]
    train_labels = [all_labels[i] for i in train_idx]
    test_pairs = [all_pairs[i] for i in test_idx]
    test_labels = [all_labels[i] for i in test_idx]
    
    return {
        'train': ModularAdditionDataset(M, train_pairs, train_labels),
        'test': ModularAdditionDataset(M, test_pairs, test_labels),
        'train_size': n_train,
        'test_size': n_total - n_train,
        'M': M,
    }


def generate_modular_multiplication_data(M, train_ratio, seed=42):
    """
    Generate train/test split for modular multiplication
    Task: (a, b) -> (a * b) mod M
    
    Note: For multiplicative group, we might want to exclude 0
    """
    np.random.seed(seed)
    
    # All possible (a, b) pairs (including 0 for simplicity)
    all_pairs = [(a, b) for a in range(M) for b in range(M)]
    all_labels = [(a * b) % M for a, b in all_pairs]
    
    # Random split
    n_total = len(all_pairs)
    n_train = int(n_total * train_ratio)
    
    indices = np.random.permutation(n_total)
    train_idx = indices[:n_train]
    test_idx = indices[n_train:]
    
    train_pairs = [all_pairs[i] for i in train_idx]
    train_labels = [all_labels[i] for i in train_idx]
    test_pairs = [all_pairs[i] for i in test_idx]
    test_labels = [all_labels[i] for i in test_idx]
    
    return {
        'train': ModularAdditionDataset(M, train_pairs, train_labels),
        'test': ModularAdditionDataset(M, test_pairs, test_labels),
        'train_size': n_train,
        'test_size': n_total - n_train,
        'M': M,
    }


def get_dataloader(dataset, batch_size, shuffle=True):
    """Create DataLoader from dataset"""
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


if __name__ == "__main__":
    # Test data generation
    M = 71
    train_ratio = 0.4
    
    data = generate_modular_addition_data(M, train_ratio)
    print(f"M = {M}")
    print(f"Train size: {data['train_size']} ({data['train_size'] / M**2:.1%})")
    print(f"Test size: {data['test_size']} ({data['test_size'] / M**2:.1%})")
    
    # Test a sample
    x, y = data['train'][0]
    print(f"Sample input shape: {x.shape}")
    print(f"Sample label: {y}")
