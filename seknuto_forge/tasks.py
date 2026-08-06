"""Task manager: a persistent, sequential job queue for generate / refine / series runs.

One worker thread executes jobs in order (the local JSON store is not concurrent-safe),
so you can queue work operatively from the UI and watch each job's status live.
History persists to data/tasks.json; jobs interrupted by a restart are marked as such.
"""
from __future__ import annotations
import json, queue, threading, time, uuid
from typing import Any
from . import config, learn

TASKS_FILE = config.DATA_DIR / "tasks.json"
KINDS = ("generate", "refine", "series")

_TASKS: dict[str, dict[str, Any]] = {}
_Q: "queue.Queue[str]" = queue.Queue()
_lock = threading.Lock()
_started = False

# restore history; anything mid-flight when the server died is marked interrupted
if TASKS_FILE.exists():
    try:
        for _t in json.loads(TASKS_FILE.read_text(encoding="utf-8")):
            if _t.get("status") in ("queued", "running"):
                _t["status"], _t["error"] = "error", "interrupted by restart"
            _TASKS[_t["id"]] = _t
    except Exception:
        pass


def _persist() -> None:
    with _lock:
        TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        TASKS_FILE.write_text(json.dumps(list(_TASKS.values()), ensure_ascii=False, indent=2),
                              encoding="utf-8")


def _execute(kind: str, p: dict[str, Any]) -> dict[str, Any]:
    v = p.get("variables") or {}
    imgs = p.get("image_urls") or None
    if kind == "generate":
        r = learn.run_once(v, imgs, p.get("auto_evaluate", True), p.get("prompt_override"))
        return {"generation_id": r.get("_id"), "score": r.get("final_score"),
                "hard_fail": r.get("hard_fail", False),
                "output_url": r.get("output_url"), "local_path": r.get("local_path")}
    if kind == "refine":
        d = learn.refine(v, imgs)
        b = d.get("best") or {}
        return {"iterations": d["iterations"], "generation_id": b.get("_id"),
                "score": b.get("final_score"), "output_url": b.get("output_url"),
                "local_path": b.get("local_path"), "discovered": d.get("discovered")}
    # series
    d = learn.series(v, imgs, p.get("count", 3))
    return {"series_id": d["series_id"], "count": d["count"],
            "slides": [{k: s.get(k) for k in ("slide", "role", "score", "output_url", "id")}
                       for s in d["slides"]]}


def _worker() -> None:
    while True:
        tid = _Q.get()
        t = _TASKS.get(tid)
        if not t:
            continue
        t["status"], t["started"] = "running", time.time()
        _persist()
        try:
            t["result"] = _execute(t["kind"], t["payload"])
            t["status"] = "done"
        except Exception as e:
            t["status"], t["error"] = "error", str(e)[:500]
        t["finished"] = time.time()
        _persist()


def _ensure_worker() -> None:
    global _started
    if not _started:
        _started = True
        threading.Thread(target=_worker, daemon=True).start()


def create(kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    if kind not in KINDS:
        raise ValueError("kind must be one of: " + ", ".join(KINDS))
    _ensure_worker()
    t = {"id": uuid.uuid4().hex[:12], "kind": kind, "payload": payload,
         "status": "queued", "created": time.time(), "result": None, "error": None}
    _TASKS[t["id"]] = t
    _persist()
    _Q.put(t["id"])
    return t


def list_tasks() -> list[dict[str, Any]]:
    return sorted(_TASKS.values(), key=lambda t: t["created"], reverse=True)


def get(tid: str) -> dict[str, Any] | None:
    return _TASKS.get(tid)
