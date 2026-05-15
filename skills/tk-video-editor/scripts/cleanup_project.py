#!/usr/bin/env python3
"""Clean regenerable local artifacts from a TK video project.

Default mode is dry-run. It reports what would be removed and writes a cleanup
report without deleting anything. Use --execute to delete candidates.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


PROTECTED_DIR_PARTS = {
    "materials/raw",
    "raw",
}

PROTECTED_FILENAMES = {
    "asset_library.json",
    "material_index.json",
    "viral_pattern_card.json",
    "product_script_card.json",
    "shot_matching_plan.json",
    "publishing_copy_card.json",
    "delivery_manifest.json",
    "final_delivery_manifest.json",
    "citely_preview_delivery_manifest.json",
}

TEMP_DIR_NAMES = {
    "__pycache__",
    "preview_render",
    "segments",
    "overlays",
    "qa_frames",
    "tmp",
    "temp",
}

TEMP_SUFFIXES = {
    ".pyc",
    ".tmp",
}


@dataclass
class Candidate:
    path: Path
    reason: str
    bytes: int
    is_dir: bool


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def path_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            total += item.stat().st_size
    return total


def protected(path: Path, root: Path) -> bool:
    relative = rel(path, root)
    parts = set(path.relative_to(root).parts)
    if "materials" in parts and "raw" in parts:
        return True
    if "raw" in parts and path.suffix.lower() in {".mov", ".mp4", ".gif", ".m4v"}:
        return True
    if path.name in PROTECTED_FILENAMES:
        return True
    if path.suffix.lower() in {".json", ".md"} and not any(part in TEMP_DIR_NAMES for part in parts):
        return True
    if relative.startswith("output/covers/") and path.suffix.lower() in {".jpg", ".jpeg", ".png"}:
        return True
    return False


def load_manifest_outputs(root: Path) -> set[Path]:
    keep: set[Path] = set()
    for manifest in root.rglob("*manifest*.json"):
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception:
            continue
        stack: list[object] = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, str):
                path = Path(item)
                if path.is_absolute() and path.exists():
                    keep.add(path.resolve())
    return keep


def latest_version_paths(root: Path) -> set[Path]:
    """Keep the highest _vN file for each preview base stem."""
    groups: dict[tuple[Path, str, str], tuple[int, Path]] = {}
    pattern = re.compile(r"^(?P<base>.+)_v(?P<version>\d+)(?P<tail>(?:_midpoint_sheet|_sheet)?)$")
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".mp4", ".jpg", ".jpeg", ".png", ".json"}:
            continue
        match = pattern.match(path.stem)
        if not match:
            continue
        key = (path.parent, match.group("base") + match.group("tail"), path.suffix.lower())
        version = int(match.group("version"))
        current = groups.get(key)
        if current is None or version > current[0]:
            groups[key] = (version, path.resolve())
    return {item[1] for item in groups.values()}


def collect_candidates(root: Path, mode: str) -> list[Candidate]:
    keep_from_manifest = load_manifest_outputs(root)
    latest_versions = latest_version_paths(root)
    candidates: list[Candidate] = []

    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path == root or not path.exists():
            continue
        if protected(path, root) or path.resolve() in keep_from_manifest:
            continue

        parts = set(path.relative_to(root).parts)
        if path.is_dir() and path.name in TEMP_DIR_NAMES:
            candidates.append(Candidate(path, f"temporary directory `{path.name}`", path_size(path), True))
            continue

        if path.is_file() and path.suffix.lower() in TEMP_SUFFIXES:
            candidates.append(Candidate(path, f"temporary file suffix `{path.suffix}`", path_size(path), False))
            continue

        if mode in {"normal", "aggressive"}:
            if path.is_file() and re.search(r"_v\d+", path.stem) and path.resolve() not in latest_versions:
                candidates.append(Candidate(path, "older versioned preview artifact", path_size(path), False))
                continue

        if mode == "aggressive":
            if path.is_dir() and path.name == "frames" and "references" in parts:
                candidates.append(Candidate(path, "reference extracted frames can be regenerated", path_size(path), True))
                continue
            if path.is_file() and path.name.endswith("_sheet.jpg") and path.resolve() not in latest_versions:
                candidates.append(Candidate(path, "non-latest contact sheet", path_size(path), False))
                continue

    # Avoid deleting children twice if a parent directory is already selected.
    selected: list[Candidate] = []
    selected_dirs: list[Path] = []
    for candidate in sorted(candidates, key=lambda c: len(c.path.parts)):
        if any(parent in candidate.path.parents for parent in selected_dirs):
            continue
        selected.append(candidate)
        if candidate.is_dir:
            selected_dirs.append(candidate.path)
    return selected


def human_size(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{value} B"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--mode", choices=["light", "normal", "aggressive"], default="normal")
    parser.add_argument("--execute", action="store_true", help="Actually delete candidates. Default is dry-run.")
    parser.add_argument("--report-out", type=Path, default=None)
    args = parser.parse_args()

    root = args.project_dir.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Project directory not found: {root}")

    candidates = collect_candidates(root, args.mode)
    total = sum(item.bytes for item in candidates)

    removed: list[str] = []
    if args.execute:
        for item in candidates:
            if item.is_dir:
                shutil.rmtree(item.path)
            else:
                item.path.unlink(missing_ok=True)
            removed.append(str(item.path))

    report = {
        "project_dir": str(root),
        "mode": args.mode,
        "dry_run": not args.execute,
        "candidate_count": len(candidates),
        "reclaimable_bytes": total,
        "reclaimable_human": human_size(total),
        "candidates": [
            {
                "path": str(item.path),
                "relative_path": rel(item.path, root),
                "reason": item.reason,
                "bytes": item.bytes,
                "size": human_size(item.bytes),
                "type": "directory" if item.is_dir else "file",
            }
            for item in candidates
        ],
        "removed": removed,
        "protected_policy": {
            "keeps_raw_materials": True,
            "keeps_structured_json_and_markdown": True,
            "keeps_cover_images": True,
            "keeps_manifest_outputs": True,
        },
    }

    report_out = args.report_out or root / "output" / "cleanup_report.json"
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    action = "Deleted" if args.execute else "Would delete"
    print(f"{action} {len(candidates)} items, reclaimable {human_size(total)}")
    print(f"Report: {report_out}")


if __name__ == "__main__":
    main()
