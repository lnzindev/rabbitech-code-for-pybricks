#!/usr/bin/env python3
"""Compatibilidade com o nome antigo.

Use:
    python tools/update_integrity.py update
    python tools/update_integrity.py verify
"""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("integrity.py")), run_name="__main__")
