#!/usr/bin/env python3
"""Analyze a reference human hook and optionally generate an AI human intro clip.

The module only handles the opening human hook. It writes a human_hook_card and,
when a real clip is generated, appends that clip to the project asset library so
asset_matching can use it like any other footage.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from _shared import load_json, write_json  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_MODEL = "seedance-2.0-text-to-video"
DEFAULT_BASE_URL = "https://api.evolink.ai/v1"


def first_nonempty(*values: Any, default: str = "") -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


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


def evolink_base_url() -> str:
    return load_env_value("EVOLINK_BASE_URL") or load_env_value("EVOLINK_API_BASE_URL") or DEFAULT_BASE_URL


def collect_reference_text(data: dict[str, Any]) -> str:
    viral = data.get("viral_pattern_card") if isinstance(data.get("viral_pattern_card"), dict) else data
    observation = data.get("human_hook_observation") if isinstance(data.get("human_hook_observation"), dict) else {}
    chunks: list[str] = [
        str(data.get("account_url", "")),
        str(data.get("reference_hook_summary", "")),
        str(data.get("frames_summary", "")),
        json.dumps(observation, ensure_ascii=False),
        str(viral.get("template_id", "")),
        str(viral.get("main_content_logic", "")),
    ]

    caption_logic = viral.get("caption_logic") if isinstance(viral.get("caption_logic"), dict) else {}
    chunks.append(" ".join(str(item) for item in caption_logic.get("visible_sequence", []) if item))
    chunks.append(" ".join(str(item) for item in caption_logic.get("sentence_roles", []) if item))

    for pattern in viral.get("viral_patterns", []) or []:
        if not isinstance(pattern, dict):
            continue
        chunks.extend([
            str(pattern.get("opening_0_3s", "")),
            str(pattern.get("hook_type", "")),
            json.dumps(pattern.get("visual_style", {}), ensure_ascii=False),
        ])

    for video in data.get("video_list", []) or []:
        if not isinstance(video, dict):
            continue
        chunks.extend([
            str(video.get("caption", "")),
            str(video.get("transcript", "")),
            str(video.get("frames_summary", "")),
            str(video.get("video_url", "")),
        ])

    return "\n".join(chunk for chunk in chunks if chunk.strip())


def detect_human_hook(data: dict[str, Any], reference_text: str) -> tuple[bool, list[str]]:
    observation = data.get("human_hook_observation")
    if isinstance(observation, dict):
        if observation.get("detected") is True:
            return True, []
        if observation.get("detected") is False and observation.get("status") == "vision_analyzed":
            return False, ["Vision analysis did not detect a real-person opening hook."]

    explicit = data.get("human_hook")
    if isinstance(explicit, dict) and explicit.get("enabled") is True:
        return True, []

    lowered = reference_text.lower()
    human_terms = [
        "human hook",
        "human face",
        "creator face",
        "selfie",
        "student selfie",
        "face occupies",
        "real person",
        "person on camera",
        "creator looks",
        "真人",
        "人脸",
        "出镜",
    ]
    template_terms = [
        "soft_student_era_human_hook",
        "face-fear-tool-proof",
        "confession-to-proof",
    ]
    detected = any(term in lowered for term in human_terms + template_terms)
    gaps: list[str] = []
    if not detected:
        gaps.append("No clear human-on-camera opening signal was found in reference metadata or frame summaries.")
    if "frames_summary" not in lowered and "contact_sheet" not in lowered and "local_video" not in lowered:
        gaps.append("No frame summary/contact sheet/local reference video was supplied; prompt uses template-level visual inference.")
    return detected, gaps


def infer_scene(reference_text: str) -> str:
    lowered = reference_text.lower()
    if any(term in lowered for term in ["bedroom", "dorm", "student room", "study room", "desk", "laptop"]):
        return "student desk with a laptop, warm bedroom or dorm study lighting"
    if any(term in lowered for term in ["office", "workspace"]):
        return "small creator workspace with laptop and desk items"
    if any(term in lowered for term in ["lab", "research"]):
        return "research desk or lab-adjacent study workspace with laptop"
    return "casual study desk with laptop, notebook, and warm indoor lighting"


def infer_emotion(reference_text: str) -> str:
    lowered = reference_text.lower()
    if any(term in lowered for term in ["fear", "anxiety", "warning", "professor", "submission", "authority"]):
        return "anxious, surprised, and slightly confessional"
    if any(term in lowered for term in ["disbelief", "wasted", "manual", "random tabs"]):
        return "frustrated disbelief turning into discovery"
    if any(term in lowered for term in ["relief", "boom", "result"]):
        return "surprised relief after finding a shortcut"
    return "curious, urgent, and creator-native"


def infer_action(reference_text: str) -> str:
    lowered = reference_text.lower()
    if any(term in lowered for term in ["pointing", "finger", "points"]):
        return "leans toward the phone, raises eyebrows, then points toward the laptop beside them"
    if any(term in lowered for term in ["laptop", "screen"]):
        return "glances from the phone to the laptop, reacts, then gestures toward the screen"
    return "leans close to the selfie camera with a quick surprised reaction and small hand gesture"


def product_name(data: dict[str, Any]) -> str:
    product = data.get("product") if isinstance(data.get("product"), dict) else {}
    return first_nonempty(product.get("product_name"), data.get("product_name"), default="the product")


def build_prompt(data: dict[str, Any], reference_text: str) -> tuple[dict[str, Any], str, str]:
    observation = data.get("human_hook_observation") if isinstance(data.get("human_hook_observation"), dict) else {}
    observed = observation.get("observation") if isinstance(observation.get("observation"), dict) else {}
    prompt_inputs = observed.get("prompt_inputs") if isinstance(observed.get("prompt_inputs"), dict) else {}
    scene = first_nonempty(prompt_inputs.get("scene"), observed.get("environment"), default=infer_scene(reference_text))
    emotion = first_nonempty(prompt_inputs.get("emotion"), observed.get("expression"), default=infer_emotion(reference_text))
    action = first_nonempty(prompt_inputs.get("motion"), observed.get("action"), default=infer_action(reference_text))
    camera = first_nonempty(observed.get("camera"), default="front-facing phone camera, subtle handheld movement, native TikTok feel")
    framing = "vertical 9:16 smartphone selfie, close-up to medium close-up"
    person = observed.get("person") if isinstance(observed.get("person"), dict) else {}
    if isinstance(person.get("framing"), str) and person["framing"].strip():
        framing = person["framing"].strip()
    product = product_name(data)
    duration = int(data.get("human_hook_duration_s") or 4)

    analysis = {
        "duration_s": duration,
        "character": "young adult student/creator, original fictional person, not the reference creator",
        "framing": framing,
        "action": action,
        "emotion": emotion,
        "environment": scene,
        "camera": camera,
        "overlay_policy": "generate clean video without baked-in text; renderer will add captions later",
        "identity_policy": "do not copy the reference person's face, identity, clothing, or exact likeness",
    }

    prompt = (
        f"Realistic vertical 9:16 smartphone selfie video, {duration} seconds. "
        f"An original young adult student creator sits at a {scene}. "
        f"The creator looks {emotion}, {action}. "
        f"Natural handheld phone motion, warm indoor lighting, authentic TikTok studytok style, "
        f"close-up face first, laptop visible but not brand-specific, no logos, no readable text, "
        f"no subtitles baked into the video. The moment should feel like a peer sharing a useful {product} workflow."
    )
    negative = (
        "Do not imitate or recreate the reference creator's face or identity. "
        "No watermark, no logo, no readable on-screen text, no distorted hands, no extra limbs, no uncanny face, no product UI."
    )
    return analysis, prompt, negative


def request_json(method: str, url: str, api_key: str, payload: dict[str, Any] | None = None, timeout: int = 60) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {api_key}")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def create_video_task(prompt: str, negative_prompt: str, duration: int, api_key: str) -> dict[str, Any]:
    base_url = evolink_base_url()
    endpoint = load_env_value("EVOLINK_VIDEO_GENERATE_ENDPOINT") or f"{base_url.rstrip('/')}/videos/generations"
    payload = {
        "model": load_env_value("EVOLINK_VIDEO_MODEL") or DEFAULT_MODEL,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "duration": duration,
        "aspect_ratio": "9:16",
    }
    return request_json("POST", endpoint, api_key, payload)


def poll_task(task_id: str, api_key: str, timeout_s: int, interval_s: int) -> dict[str, Any]:
    base_url = evolink_base_url()
    template = load_env_value("EVOLINK_TASK_STATUS_ENDPOINT") or f"{base_url.rstrip('/')}/tasks/{{task_id}}"
    deadline = time.time() + timeout_s
    last: dict[str, Any] = {}
    while time.time() < deadline:
        status_url = template.format(task_id=urllib.parse.quote(task_id))
        last = request_json("GET", status_url, api_key, None)
        status = str(last.get("status", "")).lower()
        if status in {"completed", "succeeded", "success", "failed", "cancelled", "canceled"}:
            return last
        time.sleep(interval_s)
    last["status"] = last.get("status") or "timeout"
    return last


def download_file(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=180) as response:
        out_path.write_bytes(response.read())


def probe_video(path: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def generate_thumbnail(video_path: Path, thumbnail_path: Path) -> str | None:
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-ss",
                "1",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-vf",
                "scale=360:-1",
                str(thumbnail_path),
            ],
            check=True,
        )
        return str(thumbnail_path)
    except Exception:
        return None


def make_asset(project_dir: Path, video_path: Path, analysis: dict[str, Any]) -> dict[str, Any]:
    metadata = probe_video(video_path)
    streams = metadata.get("streams") or []
    video_stream = next((item for item in streams if item.get("codec_type") == "video"), {})
    audio_stream = next((item for item in streams if item.get("codec_type") == "audio"), None)
    duration = float(video_stream.get("duration") or metadata.get("format", {}).get("duration") or analysis.get("duration_s") or 4)
    width = int(video_stream.get("width") or 0)
    height = int(video_stream.get("height") or 0)
    thumbnail = generate_thumbnail(video_path, project_dir / "materials" / "contact_sheets" / "ai_human_hook.jpg")
    return {
        "clip_id": "ai_human_hook",
        "file_path": str(video_path.resolve()),
        "thumbnail_path": thumbnail,
        "duration": round(duration, 3),
        "orientation": "vertical_ai_selfie_intro" if height >= width else "ai_selfie_intro",
        "quality_score": 8,
        "shot_type": "AI generated human selfie hook",
        "camera_motion": "subtle handheld selfie movement",
        "scene": analysis.get("environment", "student desk"),
        "visible_objects": ["student creator", "laptop", "study desk"],
        "emotion": analysis.get("emotion", "surprised creator hook"),
        "best_use": ["human hook", "opening hook", "creator reaction", "student anxiety setup"],
        "not_good_for": ["product proof", "final result proof"],
        "usable_segments": [
            {
                "start": 0,
                "end": min(round(duration, 3), float(analysis.get("duration_s") or 4)),
                "reason": "AI-generated opening human hook based on reference hook analysis.",
            }
        ],
        "text_overlay_safe_area": "lower center; keep face readable",
        "audio_quality": "not needed" if not audio_stream else "present but not required",
        "notes": "Generated from human_hook_generation; use only as the opening hook.",
    }


def upsert_asset(library_path: Path, asset: dict[str, Any]) -> None:
    library_path.parent.mkdir(parents=True, exist_ok=True)
    if library_path.exists():
        library = load_json(library_path)
    else:
        library = {"assets": []}
    if isinstance(library, list):
        assets = library
        wrapper: dict[str, Any] | None = None
    elif isinstance(library, dict):
        assets = library.get("assets")
        if not isinstance(assets, list):
            assets = []
        wrapper = library
    else:
        assets = []
        wrapper = {"assets": assets}

    assets = [item for item in assets if isinstance(item, dict) and item.get("clip_id") != asset.get("clip_id")]
    assets.insert(0, asset)
    if wrapper is None:
        write_json(library_path, assets)
        return

    wrapper["assets"] = assets
    wrapper["status"] = "indexed"
    wrapper["asset_count"] = len(assets)
    wrapper["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    wrapper["note"] = "Includes AI-generated human hook clip when available."
    write_json(library_path, wrapper)


def sync_full_workflow(full_path: Path, asset: dict[str, Any]) -> None:
    if not full_path.exists():
        return
    full = load_json(full_path)
    assets = full.get("asset_library")
    if not isinstance(assets, list):
        assets = []
    assets = [item for item in assets if isinstance(item, dict) and item.get("clip_id") != asset.get("clip_id")]
    assets.insert(0, asset)
    full["asset_library"] = assets
    full["generated_human_hook_asset"] = asset
    write_json(full_path, full)


def generated_url(status: dict[str, Any]) -> str:
    results = status.get("results")
    if isinstance(results, list) and results:
        return str(results[0])
    output = status.get("output")
    if isinstance(output, dict):
        for key in ["url", "video_url"]:
            if output.get(key):
                return str(output[key])
    for key in ["url", "video_url"]:
        if status.get(key):
            return str(status[key])
    return ""


def build_card(args: argparse.Namespace) -> dict[str, Any]:
    data = load_json(args.input)
    reference_text = collect_reference_text(data)
    detected, evidence_gaps = detect_human_hook(data, reference_text)
    analysis, prompt, negative_prompt = build_prompt(data, reference_text)

    card: dict[str, Any] = {
        "status": "skipped" if not detected else "prompt_ready",
        "detected": detected,
        "analysis": analysis,
        "text_to_video_prompt": prompt if detected else "",
        "negative_prompt": negative_prompt if detected else "",
        "generation": {
            "provider": "evolink",
            "model": load_env_value("EVOLINK_VIDEO_MODEL") or DEFAULT_MODEL,
            "dry_run": bool(args.dry_run),
            "attempted": False,
        },
        "asset": None,
        "evidence_gaps": evidence_gaps,
    }

    if not detected:
        return card

    api_key = load_env_value("EVOLINK_API_KEY") or load_env_value("AI_REAL_PERSON_VIDEO_API_KEY")
    if args.dry_run:
        card["generation"]["status"] = "dry_run_prompt_only"
        return card
    if not api_key:
        card["generation"]["status"] = "missing_api_key"
        card["generation"]["message"] = "Set EVOLINK_API_KEY or AI_REAL_PERSON_VIDEO_API_KEY in .env.local to generate the human hook video."
        return card

    generated_dir = Path(args.generated_dir or args.out.parent / "generated_hooks")
    video_out = Path(args.video_out or generated_dir / "ai_human_hook.mp4")
    task_create_path = generated_dir / "evolink_task_create.json"
    task_status_path = generated_dir / "evolink_task_status.json"

    try:
        card["generation"]["attempted"] = True
        create_response = create_video_task(prompt, negative_prompt, int(analysis["duration_s"]), api_key)
        write_json(task_create_path, create_response)
        task_id = str(create_response.get("id") or create_response.get("task_id") or "")
        if not task_id:
            raise RuntimeError("Video provider did not return a task id.")
        status = poll_task(task_id, api_key, args.poll_timeout, args.poll_interval)
        write_json(task_status_path, status)
        result_url = generated_url(status)
        if str(status.get("status", "")).lower() not in {"completed", "succeeded", "success"} or not result_url:
            raise RuntimeError(f"Video task did not complete successfully: {status.get('status', 'unknown')}")
        download_file(result_url, video_out)
        asset = make_asset(Path(args.project_dir).resolve(), video_out, analysis)
        if args.asset_library:
            upsert_asset(Path(args.asset_library), asset)
        if args.full_workflow_input:
            sync_full_workflow(Path(args.full_workflow_input), asset)
        card["status"] = "generated"
        card["generation"].update({
            "status": "completed",
            "task_id": task_id,
            "task_create_path": str(task_create_path),
            "task_status_path": str(task_status_path),
            "video_path": str(video_out),
        })
        card["asset"] = asset
    except (RuntimeError, urllib.error.URLError, subprocess.CalledProcessError, OSError) as error:
        card["status"] = "failed"
        card["generation"]["status"] = "failed"
        card["generation"]["message"] = str(error)

    return card


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", type=Path, required=True)
    parser.add_argument("--out", "-o", type=Path, required=True)
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--asset-library", type=Path, default=None)
    parser.add_argument("--full-workflow-input", type=Path, default=None)
    parser.add_argument("--generated-dir", type=Path, default=None)
    parser.add_argument("--video-out", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--poll-timeout", type=int, default=420)
    parser.add_argument("--poll-interval", type=int, default=6)
    args = parser.parse_args()
    write_json(args.out, build_card(args))


if __name__ == "__main__":
    main()
