#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Langton's Ant Diagnostic Script
快速检查高速公路是否出现以及何时出现
"""

import numpy as np
import sys

class LangtonsAnt:
    DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    
    def __init__(self, size=200):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.pos = np.array([size // 2, size // 2])
        self.dir_idx = 0
        self.position_history = [self.pos.copy()]
        self.step_count = 0
        
    def step(self):
        x, y = self.pos
        current_color = self.grid[x, y]
        
        if current_color == 0:
            self.dir_idx = (self.dir_idx + 1) % 4
            self.grid[x, y] = 1
        else:
            self.dir_idx = (self.dir_idx - 1) % 4
            self.grid[x, y] = 0
        
        dx, dy = self.DIRECTIONS[self.dir_idx]
        x = (x + dx) % self.size
        y = (y + dy) % self.size
        self.pos = np.array([x, y])
        
        self.position_history.append(self.pos.copy())
        self.step_count += 1
    
    def measure_alignment(self, window=100):
        if len(self.position_history) < window + 1:
            return 0.0
        
        recent = np.array(self.position_history[-(window+1):])
        displacements = np.diff(recent, axis=0)
        
        # Handle wrapping
        for i in range(len(displacements)):
            for j in range(2):
                if displacements[i, j] > self.size / 2:
                    displacements[i, j] -= self.size
                elif displacements[i, j] < -self.size / 2:
                    displacements[i, j] += self.size
        
        # Compute mean direction
        mean_dir = np.mean(displacements, axis=0)
        mean_norm = np.linalg.norm(mean_dir)
        
        if mean_norm < 1e-10:
            return 0.0
        
        # Alignment with mean direction
        alignments = []
        for v in displacements:
            v_norm = np.linalg.norm(v)
            if v_norm > 1e-10:
                alignments.append(np.dot(v, mean_dir) / (v_norm * mean_norm))
        
        return float(np.mean(alignments)) if alignments else 0.0

def main():
    print("Langton's Ant Highway Detection Diagnostic")
    print("=" * 60)
    
    ant = LangtonsAnt(size=200)
    check_interval = 1000
    max_steps = 20000  # Increased for better highway detection
    
    print(f"\nRunning {max_steps} steps, checking every {check_interval}...")
    print("\nStep     | Alignment | Net Displacement | Status")
    print("-" * 70)
    
    highway_detected = False
    highway_start = None
    
    for step in range(max_steps):
        ant.step()
        
        if step % check_interval == 0 and step > 1000:
            alignment = ant.measure_alignment(window=500)
            
            # Also check net displacement (highway moves diagonally)
            if len(ant.position_history) > 1000:
                recent_pos = np.array(ant.position_history[-1000:])
                net_displacement = np.linalg.norm(recent_pos[-1] - recent_pos[0])
            else:
                net_displacement = 0
            
            status = ""
            if alignment > 0.85 or net_displacement > 500:
                status = "✓ HIGHWAY DETECTED"
                if not highway_detected:
                    highway_detected = True
                    highway_start = step
            elif alignment > 0.6 or net_displacement > 300:
                status = "↗ High order"
            elif alignment > 0.3 or net_displacement > 100:
                status = "→ Medium order"
            else:
                status = "↺ Chaotic"
            
            print(f"{step:8d} | {alignment:9.3f} | {net_displacement:16.1f} | {status}")
    
    print("\n" + "=" * 60)
    if highway_detected:
        print(f"✓ Highway emerged at step ~{highway_start}")
        print(f"  Expected range: 8000-12000")
        if 8000 <= highway_start <= 12000:
            print(f"  ✓ Within expected range!")
        else:
            print(f"  ⚠ Outside expected range")
    else:
        print("✗ No highway detected in this run")
        print("  Possible reasons:")
        print("  - Need longer evolution time")
        print("  - Grid size too small")
        print("  - Different initial conditions needed")
    
    print("\nFinal grid statistics:")
    print(f"  Black cells: {np.sum(ant.grid == 1)} ({100*np.sum(ant.grid == 1)/ant.grid.size:.1f}%)")
    print(f"  White cells: {np.sum(ant.grid == 0)} ({100*np.sum(ant.grid == 0)/ant.grid.size:.1f}%)")

if __name__ == "__main__":
    main()
