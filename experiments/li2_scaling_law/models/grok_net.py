"""
Neural network models for grokking experiments
Matches Li² paper experimental setup
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class TwoLayerGrokNet(nn.Module):
    """
    2-layer network for grokking experiments
    
    Architecture: X -> Linear -> Activation -> Linear -> Output
    
    Matches Li² paper setup:
    - No bias terms
    - Quadratic activation as primary option
    - One-hot input encoding
    """
    
    def __init__(self, M, hidden_dim=2048, activation='quadratic'):
        """
        Args:
            M: group size (input is 2*M one-hot, output is M classes)
            hidden_dim: hidden layer width (K in paper)
            activation: 'quadratic', 'relu', 'gelu', or 'silu'
        """
        super().__init__()
        
        self.M = M
        self.hidden_dim = hidden_dim
        self.activation_name = activation
        
        input_dim = 2 * M  # one-hot encoding for (a, b)
        
        # W in paper notation
        self.embed = nn.Linear(input_dim, hidden_dim, bias=False)
        
        # V in paper notation
        self.output = nn.Linear(hidden_dim, M, bias=False)
        
        # Initialize weights
        self._init_weights()
        
    def _init_weights(self):
        """Standard initialization"""
        nn.init.normal_(self.embed.weight, std=0.02)
        nn.init.normal_(self.output.weight, std=0.02)
        
    def _init_weights_zero_output(self):
        """Zero-init for output layer (Sec 3.2 of paper)"""
        nn.init.normal_(self.embed.weight, std=0.02)
        nn.init.zeros_(self.output.weight)
        
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: [batch_size, 2*M] one-hot encoded inputs
            
        Returns:
            logits: [batch_size, M]
        """
        # Hidden layer
        h = self.embed(x)  # [batch, hidden_dim]
        
        # Activation
        if self.activation_name == 'quadratic':
            h = h ** 2
        elif self.activation_name == 'relu':
            h = F.relu(h)
        elif self.activation_name == 'gelu':
            h = F.gelu(h)
        elif self.activation_name == 'silu':
            h = F.silu(h)
        else:
            raise ValueError(f"Unknown activation: {self.activation_name}")
            
        # Output layer
        logits = self.output(h)  # [batch, M]
        
        return logits
    
    def get_hidden_activations(self, x):
        """Get hidden layer activations for analysis"""
        h = self.embed(x)
        if self.activation_name == 'quadratic':
            h = h ** 2
        elif self.activation_name == 'relu':
            h = F.relu(h)
        elif self.activation_name == 'gelu':
            h = F.gelu(h)
        elif self.activation_name == 'silu':
            h = F.silu(h)
        return h


class ThreeLayerGrokNet(nn.Module):
    """
    3-layer network for deeper architecture experiments
    Extension of Li² paper Section 6
    """
    
    def __init__(self, M, hidden_dim=2048, activation='quadratic'):
        super().__init__()
        
        self.M = M
        self.hidden_dim = hidden_dim
        self.activation_name = activation
        
        input_dim = 2 * M
        
        self.layer1 = nn.Linear(input_dim, hidden_dim, bias=False)
        self.layer2 = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.output = nn.Linear(hidden_dim, M, bias=False)
        
        self._init_weights()
        
    def _init_weights(self):
        for layer in [self.layer1, self.layer2, self.output]:
            nn.init.normal_(layer.weight, std=0.02)
            
    def _activate(self, h):
        if self.activation_name == 'quadratic':
            return h ** 2
        elif self.activation_name == 'relu':
            return F.relu(h)
        elif self.activation_name == 'gelu':
            return F.gelu(h)
        elif self.activation_name == 'silu':
            return F.silu(h)
        
    def forward(self, x):
        h = self.layer1(x)
        h = self._activate(h)
        h = self.layer2(h)
        h = self._activate(h)
        logits = self.output(h)
        return logits


def create_model(M, hidden_dim, n_layers=2, activation='quadratic', zero_init_output=False):
    """
    Factory function to create models
    
    Args:
        M: group size
        hidden_dim: hidden layer width
        n_layers: 2 or 3
        activation: activation function name
        zero_init_output: whether to use zero-init for output layer
        
    Returns:
        nn.Module
    """
    if n_layers == 2:
        model = TwoLayerGrokNet(M, hidden_dim, activation)
    elif n_layers == 3:
        model = ThreeLayerGrokNet(M, hidden_dim, activation)
    else:
        raise ValueError(f"Unsupported n_layers: {n_layers}")
        
    if zero_init_output:
        nn.init.zeros_(model.output.weight)
        
    return model


if __name__ == "__main__":
    # Test model creation
    M = 71
    hidden_dim = 2048
    
    model = TwoLayerGrokNet(M, hidden_dim, 'quadratic')
    print(f"Model: {model}")
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Test forward pass
    batch_size = 32
    x = torch.zeros(batch_size, 2 * M)
    for i in range(batch_size):
        a, b = i % M, (i * 7) % M
        x[i, a] = 1.0
        x[i, M + b] = 1.0
        
    logits = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {logits.shape}")
