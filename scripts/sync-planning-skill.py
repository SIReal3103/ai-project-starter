#!/usr/bin/env python3
"""Compatibility entry point for bundling only ai-product-planning."""

from pathlib import Path
import runpy
import sys


if __name__ == "__main__":
    script = Path(__file__).with_name("sync-skills.py")
    sys.argv = [str(script), "--skill", "ai-product-planning", *sys.argv[1:]]
    runpy.run_path(str(script), run_name="__main__")
