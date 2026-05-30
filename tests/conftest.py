"""Pytest configuration: make the batch-prepare source importable.

The package directory name contains a hyphen, so it is not importable as a
normal package. We add its ``src`` directory (and the repo root, for the
``shared`` package) to ``sys.path``.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH_PREPARE_SRC = os.path.join(
    REPO_ROOT, "packages", "batch-prepare", "src"
)

for path in (REPO_ROOT, BATCH_PREPARE_SRC):
    if path not in sys.path:
        sys.path.insert(0, path)
