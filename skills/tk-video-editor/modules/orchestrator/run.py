#!/usr/bin/env python3
"""Run the TK video workflow orchestrator.

The orchestrator only coordinates module outputs. It writes intermediate JSON
files and stops before rendering if upstream decisions need revision.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
MODULES = SKILL_ROOT / "modules"


def run_module(module: str, input_path: Path, out_path: Path) -> None:
    script = MODULES / module / "run.py"
    if not script.exists():
        raise SystemExit(f"module runner not found: {script}")
    subprocess.run(
        [sys.executable, str(script), "--input", str(input_path), "--out", str(out_path)],
        check=True,
        cwd=str(SKILL_ROOT),
    )


def run_human_hook_module(input_path: Path, out_path: Path, project_dir: Path) -> None:
    script = MODULES / "human_hook_generation" / "run.py"
    if not script.exists():
        raise SystemExit(f"module runner not found: {script}")
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--input",
            str(input_path),
            "--out",
            str(out_path),
            "--project-dir",
            str(project_dir),
            "--dry-run",
        ],
        check=True,
        cwd=str(SKILL_ROOT),
    )


def run_reference_hook_module(input_path: Path, out_path: Path, frame_index_out: Path, project_dir: Path) -> None:
    script = MODULES / "reference_hook_analysis" / "run.py"
    if not script.exists():
        raise SystemExit(f"module runner not found: {script}")
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--input",
            str(input_path),
            "--out",
            str(out_path),
            "--frame-index-out",
            str(frame_index_out),
            "--project-dir",
            str(project_dir),
            "--dry-run",
        ],
        check=True,
        cwd=str(SKILL_ROOT),
    )


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {path}")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_script_input(full_input: dict, viral_card_path: Path) -> dict:
    return {
        "viral_pattern_card_ref": str(viral_card_path),
        "viral_pattern_card": load_json(viral_card_path),
        "product": full_input.get("product", {}),
        "platform": full_input.get("platform", full_input.get("target_platform", "TikTok")),
        "video_length": full_input.get("video_length", "25-35s"),
        "tone": full_input.get("tone", "native creator style, casual, not too salesy"),
        "cta": full_input.get("cta", ""),
    }


def build_matching_input(full_input: dict, script_card_path: Path) -> dict:
    return {
        "product_script_card": load_json(script_card_path),
        "asset_library": full_input.get("asset_library", []),
        "editing_style": full_input.get("editing_style", {
            "pace": "fast",
            "average_clip_duration": "1.5-2.5s",
            "platform": full_input.get("platform", full_input.get("target_platform", "TikTok")),
            "aspect_ratio": "9:16",
        }),
    }


def write_orchestrator_report(path: Path, status: str, outputs: dict, notes: list[str]) -> None:
    write_json(path, {
        "status": status,
        "outputs": outputs,
        "notes": notes,
    })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", type=Path, required=True, help="Full workflow input JSON")
    parser.add_argument("--output-dir", "-o", type=Path, default=Path("output"))
    parser.add_argument("--render", action="store_true", help="Render only if an EDL is provided and no revision flag exists")
    parser.add_argument("--edl", type=Path, default=None, help="Optional render-compatible EDL JSON")
    args = parser.parse_args()

    full_input = load_json(args.input)
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    account_input = out_dir / "_orchestrator_account_input.json"
    reference_hook_input = out_dir / "_orchestrator_reference_hook_input.json"
    script_input = out_dir / "_orchestrator_script_input.json"
    matching_input = out_dir / "_orchestrator_matching_input.json"
    human_hook_input = out_dir / "_orchestrator_human_hook_input.json"

    human_hook_observation = out_dir / "human_hook_observation.json"
    hook_frame_index = out_dir / "hook_frame_index.json"
    viral_card = out_dir / "viral_pattern_card.json"
    human_hook_card = out_dir / "human_hook_card.json"
    script_card = out_dir / "product_script_card.json"
    shot_plan = out_dir / "shot_matching_plan.json"
    render_report = out_dir / "render_report.json"
    orchestrator_report = out_dir / "orchestrator_report.json"
    final_video = out_dir / "final_video.mp4"

    outputs = {
        "human_hook_observation": str(human_hook_observation),
        "hook_frame_index": str(hook_frame_index),
        "viral_pattern_card": str(viral_card),
        "human_hook_card": str(human_hook_card),
        "product_script_card": str(script_card),
        "shot_matching_plan": str(shot_plan),
        "render_report": str(render_report),
        "final_video": str(final_video) if args.render else None,
    }
    notes: list[str] = []

    account_payload = {
        "account_url": full_input.get("account_url", ""),
        "video_list": full_input.get("video_list", []),
        "target_platform": full_input.get("target_platform", full_input.get("platform", "TikTok")),
        "analysis_goal": full_input.get("analysis_goal", "Extract reusable product-marketing video structures"),
    }
    write_json(account_input, account_payload)
    reference_payload = {
        **full_input,
        "project_dir": str(args.input.resolve().parent),
    }
    write_json(reference_hook_input, reference_payload)
    run_reference_hook_module(reference_hook_input, human_hook_observation, hook_frame_index, args.input.resolve().parent)
    run_module("viral_deconstruction", account_input, viral_card)

    human_hook_payload = {
        **full_input,
        "human_hook_observation": load_json(human_hook_observation),
        "viral_pattern_card": load_json(viral_card),
        "project_dir": str(args.input.resolve().parent),
    }
    write_json(human_hook_input, human_hook_payload)
    run_human_hook_module(human_hook_input, human_hook_card, args.input.resolve().parent)

    write_json(script_input, build_script_input(full_input, viral_card))
    run_module("product_script_rewrite", script_input, script_card)

    write_json(matching_input, build_matching_input(full_input, script_card))
    run_module("asset_matching", matching_input, shot_plan)

    shot_plan_data = load_json(shot_plan)
    if shot_plan_data.get("needs_script_revision"):
        notes.append("asset_matching returned needs_script_revision=true; rendering skipped.")
        write_json(render_report, {
            "status": "blocked",
            "inputs": {"shot_matching_plan": str(shot_plan), "edl": str(args.edl) if args.edl else None},
            "outputs": {"final_video": None, "render_report": str(render_report)},
            "notes": notes + shot_plan_data.get("risk_notes", []),
        })
        write_orchestrator_report(orchestrator_report, "blocked", outputs, notes)
        return

    if args.render:
        if not args.edl:
            notes.append("--render was requested but no --edl was provided; rendering skipped.")
            render_status_input = shot_plan
            subprocess.run([
                sys.executable,
                str(MODULES / "video_rendering" / "run.py"),
                "--input",
                str(render_status_input),
                "--report-out",
                str(render_report),
            ], check=True, cwd=str(SKILL_ROOT))
            write_orchestrator_report(orchestrator_report, "planned", outputs, notes)
            return

        subprocess.run([
            sys.executable,
            str(MODULES / "video_rendering" / "run.py"),
            "--input",
            str(shot_plan),
            "--edl",
            str(args.edl),
            "--video-out",
            str(final_video),
            "--report-out",
            str(render_report),
            "--render",
        ], check=True, cwd=str(SKILL_ROOT))
        write_orchestrator_report(orchestrator_report, "rendered", outputs, notes)
        return

    subprocess.run([
        sys.executable,
        str(MODULES / "video_rendering" / "run.py"),
        "--input",
        str(shot_plan),
        "--report-out",
        str(render_report),
    ], check=True, cwd=str(SKILL_ROOT))
    write_orchestrator_report(orchestrator_report, "planned", outputs, notes)


if __name__ == "__main__":
    main()
