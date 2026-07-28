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


def critique(image_url: str) -> dict[str, Any]:
    """Return {auto_score, checks, defects}. Requires ANTHROPIC_API_KEY + web access
    to fetch the image bytes."""
    import anthropic, urllib.request

    with urllib.request.urlopen(image_url) as r:
        img_bytes = r.read()
    media = "image/png" if image_url.lower().endswith(".png") else "image/jpeg"
    b64 = base64.standard_b64encode(img_bytes).decode()

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model=config.CRITIC_MODEL,
        max_tokens=700,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media, "data": b64}},
                {"type": "text", "text": RUBRIC},
            ],
        }],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    data = json.loads(text)

    checks = data.get("checks", {})
    return {
        "auto_score": _score_from_checks(int(data.get("score", 0)), checks),
        "checks": checks,
        "defects": [d.strip().lower() for d in data.get("defects", [])],
    }


def blend_final(auto_score: float | None, human_score: float | None) -> float | None:
    """Human rating (0-100) overrides/anchors the auto score when present."""
    if human_score is None:
        return auto_score
    if auto_score is None:
        return float(human_score)
    w = config.HUMAN_WEIGHT
    return round(w * human_score + (1 - w) * auto_score, 1)
