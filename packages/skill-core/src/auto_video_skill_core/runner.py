from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Sequence

from .paths import tk_video_skill_dir


def run_module(module: str, args: Sequence[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run one existing tk-video-editor module by name.

    Example:
        run_module("viral_deconstruction", ["--input", "input.json", "--out", "output.json"])
    """
    module_path = tk_video_skill_dir() / "modules" / module / "run.py"
    if not module_path.exists():
        raise FileNotFoundError(f"Unknown tk-video-editor module: {module}")

    return subprocess.run(
        [sys.executable, str(module_path), *args],
        cwd=str(cwd or tk_video_skill_dir()),
        text=True,
        capture_output=True,
        check=False,
    )
