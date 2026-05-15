#!/usr/bin/env python3
"""Add a local TTS voiceover and low-volume placeholder BGM to a rendered video.

This is for workflow proofing, not final brand audio. It uses macOS `say` for
replaceable narration and FFmpeg-generated low-volume audio bed as a placeholder.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=capture)


def load_segments(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    segments = data.get("segments", data)
    if not isinstance(segments, list):
        raise SystemExit(f"captions file must contain a segments list: {path}")
    return segments


def probe_duration(path: Path) -> float:
    proc = run([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ], capture=True)
    return float(proc.stdout.strip())


def atempo_chain(factor: float) -> str:
    parts: list[str] = []
    factor = max(0.5, factor)
    while factor > 2.0:
        parts.append("atempo=2.0")
        factor /= 2.0
    parts.append(f"atempo={factor:.4f}")
    return ",".join(parts)


def synthesize_line(text: str, voice: str, rate: int, out_path: Path) -> None:
    cmd = ["say", "-r", str(rate), "-o", str(out_path), text]
    if voice:
        cmd[1:1] = ["-v", voice]
    try:
        run(cmd)
    except subprocess.CalledProcessError:
        fallback = ["say", "-r", str(rate), "-o", str(out_path), text]
        run(fallback)


def build_voice_track(segments: list[dict], workdir: Path, voice: str, rate: int) -> Path:
    raw_dir = workdir / "voice_raw"
    seg_dir = workdir / "voice_segments"
    shutil.rmtree(raw_dir, ignore_errors=True)
    shutil.rmtree(seg_dir, ignore_errors=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    seg_dir.mkdir(parents=True, exist_ok=True)

    rendered: list[Path] = []
    for idx, seg in enumerate(segments):
        text = str(seg.get("text") or "").strip()
        duration = max(0.35, float(seg["end"]) - float(seg["start"]))
        raw = raw_dir / f"line_{idx:02d}.aiff"
        wav = seg_dir / f"voice_{idx:02d}.wav"
        synthesize_line(text, voice, rate, raw)
        raw_dur = probe_duration(raw)

        filters = []
        if raw_dur > duration * 0.88:
            filters.append(atempo_chain(raw_dur / (duration * 0.88)))
        filters.extend([
            "volume=1.15",
            "apad",
            f"atrim=duration={duration:.3f}",
            "asetpts=PTS-STARTPTS",
        ])
        run([
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(raw),
            "-af",
            ",".join(filters),
            "-ar",
            "48000",
            "-ac",
            "1",
            str(wav),
        ])
        rendered.append(wav)

    concat = workdir / "voice_concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in rendered), encoding="utf-8")
    voice_track = workdir / "voice_track.wav"
    run([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat),
        "-c",
        "copy",
        str(voice_track),
    ])
    return voice_track


def build_bgm(duration: float, workdir: Path) -> Path:
    out = workdir / "placeholder_bgm.wav"
    # Low-volume tonal bed plus pink noise. This is only a timing placeholder.
    expr = (
        "0.020*sin(2*PI*92*t)"
        "+0.014*sin(2*PI*184*t)"
        "+0.010*sin(2*PI*276*t)"
    )
    run([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        f"aevalsrc='{expr}':s=48000:d={duration:.3f}",
        "-f",
        "lavfi",
        "-i",
        f"anoisesrc=color=pink:duration={duration:.3f}:sample_rate=48000",
        "-filter_complex",
        "[1:a]volume=0.010[n];[0:a][n]amix=inputs=2:duration=first,afade=t=in:st=0:d=0.4,afade=t=out:st="
        f"{max(0, duration - 0.8):.3f}:d=0.8[a]",
        "-map",
        "[a]",
        "-ar",
        "48000",
        "-ac",
        "2",
        str(out),
    ])
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--captions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, default=None)
    parser.add_argument("--voice", default="Samantha")
    parser.add_argument("--rate", type=int, default=235)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    workdir = args.workdir or args.out.parent / f"{args.out.stem}_audio_work"
    workdir.mkdir(parents=True, exist_ok=True)

    segments = load_segments(args.captions)
    duration = probe_duration(args.video)
    voice_track = build_voice_track(segments, workdir, args.voice, args.rate)
    bgm = build_bgm(duration, workdir)

    run([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(args.video),
        "-i",
        str(voice_track),
        "-i",
        str(bgm),
        "-filter_complex",
        "[1:a]volume=1.0[v];[2:a]volume=0.45[b];[v][b]amix=inputs=2:duration=first,"
        "loudnorm=I=-14:TP=-1:LRA=11[a]",
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(args.out),
    ])

    report = {
        "status": "audio_workmix_rendered",
        "video": str(args.video),
        "captions": str(args.captions),
        "voice": args.voice,
        "rate": args.rate,
        "bgm": str(bgm),
        "voice_track": str(voice_track),
        "output": str(args.out),
        "duration": duration,
        "notes": [
            "Voiceover uses local macOS TTS and should be replaced with creator voice or ElevenLabs before final publication if needed.",
            "BGM is a generated low-volume placeholder bed for timing only.",
        ],
    }
    (args.out.with_suffix(".audio_report.json")).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
