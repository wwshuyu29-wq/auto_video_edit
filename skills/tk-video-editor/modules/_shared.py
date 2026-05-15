#!/usr/bin/env python3
"""Shared helpers for TK video workflow modules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"input not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("input JSON must be an object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {path}")


def base_parser(description: str, default_out: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--input", "-i", type=Path, required=True)
    parser.add_argument("--out", "-o", type=Path, default=Path(default_out))
    return parser


def first_nonempty(*values: Any, default: str = "") -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def score_from_count(count: int, good: int = 3, cap: int = 10) -> int:
    if count <= 0:
        return 3
    return min(cap, 5 + min(count, good) * 2)
