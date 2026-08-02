"""Automatic critic. Sends the generated image to a vision model and scores it against
the SeknuTo checklist, returning a numeric score + per-check booleans + named defects.

The critic is a *proxy* for your eye — treat auto_score as a fast filter and keep
occasional human ratings (rate()) as ground truth. final_score blends the two.
"""
from __future__ import annotations
import base64, json, re
from typing import Any
from . import config

RUBRIC = """You are the quality critic for SeknuTo.cz print artwork. Judge ONLY what you see.
Return STRICT JSON, no prose, no markdown fences, with this shape:
{
  "score": <0-100 integer overall quality>,
  "checks": {
    "diacritics_ok": <bool>,          // all Czech accents correct (Sekáme, Kácíme, Čistíme, Dvůr, Králové)
    "single_diagonal": <bool>,         // exactly one 42-45° diagonal, none duplicated
    "logo_present": <bool>,            // SeknuTo.cz grass-blade logo top-left
    "no_duplicate_elements": <bool>,   // no doubled logo/phone/CTA/badge
    "brand_colors_only": <bool>,       // greens #3FA34D/#2d8840/#1e5a32, at most one yellow accent
    "service_headline_present": <bool>,// hero shows the service words, not generic "Hotovo"
    "phone_legible": <bool>,           // 730 588 372 clearly readable
    "no_technical_labels": <bool>      // no px/mm/dimension/wireframe text rendered
  },
  "defects": [ "<short lowercase defect phrase>", ... ]  // e.g. "duplicate logo", "Cistime misspelled"
}
Deduct hard for any misspelling of Czech words or duplicated elements."""


def _score_from_checks(score: int, checks: dict[str, bool]) -> float:
    """Blend the model's holistic score with the hard checklist so a single
    misspelling can't slip through on vibes."""
    passed = sum(1 for v in checks.values() if v)
    total = max(len(checks), 1)
    checklist = 100.0 * passed / total
    return round(0.5 * score + 0.5 * checklist, 1)


def _rubric_dark_emerald(design: dict[str, Any]) -> str:
    """Build the §13 rubric instruction from the machine-readable design system."""
    r = design["rubric"]
    crit = "\n".join(f'    "{c["key"]}": <bool>,   // w{c["weight"]} — {c["desc"]}'
                     for c in r["criteria"])
    hard = "; ".join(r["hard_fails"])
    return (
        'You are the QA critic for SeknuTo.cz "Dark Emerald" artwork (design system v3). '
        'Judge ONLY what you see. Return STRICT JSON, no prose, no fences:\n'
        "{\n"
        '  "score": <0-100 holistic>,\n'
        '  "checks": {\n' + crit + "\n  },\n"
        '  "hard_fail": <bool>,   // true if ANY of: ' + hard + "\n"
        '  "defects": [ "<short lowercase defect>", ... ]\n'
        "}\n"
        "A single Czech diacritics error is an automatic hard_fail. Deduct hard for duplicated "
        "unique elements, a second glowing element, any visible price, or English text."
    )


def critique(image_url: str, mode: str = "B_sluzby") -> dict[str, Any]:
    """Return {auto_score, checks, defects, hard_fail}. dark_emerald mode is scored against
    the weighted §13 rubric; other modes use the diagonal checklist. Requires ANTHROPIC_API_KEY."""
    import anthropic, urllib.request
    from . import knowledge

    if image_url.startswith("data:"):
        header, _, b64data = image_url.partition(",")
        img_bytes = base64.b64decode(b64data)
        media = "image/png" if "png" in header else "image/jpeg"
    else:
        with urllib.request.urlopen(image_url) as r:
            img_bytes = r.read()
        media = "image/png" if image_url.lower().endswith(".png") else "image/jpeg"
    b64 = base64.standard_b64encode(img_bytes).decode()

    design = knowledge.load_design()
    rubric = _rubric_dark_emerald(design) if mode == "dark_emerald" else RUBRIC

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model=config.CRITIC_MODEL, max_tokens=900,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media, "data": b64}},
            {"type": "text", "text": rubric},
        ]}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    data = json.loads(text)
    checks = data.get("checks", {})
    defects = [d.strip().lower() for d in data.get("defects", [])]

    if mode == "dark_emerald":
        defs = design["rubric"]["criteria"]
        auto = float(sum(c["weight"] for c in defs if checks.get(c["key"])))
        hard = bool(data.get("hard_fail")) or any(
            (not checks.get(c["key"])) and c["hard_fail_if_false"] for c in defs)
    else:
        auto = _score_from_checks(int(data.get("score", 0)), checks)
        hard = bool(data.get("hard_fail")) or not checks.get("diacritics_ok", True) \
            or not checks.get("no_technical_labels", True)

    return {"auto_score": round(auto, 1), "checks": checks, "defects": defects, "hard_fail": hard}


def blend_final(auto_score: float | None, human_score: float | None) -> float | None:
    """Human rating (0-100) overrides/anchors the auto score when present."""
    if human_score is None:
        return auto_score
    if auto_score is None:
        return float(human_score)
    w = config.HUMAN_WEIGHT
    return round(w * human_score + (1 - w) * auto_score, 1)


def _brand_safe(candidate: str, original: str, patterns: dict[str, Any]) -> bool:
    """Fail-safe guard on a rewritten prompt: it must not DROP any locked string that the
    original carried (mode-specific — editorial has no phone, mode A has PŘED/PO pills, etc.)
    and must not introduce prices. Enforces CLAUDE.md even if the LLM slips."""
    for val in patterns["locked_strings"].values():
        if val and val in original and val not in candidate:
            return False
    # Only scan the POSITIVE part — the negative/never-do sections legitimately
    # name Kč / per m2 as things to avoid, so they must not trip the guard.
    positive = candidate.split("=== MUST NEVER DO ===")[0].split("NEGATIVE PROMPT:")[0].lower()
    banned = ["kč", "czk", " per m2", "/m2", "za m2", "cena od", "cena:"]
    return not any(b in positive for b in banned)


IMPROVE_SYS = """You are a prompt engineer for SeknuTo.cz print artwork. You are given a
production image prompt and the auto-critic's failed checks + defects for the image it
produced. Rewrite the prompt so those SPECIFIC defects are fixed.

HARD RULES you must never break (rewrite fails otherwise):
- Keep EVERY locked string exactly: web 'SeknuTo.cz', phone '730 588 372',
  region 'Dvůr Králové a okolí', tagline, hero headline — verbatim, with diacritics.
- Never add prices (no Kč, no per m2). Only 'Cena na míru' / 'Kalkulace zdarma'.
- Exactly one yellow (#FFD54F) accent. Exactly one 42-45° diagonal with a #3FA34D edge (modes A/B).
- Keep the DIACRITICS block and the NEGATIVE PROMPT. Colors only from the locked palette.
- Do not invent new sections; tighten wording to remove the reported defects.
Return ONLY the full improved prompt text — no commentary, no markdown fences."""


def improve_prompt(prompt: str, checks: dict[str, bool], defects: list[str],
                   patterns: dict[str, Any]) -> str:
    """Ask Claude to rewrite the prompt to fix the critic's findings, brand-safely.
    Returns the improved prompt, or the original if the rewrite is unsafe/unavailable."""
    import anthropic

    failed = [k for k, v in (checks or {}).items() if not v]
    task = (
        f"FAILED CHECKS: {', '.join(failed) or 'none'}\n"
        f"DEFECTS: {', '.join(defects) or 'none'}\n\n"
        f"CURRENT PROMPT:\n{prompt}"
    )
    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=config.CRITIC_MODEL, max_tokens=2000, system=IMPROVE_SYS,
            messages=[{"role": "user", "content": task}],
        )
        improved = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
        improved = re.sub(r"^```(\w+)?|```$", "", improved, flags=re.MULTILINE).strip()
    except Exception:
        return prompt  # no key / API error -> keep the working prompt

    # brand-safety gate: only accept the rewrite if it still obeys the locked rules
    return improved if (improved and _brand_safe(improved, prompt, patterns)) else prompt
