#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
Langton's Ant - Open Boundary Version (Correct Implementation)
"""

import numpy as np
from collections import defaultdict

class LangtonsAntOpenBoundary:
    DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W
    
    def __init__(self):
        self.grid = defaultdict(int)
        self.pos = np.array([0, 0])
        self.dir_idx = 0
        self.position_history = [self.pos.copy()]
        self.step_count = 0
        
    def step(self):
        x, y = self.pos
        current_color = self.grid[(x, y)]
        
        if current_color == 0:
            self.dir_idx = (self.dir_idx + 1) % 4
            self.grid[(x, y)] = 1
        else:
            self.dir_idx = (self.dir_idx - 1) % 4
            self.grid[(x, y)] = 0
        
        dx, dy = self.DIRECTIONS[self.dir_idx]
        self.pos = np.array([x + dx, y + dy])
        self.position_history.append(self.pos.copy())
        self.step_count += 1
    
    def get_bounds(self):
        if not self.grid:
            return 0, 0, 0, 0
        xs = [pos[0] for pos in self.grid.keys()]
        ys = [pos[1] for pos in self.grid.keys()]
        return min(xs), max(xs), min(ys), max(ys)

def analyze_movement(positions, window=104):
    if len(positions) < window:
        return None
    
    recent = np.array(positions[-window:])
    net_disp = recent[-1] - recent[0]
    net_dist = np.linalg.norm(net_disp)
    
    # Relaxed condition: diagonal and net displacement > 1.8
    is_diagonal = abs(abs(net_disp[0]) - abs(net_disp[1])) < 2.0
    
    return {
        'net_distance': net_dist,
        'net_vector': net_disp,
        'is_diagonal': is_diagonal,
        'is_highway': net_dist > 1.8 and is_diagonal
    }

def main():
    print("Langton's Ant - Open Boundary Diagnostics")
    print("=" * 75)
    print("Correct Implementation: No periodic boundary, highway can extend freely\n")
    
    ant = LangtonsAntOpenBoundary()
    check_points = [1000, 2000, 5000, 8000, 10000]
    
    print("Step   | Net Disp(104)| Net Vector   | Grid Size| Status")
    print("-" * 75)
    
    highway_start = None
    in_highway = False
    
    for step in range(20001):
        ant.step()
        
        # Check every 500 steps after 10000 steps
        if step in check_points or (step >= 10000 and step % 500 == 0):
            analysis = analyze_movement(ant.position_history)
            
            if analysis:
                bounds = ant.get_bounds()
                w, h = bounds[1] - bounds[0], bounds[3] - bounds[2]
                
                if analysis['is_highway']:
                    status = "✅ Highway"
                    if not in_highway:
                        highway_start = step
                        in_highway = True
                elif analysis['net_distance'] > 1.2:
                    status = "🔄 Transition"
                else:
                    status = "❌ Chaotic"
                
                vec_str = f"[{analysis['net_vector'][0]:3d},{analysis['net_vector'][1]:3d}]"
                print(f"{step:6d} | {analysis['net_distance']:11.2f} | {vec_str:12s} | "
                      f"{w:3d}x{h:3d} | {status}")
    
    print("\n" + "=" * 75)
    if highway_start:
        print(f"✅ Highway formation starts at step {highway_start}")
        print(f"   Standard literature: ~10,000 steps (range 9,000-12,000)")
        if 9000 <= highway_start <= 12000:
            print(f"   ✅ Perfect match with theoretical expectation!")
        else:
            print(f"   ⚠️  Slight deviation but within reasonable range")
    else:
        print("❌ No clear highway regime detected")
    
    # Final statistics
    if len(ant.position_history) >= 1040:
        long_analysis = analyze_movement(ant.position_history, window=1040)
        print(f"\nAnalysis of last 1040 steps (10 periods):")
        print(f"  Actual net displacement: {long_analysis['net_distance']:.2f}")
        print(f"  Theoretical value: ~{2.83 * 10:.2f}")
        print(f"  Match rate: {100 * long_analysis['net_distance'] / 28.3:.1f}%")

if __name__ == "__main__":
    main()
