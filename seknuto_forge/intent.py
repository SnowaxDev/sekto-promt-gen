"""Natural-language brief -> a structured, brand-locked build plan.

'Napíšu co chci' -> the system reads the design-system banks (the controlled vocabulary) and
the mode/format map, and turns a short Czech brief into the exact `variables` the chassis needs.
Everything it may choose is already in-brand, so the output stays locked to the identity.
"""
from __future__ import annotations
from typing import Any
from . import config, knowledge, chassis, evaluate

_ALLOWED_COPY = ("ladder", "eyebrow", "chips", "status", "proof", "cta", "micro",
                 "service_headline", "location")


def _system_prompt() -> str:
    design = knowledge.load_design()
    banks = design["banks"]
    fmts = ", ".join(chassis.FORMAT_SPECS.keys())
    bank_txt = "\n".join(f"- {k}: {v}" for k, v in banks.items())
    return (
        "You are the art director for SeknuTo.cz (Czech garden service). Turn a short brief into a "
        "STRICT JSON build plan. Return ONLY JSON, no prose, no fences.\n\n"
        f"Allowed formats: {fmts}\n"
        "Modes: dark_emerald (premium digital — IG/OG/story), B_sluzby (print: services + diagonal), "
        "A_transformace (print: before/after), editorial_immersive (real-photo house style).\n\n"
        "Pick copy ONLY from these banks (verbatim, keep Czech diacritics). Do not invent new copy:\n"
        f"{bank_txt}\n\n"
        "JSON shape (include ONLY fields that apply to the chosen mode):\n"
        '{ "format": "<one allowed format>", "mode": "<one mode>", "series": <bool>, '
        '"count": <int 1-6>, "ladder": ["L1","L2","L3"], "eyebrow": "...", "chips": ["...","..."], '
        '"status": "...", "proof": "...", "cta": "...", "micro": "...", '
        '"service_headline": "...", "location": "Dvůr Králové a okolí" }\n\n'
        "Routing hints: nábor/hiring -> story + dark_emerald; leták/plakát/tisk -> A3 or DL + B_sluzby; "
        "před/po/transformace -> A_transformace (print); carousel/série/více příspěvků -> series:true with "
        "count; Instagram/příspěvek -> ig_post + dark_emerald. Choose the single best fit."
    )


def interpret(brief: str) -> dict[str, Any]:
    """Return a normalized `variables` dict for chassis.build_prompt from a free-text brief.
    Falls back to a safe default if no API key / parse fails — the pipeline always gets a plan."""
    plan = _call_model(brief)
    if not plan:
        plan = {"format": "ig_post", "mode": "dark_emerald",
                "service_headline": (brief or "").strip()[:60] or None}
    return _normalize(plan, brief)


def _call_model(brief: str) -> dict[str, Any] | None:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=config.CRITIC_MODEL, max_tokens=700, system=_system_prompt(),
            messages=[{"role": "user", "content": (brief or "").strip()[:1000]}])
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        return evaluate._parse_json(text)
    except Exception:
        return None


def _normalize(plan: dict[str, Any], brief: str) -> dict[str, Any]:
    """Clamp to the allowed vocabulary so a hallucinated field can never break the build."""
    mode = plan.get("mode")
    if mode not in chassis.VALID_MODES:
        mode = "dark_emerald"
    fmt = plan.get("format")
    if fmt not in chassis.FORMAT_SPECS:
        fmt = "ig_post" if mode == "dark_emerald" else "A3"
    out: dict[str, Any] = {"format": fmt, "mode": mode,
                           "location": plan.get("location") or knowledge.load_patterns()["locked_strings"]["region"]}
    for k in _ALLOWED_COPY:
        if k in plan and plan[k]:
            out[k] = plan[k]
    if isinstance(plan.get("ladder"), list):
        out["ladder"] = [str(x) for x in plan["ladder"] if str(x).strip()][:3]
    if isinstance(plan.get("chips"), list):
        out["chips"] = [str(x) for x in plan["chips"] if str(x).strip()][:4]
    out["series"] = bool(plan.get("series"))
    out["count"] = max(1, min(int(plan.get("count", 3) or 3), 6))
    out["_brief"] = (brief or "").strip()[:300]
    return out
