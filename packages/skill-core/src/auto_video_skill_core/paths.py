from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return the repository root from inside the package layout."""
    return Path(__file__).resolve().parents[4]


def tk_video_skill_dir() -> Path:
    """Return the current local skill implementation path."""
    return repo_root() / "skills" / "tk-video-editor"
