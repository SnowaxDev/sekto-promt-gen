"""Local asset library. Every generation is saved to outputs/<date>/ on the user's PC —
the image itself plus a JSON sidecar (prompt, scores, defects, series info) — so nothing
lives only on expiring Replicate URLs and the archive doubles as a learning dataset.
"""
from __future__ import annotations
import base64, json, time, urllib.request
from pathlib import Path
from typing import Any
from . import config

_SIDE_KEYS = ("_id", "ts", "format", "mode", "prompt", "chosen_variant_ids",
              "auto_score", "auto_checks", "auto_defects", "human_score", "final_score",
              "hard_fail", "series_id", "slide_index", "series_role", "model", "output_url")


def _day_dir(ts: float | None) -> Path:
    d = config.OUTPUTS_DIR / time.strftime("%Y-%m-%d", time.localtime(ts or time.time()))
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_generation(rec: dict[str, Any]) -> str | None:
    """Download the generated image next to a JSON sidecar. Non-fatal: any error just
    means no local copy this time — the pipeline itself must never break on this."""
    if not config.SAVE_OUTPUTS:
        return None
    url, gid = rec.get("output_url") or "", rec.get("_id")
    if not url or not gid:
        return None
    try:
        if url.startswith("data:"):
            header, _, b64 = url.partition(",")
            data, ext = base64.b64decode(b64), ("png" if "png" in header else "jpg")
        else:
            with urllib.request.urlopen(url) as r:
                data = r.read()
            ext = "png" if url.lower().split("?")[0].endswith(".png") else "jpg"
        d = _day_dir(rec.get("ts"))
        img = d / f"{gid}.{ext}"
        img.write_bytes(data)
        side = {k: rec.get(k) for k in _SIDE_KEYS}
        side["file"] = img.name
        (d / f"{gid}.json").write_text(json.dumps(side, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
        return f"outputs/{d.name}/{img.name}"
    except Exception:
        return None


def update_sidecar(gid: str, fields: dict[str, Any]) -> None:
    """Keep the local metadata in sync (e.g. after a human rating)."""
    if not config.SAVE_OUTPUTS:
        return
    try:
        for p in config.OUTPUTS_DIR.glob(f"*/{gid}.json"):
            side = json.loads(p.read_text(encoding="utf-8"))
            side.update(fields)
            p.write_text(json.dumps(side, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def list_files() -> list[dict[str, Any]]:
    """Everything saved locally, newest first — feeds the 'Soubory' panel."""
    out: list[dict[str, Any]] = []
    if not config.OUTPUTS_DIR.exists():
        return out
    for side_path in config.OUTPUTS_DIR.glob("*/*.json"):
        try:
            side = json.loads(side_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        day, f = side_path.parent.name, side.get("file") or ""
        out.append({"id": side.get("_id"), "ts": side.get("ts"), "format": side.get("format"),
                    "mode": side.get("mode"), "score": side.get("final_score"),
                    "hard_fail": side.get("hard_fail", False), "series_id": side.get("series_id"),
                    "url": f"/outputs/{day}/{f}", "meta_url": f"/outputs/{day}/{side_path.name}"})
    out.sort(key=lambda x: x.get("ts") or 0, reverse=True)
    return out
