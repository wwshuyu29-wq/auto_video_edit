#!/usr/bin/env python3
"""Prepend a short cover still to a captioned video."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cover", type=Path, required=True)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=0.6)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-loop",
        "1",
        "-t",
        f"{args.duration:.3f}",
        "-i",
        str(args.cover),
        "-i",
        str(args.video),
        "-filter_complex",
        "[0:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[c];"
        "[1:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[v];"
        "[c][v]concat=n=2:v=1:a=0[outv]",
        "-map",
        "[outv]",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-movflags",
        "+faststart",
        str(args.out),
    ]
    run(cmd)

    report = {
        "status": "cover_prepended",
        "cover": str(args.cover),
        "video": str(args.video),
        "out": str(args.out),
        "cover_duration_s": args.duration,
        "notes": ["Caption text is unchanged; the cover is inserted as a short first-frame segment."],
    }
    args.out.with_suffix(".cover_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
