#!/usr/bin/env python3
"""Run one project job in the background and persist a simple status file.

This is the thinnest bridge between the web app and the existing worker CLI.
The web layer spawns this script in detached mode. This script then runs the
real worker and records idle/running/completed/failed state for the UI.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKER_CLI = REPO_ROOT / "apps" / "worker" / "worker_cli.py"
STAGE_NAMES = ("reference_hook_analysis", "viral_deconstruction", "human_hook_generation", "product_script_rewrite", "asset_matching", "video_rendering")
OPTIONAL_STAGES = {"reference_hook_analysis", "human_hook_generation"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def build_paths(job_file: Path) -> tuple[Path, Path, Path]:
    job = load_json(job_file)
    project_dir = Path(job["project_dir"]).resolve()
    output_dir = project_dir / "output"
    status_path = output_dir / "worker_run_status.json"
    log_path = output_dir / "worker_run.log"
    return project_dir, status_path, log_path


def build_initial_stages(job_file: Path) -> list[dict[str, Any]]:
    job = load_json(job_file)
    configured = {stage.get("name"): stage.get("mode", "run") for stage in job.get("stages", [])}
    return [
        {
            "name": name,
            "mode": configured.get(name, "skip" if name in OPTIONAL_STAGES else "run"),
            "state": "pending",
            "started_at": None,
            "finished_at": None,
            "output": None,
            "report": None,
        }
        for name in STAGE_NAMES
    ]


def update_stage(
    stages: list[dict[str, Any]],
    stage_name: str,
    *,
    state: str | None = None,
    output: str | None = None,
    report: str | None = None,
) -> None:
    for stage in stages:
        if stage["name"] != stage_name:
            continue
        if state:
            stage["state"] = state
            if state == "running" and not stage.get("started_at"):
                stage["started_at"] = utc_now()
            if state in {"completed", "failed"} and not stage.get("finished_at"):
                stage["finished_at"] = utc_now()
        if output:
            stage["output"] = output
        if report:
            stage["report"] = report
        return


def complete_running_stage(stages: list[dict[str, Any]]) -> None:
    for stage in stages:
        if stage.get("state") == "running":
            update_stage(stages, stage["name"], state="completed")


def parse_stage_line(line: str) -> tuple[str, str | None, str | None] | None:
    if line.startswith("stage: "):
        stage_name = line.removeprefix("stage: ").split(" ", 1)[0].strip()
        if stage_name in STAGE_NAMES:
            return ("start", stage_name, None)

    if line.startswith("reused: "):
        return ("complete_current", line.removeprefix("reused: ").strip(), None)

    if line.startswith("wrote: "):
        return ("complete_current", line.removeprefix("wrote: ").strip(), None)

    if line.startswith("preview: "):
        return ("output_current", line.removeprefix("preview: ").strip(), None)

    if line.startswith("report: "):
        return ("report_current", line.removeprefix("report: ").strip(), None)

    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-file", required=True, type=Path)
    args = parser.parse_args()

    job_file = args.job_file.resolve()
    project_dir, status_path, log_path = build_paths(job_file)
    stages = build_initial_stages(job_file)

    running_state = {
        "state": "running",
        "job_file": str(job_file),
        "project_dir": str(project_dir),
        "pid": None,
        "started_at": utc_now(),
        "finished_at": None,
        "return_code": None,
        "log_path": str(log_path),
        "error": None,
        "stages": stages,
    }
    write_json(status_path, running_state)

    try:
        with log_path.open("a", encoding="utf-8") as log_handle:
            log_handle.write(f"\n[{utc_now()}] starting worker run\n")
            log_handle.write(f"job_file={job_file}\n")
            log_handle.flush()

            command = [sys.executable, "-u", str(WORKER_CLI), "run-project", "--job-file", str(job_file)]
            process = subprocess.Popen(
                command,
                cwd=project_dir,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            running_state["pid"] = process.pid
            write_json(status_path, running_state)

            current_stage: str | None = None
            assert process.stdout is not None
            for line in process.stdout:
                log_handle.write(line)
                log_handle.flush()

                parsed = parse_stage_line(line.strip())
                if not parsed:
                    continue

                action, value, _extra = parsed
                if action == "start":
                    complete_running_stage(stages)
                    current_stage = value
                    update_stage(stages, current_stage, state="running")
                elif action == "complete_current" and current_stage:
                    update_stage(stages, current_stage, state="completed", output=value)
                elif action == "output_current" and current_stage:
                    update_stage(stages, current_stage, output=value)
                elif action == "report_current" and current_stage:
                    update_stage(stages, current_stage, state="completed", report=value)

                write_json(status_path, running_state)

            return_code = process.wait()

            if return_code == 0:
                complete_running_stage(stages)
                state = "completed"
            else:
                state = "failed"
                for stage in stages:
                    if stage.get("state") == "running":
                        update_stage(stages, stage["name"], state="failed")
            write_json(
                status_path,
                {
                    **running_state,
                    "state": state,
                    "finished_at": utc_now(),
                    "return_code": return_code,
                    "error": None if return_code == 0 else f"Worker exited with code {return_code}",
                },
            )
            log_handle.write(f"[{utc_now()}] finished worker run with code={return_code}\n")
    except Exception as error:  # pragma: no cover - defensive bridge
        for stage in stages:
            if stage.get("state") == "running":
                update_stage(stages, stage["name"], state="failed")
        write_json(
            status_path,
            {
                **running_state,
                "state": "failed",
                "finished_at": utc_now(),
                "return_code": -1,
                "error": str(error),
                "traceback": traceback.format_exc(),
            },
        )
        raise


if __name__ == "__main__":
    main()
