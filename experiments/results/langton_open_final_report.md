```
python langton_open_final.py
```

Langton's Ant - Open Boundary Diagnostic
===========================================================================
Correct Implementation: No periodic boundaries, highway can extend freely

Step   | 104-step Net Disp | Net Vector   | Grid Size | Status
---------------------------------------------------------------------------
  1000 |        7.00 | [  0, -7]    |  19x 15 | 🔄 Transient
  2000 |        3.00 | [  0,  3]    |  24x 20 | 🔄 Transient
  5000 |       12.21 | [-10,  7]    |  30x 28 | 🔄 Transient
  8000 |        7.81 | [  6,  5]    |  42x 37 | ✅ Highway
 10000 |        4.12 | [ -4,  1]    |  48x 44 | 🔄 Transient
 10500 |        2.24 | [ -2,  1]    |  56x 44 | ✅ Highway
 11000 |        2.24 | [ -2,  1]    |  66x 44 | ✅ Highway
 11500 |        2.24 | [ -2,  1]    |  76x 47 | ✅ Highway
 12000 |        2.24 | [ -2,  1]    |  86x 56 | ✅ Highway
 12500 |        3.61 | [ -2,  3]    |  95x 66 | ✅ Highway
 13000 |        3.61 | [ -2,  3]    | 104x 76 | ✅ Highway
 13500 |        3.61 | [ -2,  3]    | 114x 86 | ✅ Highway
 14000 |        3.61 | [ -2,  3]    | 124x 96 | ✅ Highway
 14500 |        2.24 | [ -2,  1]    | 134x104 | ✅ Highway
 15000 |        2.24 | [ -2,  1]    | 144x114 | ✅ Highway
 15500 |        2.24 | [ -2,  1]    | 152x124 | ✅ Highway
 16000 |        3.61 | [ -2,  3]    | 162x134 | ✅ Highway
 16500 |        3.61 | [ -2,  3]    | 172x144 | ✅ Highway
 17000 |        3.61 | [ -2,  3]    | 182x152 | ✅ Highway
 17500 |        2.24 | [ -2,  1]    | 192x162 | ✅ Highway
 18000 |        2.24 | [ -2,  1]    | 201x172 | ✅ Highway
 18500 |        3.61 | [ -2,  3]    | 210x182 | ✅ Highway
 19000 |        3.61 | [ -2,  3]    | 220x192 | ✅ Highway
 19500 |        2.24 | [ -2,  1]    | 230x200 | ✅ Highway
 20000 |        2.24 | [ -2,  1]    | 240x210 | ✅ Highway

===========================================================================
✅ Highway formation begins at step 8000
   Standard literature: ~10,000 steps (9,000-12,000 range)
   ⚠️  Slight deviation but within reasonable range

Last 1040 steps (10 periods) analysis:
  Actual net displacement: 27.59
  Theoretical value: ~28.30
  Match: 97.5%