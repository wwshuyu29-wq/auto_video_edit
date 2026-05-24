#!/usr/bin/env python3
"""Extract the opening hook frames from a reference video and describe them.

This module only turns reference video evidence into structured observation.
It does not write product scripts, choose footage, or generate the AI human clip.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
import shutil
from pathlib import Path
from typing import Any

import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from _shared import load_json, write_json  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_WINDOW = [0.0, 5.0]
DEFAULT_OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"


def load_env_value(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if value:
        return value

    env_path = REPO_ROOT / ".env.local"
    if not env_path.exists():
        return ""

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        if key.strip() != name:
            continue
        candidate = raw_value.strip().strip('"').strip("'")
        if candidate.startswith("${") and candidate.endswith("}"):
            return load_env_value(candidate[2:-1])
        return candidate
    return ""


def vision_api_config() -> tuple[str, str, str, str]:
    openai_key = load_env_value("OPENAI_API_KEY")
    openai_endpoint = load_env_value("OPENAI_RESPONSES_ENDPOINT") or DEFAULT_OPENAI_RESPONSES_ENDPOINT
    if openai_key:
        return openai_key, openai_endpoint, "openai", "responses"

    evolink_key = load_env_value("EVOLINK_API_KEY") or load_env_value("AI_REAL_PERSON_VIDEO_API_KEY")
    evolink_endpoint = (
        load_env_value("EVOLINK_OPENAI_RESPONSES_ENDPOINT")
        or load_env_value("EVOLINK_RESPONSES_ENDPOINT")
        or ""
    )
    evolink_shape = "responses"
    if not evolink_endpoint:
        evolink_endpoint = (
            load_env_value("EVOLINK_OPENAI_CHAT_COMPLETIONS_ENDPOINT")
            or load_env_value("EVOLINK_CHAT_COMPLETIONS_ENDPOINT")
            or ""
        )
        evolink_shape = "chat_completions"
    if not evolink_endpoint:
        base_url = load_env_value("EVOLINK_OPENAI_BASE_URL")
        if base_url:
            evolink_endpoint = urllib.parse.urljoin(base_url.rstrip("/") + "/", "responses")
            evolink_shape = "responses"
    if evolink_key and evolink_endpoint:
        return evolink_key, evolink_endpoint, "evolink_openai_compatible", evolink_shape

    return "", "", "", ""


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return cleaned[:80] or "reference"


def resolve_path(value: str, project_dir: Path, input_dir: Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    project_candidate = project_dir / path
    if project_candidate.exists():
        return project_candidate
    return input_dir / path


def find_reference_video(data: dict[str, Any], project_dir: Path, input_dir: Path) -> tuple[Path | None, str]:
    candidates: list[str] = []
    for key in ["reference_video_path", "local_video", "video_path"]:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            candidates.append(value.strip())

    for video in data.get("video_list", []) or []:
        if not isinstance(video, dict):
            continue
        for key in ["reference_video_path", "local_video", "video_path", "downloaded_video"]:
            value = video.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(value.strip())

    for raw in candidates:
        path = resolve_path(raw, project_dir, input_dir)
        if path.exists():
            return path, raw

    reference_root = project_dir / "references"
    for pattern in ["**/reference.mp4", "**/reference.mov", "**/*.mp4", "**/*.mov"]:
        found = sorted(reference_root.glob(pattern))
        if found:
            return found[0], str(found[0])

    return None, ""


def collect_reference_urls(data: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for key in ["reference_video_url", "video_url", "tiktok_url"]:
        value = data.get(key)
        if isinstance(value, str) and value.strip().startswith(("http://", "https://")):
            urls.append(value.strip())

    for video in data.get("video_list", []) or []:
        if not isinstance(video, dict):
            continue
        value = video.get("video_url")
        if isinstance(value, str) and value.strip().startswith(("http://", "https://")):
            urls.append(value.strip())

    seen: set[str] = set()
    unique: list[str] = []
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        unique.append(url)
    return unique


def find_downloaded_video(download_dir: Path) -> Path | None:
    for pattern in ["*.mp4", "*.mov", "*.m4v", "*.webm"]:
        found = sorted(download_dir.glob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)
        if found:
            return found[0]
    return None


def download_reference_video(data: dict[str, Any], download_dir: Path) -> tuple[Path | None, str, str]:
    urls = collect_reference_urls(data)
    if not urls:
        return None, "", "No reference video URL was found in video_list/reference_video_url."

    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        return None, urls[0], "yt-dlp is not installed; upload a local reference video or install yt-dlp."

    download_dir.mkdir(parents=True, exist_ok=True)
    last_error = "unknown yt-dlp error"
    for url in urls:
        before = {path.resolve() for path in download_dir.glob("*") if path.is_file()}
        output_template = str(download_dir / "reference.%(ext)s")
        try:
            proc = subprocess.run(
                [
                    yt_dlp,
                    "--no-playlist",
                    "-f",
                    "mp4/bestvideo*+bestaudio/best",
                    "--merge-output-format",
                    "mp4",
                    "-o",
                    output_template,
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=240,
            )
        except subprocess.TimeoutExpired:
            last_error = "yt-dlp timed out while downloading the reference video."
            continue
        candidate = find_downloaded_video(download_dir)
        if proc.returncode == 0 and candidate:
            return candidate, url, ""

        after = {path.resolve() for path in download_dir.glob("*") if path.is_file()}
        for path in after - before:
            try:
                path.unlink()
            except OSError:
                pass
        error_text = (proc.stderr or proc.stdout or "unknown yt-dlp error").strip().splitlines()
        last_error = error_text[-1] if error_text else "unknown yt-dlp error"
    return None, urls[0], f"yt-dlp could not download the reference video: {last_error}"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def probe_video(video: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def extract_frames(video: Path, out_dir: Path, start: float, end: float, fps: float) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("frame_*.jpg"):
        old.unlink()
    duration = max(0.5, end - start)
    run([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{start:.3f}",
        "-t",
        f"{duration:.3f}",
        "-i",
        str(video),
        "-vf",
        f"fps={fps},scale=540:-1",
        str(out_dir / "frame_%02d.jpg"),
    ])
    return sorted(out_dir.glob("frame_*.jpg"))


def make_contact_sheet(video: Path, out_path: Path, start: float, end: float, fps: float) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    duration = max(0.5, end - start)
    run([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{start:.3f}",
        "-t",
        f"{duration:.3f}",
        "-i",
        str(video),
        "-vf",
        f"fps={fps},scale=270:-1,tile=5x2",
        "-frames:v",
        "1",
        str(out_path),
    ])


def text_blob(data: dict[str, Any]) -> str:
    chunks: list[str] = [
        str(data.get("account_url", "")),
        str(data.get("frames_summary", "")),
        str(data.get("caption", "")),
        str(data.get("transcript", "")),
    ]
    for video in data.get("video_list", []) or []:
        if not isinstance(video, dict):
            continue
        chunks.extend([
            str(video.get("video_url", "")),
            str(video.get("caption", "")),
            str(video.get("transcript", "")),
            str(video.get("frames_summary", "")),
        ])
    return "\n".join(chunk for chunk in chunks if chunk.strip()).lower()


def heuristic_observation(data: dict[str, Any], frame_index: dict[str, Any]) -> dict[str, Any]:
    blob = text_blob(data)
    detected = any(term in blob for term in [
        "human hook",
        "selfie",
        "creator face",
        "human face",
        "person on camera",
        "真人",
        "出镜",
        "soft.student.era",
    ])
    if not detected and any(term in blob for term in ["professor", "anxiety", "student", "laptop", "desk"]):
        detected = "soft.student.era" in blob

    observation = {
        "person": {
            "count": 1 if detected else 0,
            "framing": "unknown; review extracted hook frames" if not detected else "front-facing selfie or close-up creator shot",
            "identity_policy": "do not copy the reference person's face, identity, clothing, or exact likeness",
        },
        "action": "review hook frames manually" if not detected else "creator reacts to camera, then gestures toward laptop or screen",
        "expression": "unknown" if not detected else "anxious, surprised, confessional creator reaction",
        "environment": "unknown" if not detected else "student desk or dorm study setup with laptop",
        "camera": "vertical 9:16 reference video; review frames for exact camera motion",
        "text_overlay": {
            "visible": "unknown",
            "style": "review extracted frames",
            "summary": "use OCR/vision output when available",
        },
        "prompt_inputs": {
            "motion": "creator leans toward phone with small hand gesture" if detected else "",
            "scene": "student desk with laptop, warm indoor lighting" if detected else "",
            "emotion": "anxious, surprised, confessional" if detected else "",
        },
    }
    return {
        "status": "frames_extracted",
        "detected": detected,
        "frame_index": frame_index,
        "observation": observation,
        "evidence_gaps": [
            "Vision model was not used; observation is heuristic. Review extracted frames or set OPENAI_API_KEY, or configure an Evolink OpenAI-compatible responses endpoint."
        ],
    }


def data_url(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def parse_response_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return message["content"]
    texts: list[str] = []
    for item in payload.get("output", []) or []:
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []) or []:
            if isinstance(content, dict) and isinstance(content.get("text"), str):
                texts.append(content["text"])
    return "\n".join(texts)


def analyze_with_openai(frame_paths: list[Path], frame_index: dict[str, Any], model: str) -> dict[str, Any] | None:
    api_key, endpoint, provider, api_shape = vision_api_config()
    if not api_key or not endpoint:
        return None

    actual_model = model
    if provider == "evolink_openai_compatible":
        actual_model = load_env_value("EVOLINK_OPENAI_MODEL") or load_env_value("EVOLINK_VISION_MODEL") or model

    instruction = (
        "Analyze these first seconds of a TikTok reference video. Return only JSON. "
        "Detect whether this is a real-person/creator-on-camera hook. Describe person framing, action, expression, environment, camera motion, "
        "visible text overlay style, and prompt_inputs for text-to-video generation. Do not identify the person or copy likeness."
    )

    if api_shape == "chat_completions":
        chat_content: list[dict[str, Any]] = [{"type": "text", "text": instruction}]
        for path in frame_paths[:8]:
            chat_content.append({"type": "image_url", "image_url": {"url": data_url(path), "detail": "low"}})
        payload = {
            "model": actual_model,
            "messages": [{"role": "user", "content": chat_content}],
            "temperature": 0.1,
            "stream": False,
        }
    else:
        content: list[dict[str, Any]] = [
            {
                "type": "input_text",
                "text": instruction,
            }
        ]
        for path in frame_paths[:8]:
            content.append({"type": "input_image", "image_url": data_url(path), "detail": "low"})
        payload = {
            "model": actual_model,
            "input": [{"role": "user", "content": content}],
        }

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
    )
    request.add_header("Authorization", f"Bearer {api_key}")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")
    with urllib.request.urlopen(request, timeout=90) as response:
        response_payload = json.loads(response.read().decode("utf-8"))

    text = parse_response_text(response_payload).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    parsed = json.loads(text)
    return {
        "status": "vision_analyzed",
        "detected": bool(parsed.get("detected")),
        "frame_index": frame_index,
        "observation": parsed,
        "vision_provider": {
            "provider": provider,
            "model": actual_model,
            "api_shape": api_shape,
            "endpoint_host": urllib.parse.urlparse(endpoint).netloc,
            "response_id": response_payload.get("id"),
        },
        "evidence_gaps": parsed.get("evidence_gaps", []),
    }


def sync_full_workflow(full_path: Path, observation_path: Path, frame_index_path: Path, observation: dict[str, Any]) -> None:
    if not full_path.exists():
        return
    full = load_json(full_path)
    full["human_hook_observation"] = observation
    full["human_hook_observation_path"] = str(observation_path)
    full["hook_frame_index_path"] = str(frame_index_path)
    if full.get("video_list") and isinstance(full["video_list"], list) and isinstance(full["video_list"][0], dict):
        full["video_list"][0]["hook_frame_index_path"] = str(frame_index_path)
        full["video_list"][0]["human_hook_observation_path"] = str(observation_path)
    write_json(full_path, full)


def build(args: argparse.Namespace) -> dict[str, Any]:
    data = load_json(args.input)
    project_dir = args.project_dir.resolve()
    input_dir = args.input.resolve().parent
    reference_video, raw_reference = find_reference_video(data, project_dir, input_dir)
    start, end = [float(x) for x in (args.hook_window or DEFAULT_WINDOW)]
    download_gap = ""

    if reference_video is None and args.download_reference and not args.dry_run:
        download_root = args.reference_dir or project_dir / "references" / "auto_hook"
        reference_video, raw_reference, download_gap = download_reference_video(data, download_root)

    if reference_video is None:
        empty_index = {
            "reference_video": None,
            "hook_window_s": [start, end],
            "frames": [],
            "contact_sheet": None,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        if args.frame_index_out:
            write_json(args.frame_index_out, empty_index)
        return {
            "status": "no_reference_video",
            "detected": False,
            "reference_video": None,
            "hook_window_s": [start, end],
            "frame_index": empty_index,
            "observation": {
                "person": {"count": 0, "framing": "no reference video available"},
                "prompt_inputs": {},
            },
            "evidence_gaps": [
                download_gap
                or "No local reference video was found. Upload a reference video/recording or set reference_video_path/local_video in the workflow input."
            ],
        }

    ref_id = slug(reference_video.stem)
    reference_dir = args.reference_dir or project_dir / "references" / ref_id
    frames_dir = reference_dir / "hook_frames"
    contact_sheet = reference_dir / "hook_contact_sheet.jpg"
    frames = extract_frames(reference_video, frames_dir, start, end, args.fps)
    make_contact_sheet(reference_video, contact_sheet, start, end, args.fps)
    metadata = probe_video(reference_video)
    frame_index = {
        "reference_video": str(reference_video),
        "raw_reference": raw_reference,
        "hook_window_s": [start, end],
        "fps": args.fps,
        "frames_dir": str(frames_dir),
        "frames": [str(path) for path in frames],
        "contact_sheet": str(contact_sheet),
        "metadata": metadata,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if args.frame_index_out:
        write_json(args.frame_index_out, frame_index)

    result = heuristic_observation(data, frame_index)
    result["reference_video"] = str(reference_video)
    result["hook_window_s"] = [start, end]

    if args.vision and not args.dry_run:
        try:
            vision = analyze_with_openai(frames, frame_index, args.openai_model)
            if vision:
                result = {
                    **vision,
                    "reference_video": str(reference_video),
                    "hook_window_s": [start, end],
                }
        except Exception as error:
            result["evidence_gaps"].append(f"Vision analysis failed; heuristic observation retained: {error}")

    if args.full_workflow_input and not args.dry_run:
        sync_full_workflow(args.full_workflow_input, args.out, args.frame_index_out, result)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", type=Path, required=True)
    parser.add_argument("--out", "-o", type=Path, required=True)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--full-workflow-input", type=Path, default=None)
    parser.add_argument("--frame-index-out", type=Path, default=None)
    parser.add_argument("--reference-dir", type=Path, default=None)
    parser.add_argument("--hook-window", type=float, nargs=2, default=DEFAULT_WINDOW)
    parser.add_argument("--fps", type=float, default=2.0)
    parser.add_argument("--vision", action="store_true", help="Use OpenAI vision if OPENAI_API_KEY or an Evolink OpenAI-compatible responses endpoint is configured.")
    parser.add_argument("--download-reference", action="store_true", help="Try yt-dlp download from video_url when no local reference video exists.")
    parser.add_argument("--openai-model", default=os.environ.get("OPENAI_VISION_MODEL", "gpt-4.1-mini"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.frame_index_out is None:
        args.frame_index_out = args.out.parent / "hook_frame_index.json"
    write_json(args.out, build(args))


if __name__ == "__main__":
    main()
