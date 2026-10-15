#!/usr/bin/env python3
"""Run the Arm C Language Extensions docset generator from the source tree."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_SRC = SCRIPT_DIR / "generator" / "src"
sys.path.insert(0, str(PACKAGE_SRC))

from arm_acle_docset.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
