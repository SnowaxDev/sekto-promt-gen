"""Build blocks: reusable saved recipes — a named form (variables + kind + inputs) you
re-run in one click or push into the task queue. This is the safe 'automation script'
primitive: a block can only drive the existing brand-locked pipeline, never arbitrary code.
Stored in data/blocks.json (user-local, gitignored).
"""
from __future__ import annotations
import json, time, uuid
from typing import Any
from . import config, tasks

BLOCKS_FILE = config.DATA_DIR / "blocks.json"


def _load() -> list[dict[str, Any]]:
    if not BLOCKS_FILE.exists():
        return []
    try:
        return json.loads(BLOCKS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save(bs: list[dict[str, Any]]) -> None:
    BLOCKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    BLOCKS_FILE.write_text(json.dumps(bs, ensure_ascii=False, indent=2), encoding="utf-8")


def list_blocks() -> list[dict[str, Any]]:
    return _load()


def add(name: str, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    if kind not in tasks.KINDS:
        raise ValueError("kind must be one of: " + ", ".join(tasks.KINDS))
    bs = _load()
    b = {"id": uuid.uuid4().hex[:10], "name": (name or "blok").strip()[:60],
         "kind": kind, "payload": payload, "created": time.time()}
    bs.append(b)
    _save(bs)
    return b


def delete(bid: str) -> bool:
    bs = _load()
    left = [b for b in bs if b["id"] != bid]
    if len(left) == len(bs):
        return False
    _save(left)
    return True


def run(bid: str) -> dict[str, Any] | None:
    b = next((x for x in _load() if x["id"] == bid), None)
    return tasks.create(b["kind"], b["payload"]) if b else None
