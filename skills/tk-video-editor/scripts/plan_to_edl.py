#!/usr/bin/env python3
"""Validate a TK shot plan and emit render.py-compatible EDL JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(plan: dict) -> list[str]:
    errors: list[str] = []
    sources = plan.get("sources")
    segments = plan.get("segments")
    if not isinstance(sources, dict) or not sources:
        errors.append("sources must be a non-empty object")
    if not isinstance(segments, list) or not segments:
        errors.append("segments must be a non-empty list")
        return errors

    for idx, seg in enumerate(segments):
        prefix = f"segments[{idx}]"
        source = seg.get("source")
        if source not in sources:
            errors.append(f"{prefix}.source does not exist in sources: {source}")
        try:
            start = float(seg.get("start"))
            end = float(seg.get("end"))
            if start < 0 or end <= start:
                errors.append(f"{prefix} has invalid start/end")
        except (TypeError, ValueError):
            errors.append(f"{prefix}.start and end must be numbers")
        if not seg.get("beat"):
            errors.append(f"{prefix}.beat is required")
    return errors


def convert(plan: dict) -> dict:
    ranges = []
    total = 0.0
    for seg in plan["segments"]:
        start = float(seg["start"])
        end = float(seg["end"])
        total += end - start
        ranges.append({
            "source": seg["source"],
            "start": start,
            "end": end,
            "beat": seg.get("beat", ""),
            "quote": seg.get("copy", seg.get("quote", "")),
            "reason": seg.get("reason", ""),
        })

    return {
        "version": 1,
        "sources": plan["sources"],
        "ranges": ranges,
        "grade": plan.get("grade", ""),
        "overlays": plan.get("overlays", []),
        "subtitles": plan.get("subtitles"),
        "total_duration_s": round(total, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("shot_plan", type=Path)
    parser.add_argument("-o", "--out", type=Path, required=True)
    args = parser.parse_args()

    plan = json.loads(args.shot_plan.read_text())
    errors = validate(plan)
    if errors:
        raise SystemExit("\n".join(errors))

    edl = convert(plan)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    print(f"wrote EDL -> {args.out}")


if __name__ == "__main__":
    main()
