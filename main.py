#!/usr/bin/env python3
"""Copy the finished front page to the make.fun output directory."""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
DEST = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.png"


def main():
    if not SOURCE.is_file():
        raise SystemExit(f"missing {SOURCE.name}; run make_image.py first")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, DEST)
    DEST.chmod(0o644)
    expected = SOURCE.stat().st_size
    actual = DEST.stat().st_size
    if actual != expected:
        raise SystemExit(f"short copy: {actual} of {expected} bytes")
    print(DEST)
    print(actual)


if __name__ == "__main__":
    main()
