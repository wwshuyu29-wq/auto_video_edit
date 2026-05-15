#!/usr/bin/env python3
"""Create an SRT file from timed caption JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def fmt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    hours, rem = divmod(ms, 3600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captions_json", type=Path)
    parser.add_argument("-o", "--out", type=Path, required=True)
    args = parser.parse_args()

    captions = json.loads(args.captions_json.read_text())
    if isinstance(captions, dict):
        captions = captions.get("captions", [])

    lines: list[str] = []
    for idx, item in enumerate(captions, 1):
        start = float(item["start"])
        end = float(item["end"])
        text = str(item["text"]).strip()
        lines.extend([str(idx), f"{fmt_time(start)} --> {fmt_time(end)}", text, ""])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote SRT -> {args.out}")


if __name__ == "__main__":
    main()
