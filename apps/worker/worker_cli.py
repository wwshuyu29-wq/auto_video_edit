#!/usr/bin/env python3
"""Minimal local worker CLI for the auto video workflow.

This is the first cloud-worker stepping stone. It runs from the command line
and calls the existing tk-video-editor skill through packages/skill-core.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_CORE_SRC = REPO_ROOT / "packages" / "skill-core" / "src"
sys.path.insert(0, str(SKILL_CORE_SRC))

from auto_video_skill_core import run_module  # noqa: E402


STAGES = ("viral_deconstruction", "product_script_rewrite", "asset_matching")


@dataclass
class ProjectFiles:
    project_dir: Path
    output_dir: Path
    viral_pattern_card: Path
    product_script_card: Path
    shot_matching_plan: Path
    asset_library: Path
    orchestrator_account_input: Path
    orchestrator_script_input: Path


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def normalize_asset_library(data: Any) -> list[dict[str, Any]]:
    """Return a plain list of asset dictionaries from known library shapes."""
    if isinstance(data, list):
        assets = data
    elif isinstance(data, dict) and isinstance(data.get("assets"), list):
        assets = data["assets"]
    else:
        raise SystemExit("Asset library must be a list or an object with an `assets` list.")

    normalized = [asset for asset in assets if isinstance(asset, dict)]
    if len(normalized) != len(assets):
        raise SystemExit("Asset library contains non-object entries; cannot run asset matching.")
    return normalized


def project_files(project_dir: Path) -> ProjectFiles:
    output_dir = project_dir / "output"
    return ProjectFiles(
        project_dir=project_dir,
        output_dir=output_dir,
        viral_pattern_card=output_dir / "viral_pattern_card.json",
        product_script_card=output_dir / "product_script_card.json",
        shot_matching_plan=output_dir / "shot_matching_plan.json",
        asset_library=output_dir / "asset_library.json",
        orchestrator_account_input=output_dir / "_orchestrator_account_input.json",
        orchestrator_script_input=output_dir / "_orchestrator_script_input.json",
    )


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing {label}: {path}")


def inspect_project(args: argparse.Namespace) -> None:
    files = project_files(args.project_dir.resolve())
    summary = {
        "project_dir": str(files.project_dir),
        "output_dir_exists": files.output_dir.exists(),
        "artifacts": {
            "viral_pattern_card": files.viral_pattern_card.exists(),
            "product_script_card": files.product_script_card.exists(),
            "shot_matching_plan": files.shot_matching_plan.exists(),
            "asset_library": files.asset_library.exists(),
            "orchestrator_account_input": files.orchestrator_account_input.exists(),
            "orchestrator_script_input": files.orchestrator_script_input.exists(),
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def build_stage_input(stage: str, files: ProjectFiles, temp_dir: Path) -> Path:
    if stage == "viral_deconstruction":
        require_file(files.orchestrator_account_input, "viral deconstruction input")
        return files.orchestrator_account_input

    if stage == "product_script_rewrite":
        require_file(files.orchestrator_script_input, "product script rewrite input")
        return files.orchestrator_script_input

    if stage == "asset_matching":
        require_file(files.product_script_card, "product script card")
        require_file(files.asset_library, "asset library")
        assets = normalize_asset_library(load_json(files.asset_library))
        input_path = temp_dir / "asset_matching_input.json"
        write_json(
            input_path,
            {
                "product_script_card": load_json(files.product_script_card),
                "asset_library": assets,
                "editing_style": {
                    "pace": "fast",
                    "average_clip_duration": "1.5-2.5s",
                    "platform": "TikTok",
                    "aspect_ratio": "9:16",
                },
            },
        )
        return input_path

    raise SystemExit(f"Unsupported stage: {stage}")


def default_output_path(stage: str, files: ProjectFiles) -> Path:
    if stage == "viral_deconstruction":
        return files.viral_pattern_card
    if stage == "product_script_rewrite":
        return files.product_script_card
    if stage == "asset_matching":
        return files.shot_matching_plan
    raise SystemExit(f"Unsupported stage: {stage}")


def run_stage(args: argparse.Namespace) -> None:
    files = project_files(args.project_dir.resolve())
    if args.stage not in STAGES:
        raise SystemExit(f"Unsupported stage: {args.stage}. Choose one of: {', '.join(STAGES)}")

    temp_root = Path(tempfile.mkdtemp(prefix="auto-video-worker-"))
    try:
        input_path = build_stage_input(args.stage, files, temp_root)
        temp_out = temp_root / f"{args.stage}_output.json"
        final_out = args.out.resolve() if args.out else default_output_path(args.stage, files)

        print(f"stage: {args.stage}")
        print(f"project: {files.project_dir}")
        print(f"input: {input_path}")
        print(f"dry_run: {args.dry_run}")
        print(f"output: {temp_out if args.dry_run else final_out}")

        completed = run_module(
            args.stage,
            ["--input", str(input_path), "--out", str(temp_out if args.dry_run else final_out)],
            cwd=files.project_dir,
        )

        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")

        if completed.returncode != 0:
            raise SystemExit(completed.returncode)

        output_path = temp_out if args.dry_run else final_out
        require_file(output_path, "stage output")
        output_json = load_json(output_path)
        print("result: ok")
        print(f"top_level_keys: {', '.join(output_json.keys()) if isinstance(output_json, dict) else type(output_json).__name__}")
    finally:
        if args.keep_temp:
            print(f"temp_dir: {temp_root}")
        else:
            shutil.rmtree(temp_root, ignore_errors=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect project artifacts without running a stage.")
    inspect_parser.add_argument("--project-dir", required=True, type=Path)
    inspect_parser.set_defaults(func=inspect_project)

    run_parser = subparsers.add_parser("run-stage", help="Run one workflow stage through skill-core.")
    run_parser.add_argument("--project-dir", required=True, type=Path)
    run_parser.add_argument("--stage", required=True, choices=STAGES)
    run_parser.add_argument("--out", type=Path, default=None, help="Optional output path. Defaults to project output artifact.")
    run_parser.add_argument("--dry-run", action="store_true", help="Run into a temporary file without changing project outputs.")
    run_parser.add_argument("--keep-temp", action="store_true", help="Keep temporary files for debugging.")
    run_parser.set_defaults(func=run_stage)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
