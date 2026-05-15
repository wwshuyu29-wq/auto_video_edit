#!/usr/bin/env python3
"""Legacy adapter for older tk-video-editor inputs.

This adapter wraps loose or older inputs into the current orchestrator input
shape. It does not perform analysis.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def normalize(data: dict) -> dict:
    product = data.get("product") or data.get("product_profile") or {}
    video_list = data.get("video_list") or data.get("videos") or data.get("references") or []
    if isinstance(video_list, dict):
        video_list = [video_list]
    return {
        "account_url": data.get("account_url") or data.get("profile_url") or "",
        "video_list": video_list,
        "target_platform": data.get("target_platform") or data.get("platform") or "TikTok",
        "analysis_goal": data.get("analysis_goal") or "Extract reusable product-marketing video structures",
        "product": product,
        "platform": data.get("platform") or data.get("target_platform") or "TikTok",
        "video_length": data.get("video_length") or "25-35s",
        "tone": data.get("tone") or "native creator style, casual, not too salesy",
        "cta": data.get("cta") or product.get("cta", ""),
        "asset_library": data.get("asset_library") or data.get("assets") or [],
        "editing_style": data.get("editing_style") or {
            "pace": "fast",
            "average_clip_duration": "1.5-2.5s",
            "platform": data.get("platform") or "TikTok",
            "aspect_ratio": "9:16"
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", type=Path, required=True)
    parser.add_argument("--out", "-o", type=Path, default=Path("output/orchestrator_input.json"))
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(normalize(data), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
