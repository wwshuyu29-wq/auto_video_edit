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


STAGES = ("viral_deconstruction", "product_script_rewrite", "asset_matching", "video_rendering")


@dataclass
class ProjectFiles:
    project_dir: Path
    output_dir: Path
    full_workflow_input: Path
    project_job: Path
    viral_pattern_card: Path
    product_script_card: Path
    shot_matching_plan: Path
    asset_library: Path
    final_delivery_dir: Path
    worker_preview_video: Path
    worker_render_report: Path
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
        full_workflow_input=project_dir / "full_workflow_input.json",
        project_job=project_dir / "project_job.json",
        viral_pattern_card=output_dir / "viral_pattern_card.json",
        product_script_card=output_dir / "product_script_card.json",
        shot_matching_plan=output_dir / "shot_matching_plan.json",
        asset_library=output_dir / "asset_library.json",
        final_delivery_dir=output_dir / "final_delivery",
        worker_preview_video=output_dir / "final_delivery" / "worker_preview.mp4",
        worker_render_report=output_dir / "final_delivery" / "worker_render_report.json",
        orchestrator_account_input=output_dir / "_orchestrator_account_input.json",
        orchestrator_script_input=output_dir / "_orchestrator_script_input.json",
    )


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing {label}: {path}")


def relative_to_project(project_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_dir.resolve()))
    except ValueError:
        return str(path.resolve())


def resolve_project_path(project_dir: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return project_dir / path


def inspect_project(args: argparse.Namespace) -> None:
    files = project_files(args.project_dir.resolve())
    summary = {
        "project_dir": str(files.project_dir),
        "output_dir_exists": files.output_dir.exists(),
        "artifacts": {
            "full_workflow_input": files.full_workflow_input.exists(),
            "project_job": files.project_job.exists(),
            "viral_pattern_card": files.viral_pattern_card.exists(),
            "product_script_card": files.product_script_card.exists(),
            "shot_matching_plan": files.shot_matching_plan.exists(),
            "asset_library": files.asset_library.exists(),
            "final_delivery_dir": files.final_delivery_dir.exists(),
            "worker_preview_video": files.worker_preview_video.exists(),
            "worker_render_report": files.worker_render_report.exists(),
            "orchestrator_account_input": files.orchestrator_account_input.exists(),
            "orchestrator_script_input": files.orchestrator_script_input.exists(),
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def build_project_job(project_dir: Path) -> dict[str, Any]:
    files = project_files(project_dir)
    if files.full_workflow_input.exists():
        full = load_json(files.full_workflow_input)
        product = full.get("product", {})
        return {
            "project_id": files.project_dir.name,
            "project_dir": str(files.project_dir),
            "product_name": product.get("product_name", product.get("name", "")),
            "workflow_mode": "fresh",
            "source": {
                "full_workflow_input": relative_to_project(files.project_dir, files.full_workflow_input),
            },
            "artifacts": {
                "viral_pattern_card": relative_to_project(files.project_dir, files.viral_pattern_card),
                "product_script_card": relative_to_project(files.project_dir, files.product_script_card),
                "shot_matching_plan": relative_to_project(files.project_dir, files.shot_matching_plan),
                "asset_library": relative_to_project(files.project_dir, files.asset_library),
            },
            "delivery": {
                "mode": "preview_render",
                "preview_video": relative_to_project(files.project_dir, files.worker_preview_video),
                "render_report": relative_to_project(files.project_dir, files.worker_render_report),
            },
            "stages": [
                {"name": "viral_deconstruction", "mode": "run"},
                {"name": "product_script_rewrite", "mode": "run"},
                {"name": "asset_matching", "mode": "run"},
                {"name": "video_rendering", "mode": "run"},
            ],
        }

    require_file(files.viral_pattern_card, "existing viral pattern card")
    require_file(files.product_script_card, "existing product script card")
    require_file(files.asset_library, "existing asset library")

    product_name = ""
    try:
        product_name = load_json(files.product_script_card).get("product", {}).get("product_name", "")
    except Exception:
        product_name = ""

    return {
        "project_id": files.project_dir.name,
        "project_dir": str(files.project_dir),
        "product_name": product_name,
        "workflow_mode": "mixed",
        "source": {},
        "artifacts": {
            "viral_pattern_card": relative_to_project(files.project_dir, files.viral_pattern_card),
            "product_script_card": relative_to_project(files.project_dir, files.product_script_card),
            "shot_matching_plan": relative_to_project(files.project_dir, files.shot_matching_plan),
            "asset_library": relative_to_project(files.project_dir, files.asset_library),
        },
        "delivery": {
            "mode": "preview_render",
            "preview_video": relative_to_project(files.project_dir, files.worker_preview_video),
            "render_report": relative_to_project(files.project_dir, files.worker_render_report),
        },
        "stages": [
            {"name": "viral_deconstruction", "mode": "reuse_existing"},
            {"name": "product_script_rewrite", "mode": "reuse_existing"},
            {"name": "asset_matching", "mode": "run"},
            {"name": "video_rendering", "mode": "run"},
        ],
        "defaults": {
            "editing_style": {
                "pace": "fast",
                "average_clip_duration": "1.5-2.5s",
                "platform": "TikTok",
                "aspect_ratio": "9:16",
            }
        },
    }


def init_job(args: argparse.Namespace) -> None:
    project_dir = args.project_dir.resolve()
    job = build_project_job(project_dir)
    out = args.out.resolve() if args.out else project_files(project_dir).project_job
    write_json(out, job)
    print(f"wrote {out}")
    print(f"workflow_mode: {job['workflow_mode']}")
    print(f"stages: {', '.join(stage['name'] + ':' + stage['mode'] for stage in job['stages'])}")


def stage_mode(job: dict[str, Any], stage_name: str) -> str:
    for stage in job.get("stages", []):
        if stage.get("name") == stage_name:
            return str(stage.get("mode", "run"))
    raise SystemExit(f"Stage `{stage_name}` is missing from project job.")


def artifact_path(job: dict[str, Any], stage_name: str, project_dir: Path) -> Path:
    artifacts = job.get("artifacts", {})
    mapping = {
        "viral_deconstruction": "viral_pattern_card",
        "product_script_rewrite": "product_script_card",
        "asset_matching": "shot_matching_plan",
        "video_rendering": "shot_matching_plan",
    }
    key = mapping[stage_name]
    path = resolve_project_path(project_dir, artifacts.get(key))
    if path is None:
        raise SystemExit(f"Project job is missing artifact path for `{key}`.")
    return path


def build_run_input_from_full_workflow(
    stage_name: str,
    job: dict[str, Any],
    project_dir: Path,
    temp_dir: Path,
    stage_outputs: dict[str, Path],
) -> Path:
    source = job.get("source", {})
    full_path = resolve_project_path(project_dir, source.get("full_workflow_input"))
    if full_path is None:
        raise SystemExit("Project job does not define `source.full_workflow_input`.")

    full = load_json(full_path)
    out_path = temp_dir / f"{stage_name}_input.json"

    if stage_name == "viral_deconstruction":
        write_json(out_path, full)
        return out_path

    if stage_name == "product_script_rewrite":
        viral_path = stage_outputs.get("viral_deconstruction")
        if viral_path is None:
            raise SystemExit("Missing viral_deconstruction output before product_script_rewrite.")
        write_json(
            out_path,
            {
                "viral_pattern_card": load_json(viral_path),
                "product": full.get("product", {}),
                "platform": full.get("platform", full.get("target_platform", "TikTok")),
                "video_length": full.get("video_length", "25-35s"),
                "tone": full.get("tone", "native creator style"),
                "cta": full.get("cta", full.get("product", {}).get("cta", "try the product")),
            },
        )
        return out_path

    if stage_name == "asset_matching":
        script_path = stage_outputs.get("product_script_rewrite")
        if script_path is None:
            raise SystemExit("Missing product_script_rewrite output before asset_matching.")
        write_json(
            out_path,
            {
                "product_script_card": load_json(script_path),
                "asset_library": normalize_asset_library(full.get("asset_library", [])),
                "editing_style": full.get(
                    "editing_style",
                    {
                        "pace": "fast",
                        "average_clip_duration": "1.5-2.5s",
                        "platform": "TikTok",
                        "aspect_ratio": "9:16",
                    },
                ),
            },
        )
        return out_path

    raise SystemExit(f"Unsupported stage: {stage_name}")


def build_run_input_from_mixed_job(
    stage_name: str,
    job: dict[str, Any],
    project_dir: Path,
    temp_dir: Path,
    stage_outputs: dict[str, Path],
) -> Path:
    out_path = temp_dir / f"{stage_name}_input.json"

    if stage_name == "asset_matching":
        script_path = stage_outputs.get("product_script_rewrite")
        if script_path is None:
            raise SystemExit("Missing product_script_rewrite artifact before asset_matching.")
        asset_library_path = resolve_project_path(project_dir, job.get("artifacts", {}).get("asset_library"))
        if asset_library_path is None:
            raise SystemExit("Project job is missing `artifacts.asset_library`.")
        write_json(
            out_path,
            {
                "product_script_card": load_json(script_path),
                "asset_library": normalize_asset_library(load_json(asset_library_path)),
                "editing_style": job.get("defaults", {}).get(
                    "editing_style",
                    {
                        "pace": "fast",
                        "average_clip_duration": "1.5-2.5s",
                        "platform": "TikTok",
                        "aspect_ratio": "9:16",
                    },
                ),
            },
        )
        return out_path

    raise SystemExit(f"Stage `{stage_name}` cannot be built in mixed mode without an explicit input.")


def run_stage_once(
    stage_name: str,
    input_path: Path,
    output_path: Path,
    project_dir: Path,
) -> None:
    completed = run_module(
        stage_name,
        ["--input", str(input_path), "--out", str(output_path)],
        cwd=project_dir,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    require_file(output_path, f"{stage_name} output")


def asset_library_path_for_job(job: dict[str, Any], project_dir: Path, temp_dir: Path) -> Path:
    workflow_mode = job.get("workflow_mode", "fresh")
    if workflow_mode == "fresh":
        source = job.get("source", {})
        full_path = resolve_project_path(project_dir, source.get("full_workflow_input"))
        if full_path is None:
            raise SystemExit("Project job does not define `source.full_workflow_input`.")
        full = load_json(full_path)
        assets = normalize_asset_library(full.get("asset_library", []))
        asset_path = temp_dir / "render_asset_library.json"
        write_json(asset_path, assets)
        return asset_path

    asset_path = resolve_project_path(project_dir, job.get("artifacts", {}).get("asset_library"))
    if asset_path is None:
        raise SystemExit("Project job is missing `artifacts.asset_library`.")
    require_file(asset_path, "asset library for rendering")
    return asset_path


def delivery_path(job: dict[str, Any], key: str, project_dir: Path) -> Path:
    delivery = job.get("delivery", {})
    path = resolve_project_path(project_dir, delivery.get(key))
    if path is None:
        raise SystemExit(f"Project job is missing `delivery.{key}`.")
    return path


def run_render_stage(
    job: dict[str, Any],
    project_dir: Path,
    temp_dir: Path,
    shot_plan_path: Path,
    dry_run: bool,
) -> tuple[Path, Path]:
    asset_library_path = asset_library_path_for_job(job, project_dir, temp_dir)
    final_preview = delivery_path(job, "preview_video", project_dir)
    final_report = delivery_path(job, "render_report", project_dir)

    preview_out = temp_dir / final_preview.name if dry_run else final_preview
    report_out = temp_dir / final_report.name if dry_run else final_report

    completed = run_module(
        "video_rendering",
        [
            "--input",
            str(shot_plan_path),
            "--asset-library",
            str(asset_library_path),
            "--preview-render",
            "--preview-out",
            str(preview_out),
            "--report-out",
            str(report_out),
        ],
        cwd=project_dir,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)

    require_file(preview_out, "preview video output")
    require_file(report_out, "render report output")
    return preview_out, report_out


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

    if stage == "video_rendering":
        require_file(files.shot_matching_plan, "shot matching plan")
        return files.shot_matching_plan

    raise SystemExit(f"Unsupported stage: {stage}")


def default_output_path(stage: str, files: ProjectFiles) -> Path:
    if stage == "viral_deconstruction":
        return files.viral_pattern_card
    if stage == "product_script_rewrite":
        return files.product_script_card
    if stage == "asset_matching":
        return files.shot_matching_plan
    if stage == "video_rendering":
        return files.worker_preview_video
    raise SystemExit(f"Unsupported stage: {stage}")


def run_stage_command(args: argparse.Namespace) -> None:
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
        if args.stage == "video_rendering":
            print(f"output: {temp_out if args.dry_run else final_out}")
            job = {
                "workflow_mode": "mixed",
                "artifacts": {"asset_library": relative_to_project(files.project_dir, files.asset_library)},
                "delivery": {
                    "preview_video": relative_to_project(files.project_dir, final_out),
                    "render_report": relative_to_project(files.project_dir, final_out.with_name("worker_render_report.json")),
                },
            }
            preview_out, report_out = run_render_stage(
                job,
                files.project_dir,
                temp_root,
                input_path,
                args.dry_run,
            )
            print("result: ok")
            print(f"preview_video: {preview_out}")
            print(f"render_report: {report_out}")
            return

        print(f"output: {temp_out if args.dry_run else final_out}")

        run_stage_once(
            args.stage,
            input_path,
            temp_out if args.dry_run else final_out,
            files.project_dir,
        )

        output_path = temp_out if args.dry_run else final_out
        output_json = load_json(output_path)
        print("result: ok")
        print(f"top_level_keys: {', '.join(output_json.keys()) if isinstance(output_json, dict) else type(output_json).__name__}")
    finally:
        if args.keep_temp:
            print(f"temp_dir: {temp_root}")
        else:
            shutil.rmtree(temp_root, ignore_errors=True)


def run_project(args: argparse.Namespace) -> None:
    job_path = args.job_file.resolve()
    job = load_json(job_path)
    project_dir = resolve_project_path(Path.cwd(), job.get("project_dir"))
    if project_dir is None:
        project_dir = job_path.parent
    project_dir = project_dir.resolve()

    temp_root = Path(tempfile.mkdtemp(prefix="auto-video-worker-project-"))
    stage_outputs: dict[str, Path] = {}
    summary: list[dict[str, str]] = []

    try:
        print(f"project: {project_dir}")
        print(f"job: {job_path}")
        print(f"workflow_mode: {job.get('workflow_mode', 'unknown')}")
        print(f"dry_run: {args.dry_run}")

        for stage_name in STAGES:
            mode = stage_mode(job, stage_name)
            print(f"stage: {stage_name} ({mode})")

            if mode == "reuse_existing":
                existing = artifact_path(job, stage_name, project_dir)
                require_file(existing, f"existing artifact for {stage_name}")
                stage_outputs[stage_name] = existing
                summary.append({"stage": stage_name, "mode": mode, "output": str(existing)})
                print(f"reused: {existing}")
                continue

            if mode != "run":
                raise SystemExit(f"Unsupported stage mode `{mode}` for stage `{stage_name}`.")

            if stage_name == "video_rendering":
                shot_plan_path = stage_outputs.get("asset_matching")
                if shot_plan_path is None:
                    raise SystemExit("Missing asset_matching output before video_rendering.")
                preview_out, report_out = run_render_stage(job, project_dir, temp_root, shot_plan_path, args.dry_run)
                summary.append({"stage": stage_name, "mode": mode, "output": str(preview_out), "report": str(report_out)})
                print(f"preview: {preview_out}")
                print(f"report: {report_out}")
                continue

            workflow_mode = job.get("workflow_mode", "fresh")
            if workflow_mode == "fresh":
                input_path = build_run_input_from_full_workflow(stage_name, job, project_dir, temp_root, stage_outputs)
            elif workflow_mode == "mixed":
                input_path = build_run_input_from_mixed_job(stage_name, job, project_dir, temp_root, stage_outputs)
            else:
                raise SystemExit(f"Unsupported workflow mode `{workflow_mode}`.")

            final_out = artifact_path(job, stage_name, project_dir)
            output_path = temp_root / final_out.name if args.dry_run else final_out
            run_stage_once(stage_name, input_path, output_path, project_dir)
            stage_outputs[stage_name] = output_path
            summary.append({"stage": stage_name, "mode": mode, "output": str(output_path)})
            print(f"wrote: {output_path}")

        print("result: ok")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
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

    init_parser = subparsers.add_parser("init-job", help="Create a standard project_job.json from an existing project.")
    init_parser.add_argument("--project-dir", required=True, type=Path)
    init_parser.add_argument("--out", type=Path, default=None)
    init_parser.set_defaults(func=init_job)

    run_parser = subparsers.add_parser("run-stage", help="Run one workflow stage through skill-core.")
    run_parser.add_argument("--project-dir", required=True, type=Path)
    run_parser.add_argument("--stage", required=True, choices=STAGES)
    run_parser.add_argument("--out", type=Path, default=None, help="Optional output path. Defaults to project output artifact.")
    run_parser.add_argument("--dry-run", action="store_true", help="Run into a temporary file without changing project outputs.")
    run_parser.add_argument("--keep_temp", action="store_true", help="Keep temporary files for debugging.")
    run_parser.set_defaults(func=run_stage_command)

    project_parser = subparsers.add_parser("run-project", help="Run a full project workflow from project_job.json.")
    project_parser.add_argument("--job-file", required=True, type=Path)
    project_parser.add_argument("--dry-run", action="store_true", help="Run into temporary files without changing project outputs.")
    project_parser.add_argument("--keep-temp", action="store_true", help="Keep temporary files for debugging.")
    project_parser.set_defaults(func=run_project)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
