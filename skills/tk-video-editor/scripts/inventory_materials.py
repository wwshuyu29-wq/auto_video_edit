#!/usr/bin/env python3
"""Build a lightweight metadata index for a handheld footage directory."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}


def run_ffprobe(path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def parse_fps(rate: str | None) -> float | None:
    if not rate or rate == "0/0":
        return None
    if "/" in rate:
        num, den = rate.split("/", 1)
        den_f = float(den)
        return float(num) / den_f if den_f else None
    return float(rate)


def index_video(path: Path, root: Path) -> dict:
    probe = run_ffprobe(path)
    streams = probe.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    duration = (
        video_stream.get("duration")
        or probe.get("format", {}).get("duration")
        or 0
    )
    width = int(video_stream.get("width") or 0)
    height = int(video_stream.get("height") or 0)

    return {
        "id": path.stem,
        "path": str(path.resolve()),
        "relative_path": str(path.relative_to(root)),
        "is_symlink": path.is_symlink(),
        "symlink_target": str(path.resolve()) if path.is_symlink() else None,
        "duration_s": round(float(duration), 3),
        "width": width,
        "height": height,
        "orientation": "portrait" if height > width else "landscape" if width else "unknown",
        "fps": parse_fps(video_stream.get("avg_frame_rate")),
        "has_audio": audio_stream is not None,
        "codec": video_stream.get("codec_name"),
        "tags": {
            "scene": "",
            "subject": "",
            "action": "",
            "shot_type": "",
            "quality": "",
            "best_ranges": [],
            "matched_beats": [],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("footage_dir", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    root = args.footage_dir.resolve()
    if not root.exists():
        raise SystemExit(f"footage_dir not found: {root}")

    videos = sorted(p for p in root.rglob("*") if p.suffix.lower() in VIDEO_EXTS)
    items = []
    for video in videos:
        try:
            items.append(index_video(video, root))
        except subprocess.CalledProcessError as exc:
            items.append({
                "id": video.stem,
                "path": str(video.resolve()),
                "relative_path": str(video.relative_to(root)),
                "error": exc.stderr.strip() or str(exc),
            })

    payload = {
        "footage_dir": str(root),
        "count": len(items),
        "items": items,
    }
    out = args.out or (root / "material_index.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"indexed {len(items)} videos -> {out}")


if __name__ == "__main__":
    main()
