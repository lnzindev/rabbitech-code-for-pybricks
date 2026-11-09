#!/usr/bin/env python3
"""Run from repo root: python tools/update_integrity.py"""
from pathlib import Path
import hashlib
root = Path(__file__).resolve().parents[1]
names = ["base.py", "memoria.py"] + [f"saida_{i}.py" for i in range(1, 9)]
print("EXPECTED = {")
for name in names:
    digest = hashlib.sha256((root / name).read_bytes()).hexdigest()
    print(f'    "{name}": "{digest}",')
print("}")
