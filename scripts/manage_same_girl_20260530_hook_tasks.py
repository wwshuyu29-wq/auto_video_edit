#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GEN_SCRIPT = ROOT / "scripts/generate_same_girl_20260530_new_ai_hooks.py"
HHG_PATH = ROOT / "skills/tk-video-editor/modules/human_hook_generation/run.py"


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = import_module(GEN_SCRIPT, "same_girl_gen")
hhg = import_module(HHG_PATH, "human_hook_generation")


TARGET: Path = gen.TARGET
OUTPUT: Path = gen.OUTPUT
FINAL_16: Path = gen.FINAL_16
TARGET_DATE: str = gen.TARGET_DATE
PERSONAS = gen.PERSONAS


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def variant_dir(index: int, persona: dict[str, str]) -> Path:
    return OUTPUT / "generated_hooks_new_16" / f"new_same_girl_{index:02d}_{persona['name']}"


def task_id_from_create(create: dict[str, Any]) -> str:
    return str(create.get("id") or create.get("task_id") or "")


def build_card_payload(input_data: dict[str, Any], create: dict[str, Any], status: dict[str, Any] | None = None, video_path: Path | None = None) -> dict[str, Any]:
    reference_text = hhg.collect_reference_text(input_data)
    analysis, prompt, negative = hhg.build_prompt(input_data, reference_text)
    tid = task_id_from_create(create)
    card = {
        "status": "submitted",
        "detected": True,
        "analysis": analysis,
        "text_to_video_prompt": prompt,
        "negative_prompt": negative,
        "generation": {
            "provider": "evolink",
            "model": hhg.load_env_value("EVOLINK_VIDEO_MODEL") or hhg.DEFAULT_MODEL,
            "dry_run": False,
            "attempted": True,
            "status": "submitted",
            "task_id": tid,
        },
        "asset": None,
        "evidence_gaps": [],
    }
    if status is not None:
        card["generation"]["provider_status"] = status.get("status")
    if video_path is not None:
        card["status"] = "generated"
        card["generation"]["status"] = "completed"
        card["generation"]["video_path"] = str(video_path.resolve())
    return card


def ensure_task(index: int, persona: dict[str, str], api_key: str) -> dict[str, Any]:
    vdir = variant_dir(index, persona)
    input_path = vdir / "human_hook_input.json"
    create_path = vdir / "evolink_task_create.json"
    card_path = vdir / "human_hook_card.json"
    video_path = vdir / "ai_human_hook.mp4"

    if video_path.exists() and card_path.exists():
        card = read_json(card_path)
        if card.get("status") == "generated":
            return {"state": "complete", "index": index, "persona": persona, "video": video_path, "card": card_path}

    input_data = gen.build_input(index, persona)
    write_json(input_path, input_data)

    if not create_path.exists():
        reference_text = hhg.collect_reference_text(input_data)
        analysis, prompt, negative = hhg.build_prompt(input_data, reference_text)
        create = hhg.create_video_task(prompt, negative, int(analysis["duration_s"]), api_key)
        write_json(create_path, create)
        write_json(card_path, build_card_payload(input_data, create))
    else:
        create = read_json(create_path)
        if not card_path.exists() or read_json(card_path).get("status") != "generated":
            write_json(card_path, build_card_payload(input_data, create))

    tid = task_id_from_create(create)
    if not tid:
        raise RuntimeError(f"missing task id for new_same_girl_{index:02d}_{persona['name']}")
    return {"state": "pending", "index": index, "persona": persona, "task_id": tid, "video": video_path, "card": card_path, "input": input_path}


def poll_once(item: dict[str, Any], api_key: str) -> dict[str, Any]:
    template = hhg.load_env_value("EVOLINK_TASK_STATUS_ENDPOINT") or f"{hhg.evolink_base_url().rstrip('/')}/tasks/{{task_id}}"
    status_url = template.format(task_id=urllib.parse.quote(item["task_id"]))
    status = hhg.request_json("GET", status_url, api_key, None, timeout=60)
    status_path = variant_dir(item["index"], item["persona"]) / "evolink_task_status.json"
    write_json(status_path, status)
    provider_status = str(status.get("status", "")).lower()
    if provider_status not in {"completed", "succeeded", "success"}:
        if provider_status in {"failed", "cancelled", "canceled"}:
            item["state"] = "provider_failed"
        item["provider_status"] = provider_status
        return item

    result_url = hhg.generated_url(status)
    if not result_url:
        item["provider_status"] = "completed_missing_url"
        return item

    video_path = Path(item["video"])
    hhg.download_file(result_url, video_path, api_key)
    thumb = hhg.generate_thumbnail(video_path, video_path.with_suffix(".jpg"))
    input_data = read_json(Path(item["input"]))
    create = read_json(variant_dir(item["index"], item["persona"]) / "evolink_task_create.json")
    card = build_card_payload(input_data, create, status, video_path)
    card["thumbnail_path"] = thumb
    write_json(Path(item["card"]), card)
    item["state"] = "complete"
    item["provider_status"] = provider_status
    return item


def build_final_16(completed: list[dict[str, Any]]) -> None:
    if FINAL_16.exists():
        shutil.rmtree(FINAL_16)
    FINAL_16.mkdir(parents=True, exist_ok=True)
    items: list[dict[str, Any]] = []
    for item in sorted(completed, key=lambda payload: payload["index"]):
        src = Path(item["video"])
        dest = FINAL_16 / f"{item['index']:02d}_new_same_girl_{item['index']:02d}_{item['persona']['name']}.mp4"
        shutil.copy2(src, dest)
        items.append(
            {
                "index": item["index"],
                "variant_id": f"new_same_girl_{item['index']:02d}_{item['persona']['name']}",
                "source_video": str(src.resolve()),
                "final_video": str(dest.resolve()),
                "human_hook_card": str(Path(item["card"]).resolve()),
                "new_generation": True,
                "generation_date": TARGET_DATE,
            }
        )
    write_json(
        FINAL_16 / "same_girl_16_manifest.json",
        {
            "status": "ready",
            "label": f"{TARGET_DATE} newly generated same-girl AI human hooks",
            "requested_count": 16,
            "actual_count": len(items),
            "rule": f"All clips in this folder are newly generated for {TARGET_DATE} and are not copied from projects/generated/same-girl-clearfy-preview/output/final_16.",
            "items": items,
        },
    )


def main() -> None:
    api_key = hhg.load_env_value("EVOLINK_API_KEY") or hhg.load_env_value("AI_REAL_PERSON_VIDEO_API_KEY")
    if not api_key:
        raise RuntimeError("Missing EVOLINK_API_KEY or AI_REAL_PERSON_VIDEO_API_KEY in environment/.env.local")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    task_items = [ensure_task(index, persona, api_key) for index, persona in enumerate(PERSONAS, 1)]
    completed = [item for item in task_items if item["state"] == "complete"]
    pending = [item for item in task_items if item["state"] != "complete"]
    print(f"tasks ready: {len(completed)} complete, {len(pending)} pending", flush=True)

    deadline = time.time() + 1800
    while pending and time.time() < deadline:
        next_pending: list[dict[str, Any]] = []
        for item in pending:
            try:
                item = poll_once(item, api_key)
            except Exception as error:
                item["provider_status"] = f"poll_error: {str(error)[:160]}"
            if item.get("state") == "complete":
                print(f"downloaded new_same_girl_{item['index']:02d}_{item['persona']['name']}", flush=True)
                completed.append(item)
            else:
                next_pending.append(item)
        pending = next_pending
        write_json(
            TARGET / "hook_task_manager.partial.json",
            {
                "complete": len(completed),
                "pending": [
                    {
                        "index": item["index"],
                        "variant_id": f"new_same_girl_{item['index']:02d}_{item['persona']['name']}",
                        "task_id": item.get("task_id"),
                        "provider_status": item.get("provider_status"),
                    }
                    for item in pending
                ],
            },
        )
        print(f"progress: {len(completed)}/16 complete", flush=True)
        if pending:
            time.sleep(15)

    if pending:
        raise RuntimeError(f"timed out with pending hooks: {[item['index'] for item in pending]}")

    build_final_16(completed)
    write_json(
        TARGET / "hook_generation_manifest.json",
        {
            "status": "ready",
            "requested_count": 16,
            "generated_count": len(completed),
            "final_16": str(FINAL_16.resolve()),
            "items": [
                {
                    "index": item["index"],
                    "variant_id": f"new_same_girl_{item['index']:02d}_{item['persona']['name']}",
                    "video": str(Path(item["video"]).resolve()),
                    "human_hook_card": str(Path(item["card"]).resolve()),
                }
                for item in sorted(completed, key=lambda payload: payload["index"])
            ],
        },
    )
    print(f"done: {FINAL_16}", flush=True)


if __name__ == "__main__":
    main()
