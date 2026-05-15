#!/usr/bin/env python3
"""Create a render_report.json and optionally render from an existing EDL."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from _shared import load_json, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", type=Path, required=True, help="shot_matching_plan.json or render input JSON")
    parser.add_argument("--edl", type=Path, default=None, help="Render-compatible EDL JSON")
    parser.add_argument("--asset-library", type=Path, default=None, help="asset_library.json for PNG-caption TikTok preview rendering")
    parser.add_argument("--video-out", type=Path, default=Path("output/final_video.mp4"))
    parser.add_argument("--preview-out", type=Path, default=None, help="Optional preview video output path")
    parser.add_argument("--report-out", type=Path, default=Path("output/render_report.json"))
    parser.add_argument("--render", action="store_true", help="Actually call scripts/render.py when --edl is provided")
    parser.add_argument("--preview-render", action="store_true", help="Render a captioned TikTok preview from shot_matching_plan.json and asset_library.json")
    args = parser.parse_args()

    data = load_json(args.input)
    notes = []
    status = "planned"

    if data.get("needs_script_revision"):
        notes.append("Shot matching requested script or asset revision before final render.")

    if args.preview_render:
        if not args.asset_library:
            raise SystemExit("--preview-render requires --asset-library")
        preview_script = Path(__file__).resolve().parents[2] / "scripts" / "render_tiktok_preview.py"
        preview_out = args.preview_out or args.video_out.with_name("preview.mp4")
        preview_out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "python3",
            str(preview_script),
            "--shot-plan",
            str(args.input),
            "--asset-library",
            str(args.asset_library),
            "--out",
            str(preview_out),
            "--report-out",
            str(args.report_out),
        ], check=True)
        return

    if args.render:
        if not args.edl:
            raise SystemExit("--render requires --edl")
        render_script = Path(__file__).resolve().parents[2] / "scripts" / "render.py"
        args.video_out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "python3",
            str(render_script),
            str(args.edl),
            "-o",
            str(args.video_out),
            "--build-subtitles",
        ], check=True)
        status = "rendered"
    elif args.edl:
        notes.append("EDL provided but --render was not set; no video was rendered.")
    else:
        notes.append("No EDL provided. Use scripts/plan_to_edl.py or a manual EDL before rendering.")

    report = {
        "status": status,
        "inputs": {
            "shot_matching_plan": str(args.input),
            "edl": str(args.edl) if args.edl else None,
        },
        "outputs": {
            "final_video": str(args.video_out) if status == "rendered" else None,
            "render_report": str(args.report_out),
        },
        "notes": notes,
    }
    write_json(args.report_out, report)


if __name__ == "__main__":
    main()
