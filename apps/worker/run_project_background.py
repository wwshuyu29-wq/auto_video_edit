#!/usr/bin/env python3
"""Run one project job in the background and persist a simple status file.

This is the thinnest bridge between the web app and the existing worker CLI.
The web layer spawns this script in detached mode. This script then runs the
real worker and records idle/running/completed/failed state for the UI.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKER_CLI = REPO_ROOT / "apps" / "worker" / "worker_cli.py"


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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-file", required=True, type=Path)
    args = parser.parse_args()

    job_file = args.job_file.resolve()
    project_dir, status_path, log_path = build_paths(job_file)

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
    }
    write_json(status_path, running_state)

    try:
        with log_path.open("a", encoding="utf-8") as log_handle:
            log_handle.write(f"\n[{utc_now()}] starting worker run\n")
            log_handle.write(f"job_file={job_file}\n")
            log_handle.flush()

            command = [sys.executable, str(WORKER_CLI), "run-project", "--job-file", str(job_file)]
            process = subprocess.run(
                command,
                cwd=project_dir,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )

            state = "completed" if process.returncode == 0 else "failed"
            write_json(
                status_path,
                {
                    **running_state,
                    "state": state,
                    "finished_at": utc_now(),
                    "return_code": process.returncode,
                    "error": None if process.returncode == 0 else f"Worker exited with code {process.returncode}",
                },
            )
            log_handle.write(f"[{utc_now()}] finished worker run with code={process.returncode}\n")
    except Exception as error:  # pragma: no cover - defensive bridge
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

