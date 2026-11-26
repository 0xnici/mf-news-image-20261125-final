#!/usr/bin/env python3
"""
make.fun news-image-20261125 entry point.
Python 3.13 standard library only — copies the committed entry.png asset to the output directory.
"""

import os
import shutil
import sys
from pathlib import Path


def main() -> int:
    # Source asset is committed alongside this script
    src = Path(__file__).resolve().parent / "entry.png"

    # Output directory: MAKEFUN_OUTPUT_DIR if set, else /output
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    dst = out_dir / "entry.png"

    # Copy the asset
    shutil.copy2(src, dst)

    # Basic validation (stdio only, no external deps)
    data = dst.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        print("ERROR: output is not a valid PNG", file=sys.stderr)
        return 1

    import struct
    w, h = struct.unpack(">II", data[16:24])
    if not (1 <= w <= 1024 and 1 <= h <= 1024):
        print(f"ERROR: dimensions {w}x{h} exceed 1024x1024 gate", file=sys.stderr)
        return 1

    size = dst.stat().st_size
    if size > 5 * 1024 * 1024:
        print(f"ERROR: file size {size} exceeds 5 MiB limit", file=sys.stderr)
        return 1

    print(f"OK: {dst}  {w}x{h}  {size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())