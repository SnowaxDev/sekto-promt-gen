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


def pick_variants(patterns: dict[str, Any], epsilon: float | None = None) -> dict[str, dict]:
    """Choose one variant per slot. Best mean by default; with prob epsilon,
    explore a random alternative so the loop keeps gathering evidence."""
    eps = config.EXPLORE_EPSILON if epsilon is None else epsilon
    chosen: dict[str, dict] = {}
    for slot, variants in patterns["variants"].items():
        if len(variants) == 1 or random.random() >= eps:
            best = max(variants, key=variant_mean)
        else:
            best = random.choice(variants)
        chosen[slot] = best
    return chosen


def credit_variants(patterns: dict[str, Any], chosen_ids: dict[str, str], score: float) -> None:
    """Attribute a generation's final score to the variants that produced it."""
    for slot, vid in chosen_ids.items():
        for v in patterns["variants"].get(slot, []):
            if v["id"] == vid:
                v["uses"] += 1
                v["score_sum"] += float(score)
                break


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
