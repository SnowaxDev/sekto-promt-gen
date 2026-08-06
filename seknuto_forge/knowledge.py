"""The knowledge pattern: machine-readable brand rules + a self-updating registry
of interchangeable prompt fragments ("variants") scored by outcome.

This is the "knowledge pattern that improves itself" part of the request. Each prompt
slot (opener, hero_after_desc, cta_block, ...) has 1+ variants. build_prompt picks the
best-scoring variant per slot (epsilon-greedy exploration keeps alternatives alive).
After a generation is scored, learn.py credits the chosen variants — good phrasings
rise to the top and become the de-facto default. No model retraining involved.
"""
from __future__ import annotations
import json, random, time
from pathlib import Path
from typing import Any
from . import config


def _load(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_patterns() -> dict[str, Any]:
    """Load the live (mutable) patterns file, initialising it from the seed once."""
    if not config.PATTERNS_LIVE.exists():
        data = _load(config.PATTERNS_SEED)
        save_patterns(data)
        return data
    return _load(config.PATTERNS_LIVE)


_DESIGN_CACHE: dict[str, Any] | None = None


def load_design() -> dict[str, Any]:
    """Load the machine-readable Dark Emerald design system (tokens, banks, rubric,
    master negative). Cached — it's read-only reference, not learned state."""
    global _DESIGN_CACHE
    if _DESIGN_CACHE is None:
        _DESIGN_CACHE = _load(config.DESIGN_SYSTEM)
    return _DESIGN_CACHE


def save_patterns(data: dict[str, Any]) -> None:
    config.PATTERNS_LIVE.parent.mkdir(parents=True, exist_ok=True)
    with open(config.PATTERNS_LIVE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def variant_mean(v: dict[str, Any]) -> float:
    """Mean score of a variant; unseen variants get an optimistic prior of 60
    so brand-new phrasings get tried before being judged."""
    return (v["score_sum"] / v["uses"]) if v["uses"] else 60.0


def pick_variants(patterns: dict[str, Any], epsilon: float | None = None,
                  group: str = "ab") -> dict[str, dict]:
    """Choose one variant per slot. Best mean by default; with prob epsilon, explore a random
    alternative so the loop keeps discovering. `group` scopes the slots: "ab" = print modes
    (opener, cta_block, …); "de" = Dark Emerald style axes (slots prefixed "de_")."""
    eps = config.EXPLORE_EPSILON if epsilon is None else epsilon
    chosen: dict[str, dict] = {}
    for slot, variants in patterns["variants"].items():
        is_de = slot.startswith("de_")
        if (group == "ab" and is_de) or (group == "de" and not is_de):
            continue
        if len(variants) == 1 or random.random() >= eps:
            best = max(variants, key=variant_mean)
        else:
            best = random.choice(variants)
        chosen[slot] = best
    return chosen


def resolve_variants(patterns: dict[str, Any], group: str, fixed: dict[str, str]) -> dict[str, dict]:
    """Resolve an explicit variant vector (slot -> id) for a series so every piece shares one
    look. Missing slots fall back to the current best. Used to keep a campaign consistent."""
    chosen: dict[str, dict] = {}
    for slot, variants in patterns["variants"].items():
        is_de = slot.startswith("de_")
        if (group == "ab" and is_de) or (group == "de" and not is_de):
            continue
        vid = fixed.get(slot)
        match = next((v for v in variants if v["id"] == vid), None)
        chosen[slot] = match or max(variants, key=variant_mean)
    return chosen


def best_vector(patterns: dict[str, Any], group: str = "de") -> dict[str, str]:
    """The current best variant per slot in a group — the consistent style a series locks onto."""
    out: dict[str, str] = {}
    for slot, variants in patterns["variants"].items():
        is_de = slot.startswith("de_")
        if (group == "ab" and is_de) or (group == "de" and not is_de):
            continue
        out[slot] = max(variants, key=variant_mean)["id"]
    return out


def credit_variants(patterns: dict[str, Any], chosen_ids: dict[str, str], score: float) -> None:
    """Attribute a generation's final score to the variants that produced it."""
    for slot, vid in chosen_ids.items():
        for v in patterns["variants"].get(slot, []):
            if v["id"] == vid:
                v["uses"] += 1
                v["score_sum"] += float(score)
                break


def add_variant(patterns: dict[str, Any], slot: str, text: str, cap: bool = True) -> str | None:
    """Append a variant to a slot (deduped; capped for auto-discovery, uncapped for manual edits).
    New variants start unseen (optimistic prior) so the bandit tries them before judging."""
    text = (text or "").strip()
    pool = patterns["variants"].get(slot)
    if not text or pool is None:
        return None
    if cap and len(pool) >= config.DE_MAX_VARIANTS_PER_AXIS:
        return None
    if any(v["text"].strip().lower() == text.lower() for v in pool):
        return None
    vid = f"{slot}_{'disc' if cap else 'man'}_{int(time.time())}_{len(pool)}"
    pool.append({"id": vid, "text": text, "uses": 0, "score_sum": 0.0})
    return vid


def edit_variant(patterns: dict[str, Any], slot: str, vid: str, text: str) -> bool:
    """Rewrite an existing variant's text (manual knowledge editing)."""
    for v in patterns["variants"].get(slot, []):
        if v["id"] == vid:
            v["text"] = (text or "").strip()
            return True
    return False


def delete_variant(patterns: dict[str, Any], slot: str, vid: str) -> bool:
    """Remove a variant from a slot. Refuses to empty a slot (a slot needs >=1 option)."""
    pool = patterns["variants"].get(slot)
    if not pool or len(pool) <= 1:
        return False
    n = len(pool)
    pool[:] = [v for v in pool if v["id"] != vid]
    return len(pool) < n


def maybe_promote_defect(patterns: dict[str, Any], recent_defects: list[str]) -> list[str]:
    """If a defect recurs above threshold in the recent window, append it to the
    failure log and its terms to the base negative list. Returns newly-promoted defects."""
    counts: dict[str, int] = {}
    for d in recent_defects:
        counts[d] = counts.get(d, 0) + 1
    known = {f["symptom"] for f in patterns["failure_log"]}
    promoted = []
    for defect, n in counts.items():
        if n >= config.DEFECT_PROMOTE_THRESHOLD and defect not in known:
            fid = f"AUTO-{int(time.time())}-{len(promoted)}"
            patterns["failure_log"].append({
                "id": fid, "symptom": defect,
                "root_cause": "auto-detected recurring defect",
                "fix": "review prompt slot responsible; tighten instruction",
                "negative": [defect],
            })
            if defect not in patterns["base_negative"]:
                patterns["base_negative"].append(defect)
            promoted.append(defect)
    return promoted
