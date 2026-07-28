"""Deterministic prompt assembly. Given VARIABLES (format, mode, service, location,
photos) it emits the full production prompt following the Unified Print Chassis:
locked strings, single 42° diagonal, element-count lock, diacritics table, negatives.

The learnable phrasing comes from knowledge.pick_variants(); everything brand-critical
(strings, colors, counts, diacritics) is fixed and never left to the model to invent.
"""
from __future__ import annotations
from typing import Any
from . import knowledge

# Format -> nearest aspect ratio the image model supports, plus reading distance note.
FORMAT_SPECS = {
    "DL":               {"aspect": "9:16",  "note": "tall DL flyer proportion, read in hand"},
    "A5":               {"aspect": "9:16",  "note": "A5 flyer, read in hand"},
    "A4":               {"aspect": "3:4",   "note": "A4 poster, read from ~1m"},
    "A3":               {"aspect": "3:4",   "note": "A3 poster, read from 2-3m"},
    "banner_vertical":  {"aspect": "9:16",  "note": "vertical PVC banner, read from 5-15m, few huge words"},
    "banner_horizontal":{"aspect": "16:9",  "note": "wide PVC banner, read from 10-30m, 3-5 words max, no QR"},
    "rollup":           {"aspect": "9:16",  "note": "roll-up, bottom 150mm hidden in stand"},
    "social":           {"aspect": "9:16",  "note": "vertical social ad 1080x1920, emoji allowed"},
}

# Modes: A_transformace (before/after diagonal), B_sluzby (services + diagonal),
# editorial_immersive (house style: full-bleed real photo, centered, glass pills).
VALID_MODES = ("A_transformace", "B_sluzby", "editorial_immersive")


def build_prompt(variables: dict[str, Any], patterns: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return {prompt, chosen_variant_ids, aspect, negative, model_hint}.

    variables: {format, mode ('A_transformace'|'B_sluzby'), service_headline?,
                location?, date?, uses_photos (bool)}
    """
    patterns = patterns or knowledge.load_patterns()
    L = patterns["locked_strings"]
    C = patterns["colors"]

    fmt = variables.get("format", "DL")
    spec = FORMAT_SPECS.get(fmt, FORMAT_SPECS["DL"])
    mode = variables.get("mode", "B_sluzby")
    uses_photos = variables.get("uses_photos", mode == "A_transformace")
    location = variables.get("location", L["region"])
    headline = variables.get("service_headline", L["hero_headline"])
    show_qr = fmt not in ("banner_horizontal", "banner_vertical")

    if mode == "editorial_immersive":
        return _build_editorial(variables, patterns, spec)

    chosen = knowledge.pick_variants(patterns)
    chosen_ids = {slot: v["id"] for slot, v in chosen.items()}

    # --- diacritics block (only for words present) ---
    dia = "; ".join(f"{w}: {b}" for w, b in patterns["diacritics"].items())
    negatives = list(patterns["base_negative"]) + list(patterns["common_misspellings"])

    photo_rules = (
        "=== REFERENCE IMAGES ===\n"
        "IMAGE 1 = BEFORE photo (overgrown). IMAGE 2 = AFTER photo (finished). "
        "IMAGE 3 = SeknuTo.cz logo (green square, 4 grass blades).\n"
        "Preserve original photo content — never regenerate or restyle. Color-grade only: "
        "IMAGE 2 +5% saturation, IMAGE 1 -10% saturation. Never rotate the photos.\n"
        if uses_photos else
        "=== REFERENCE IMAGE ===\nIMAGE 1 = SeknuTo.cz logo. Do not invent extra photos.\n"
    )

    if mode == "A_transformace":
        hero = (
            f"[ZONE 3 HERO, dominant] {chosen['diagonal']['text']} "
            f"Lower-left triangle = BEFORE, upper-right = AFTER. "
            f"{chosen['hero_before_desc']['text']} {chosen['hero_after_desc']['text']} "
            f"Over the after side, right-aligned white heavy sans, three words stacked: '{headline}'."
        )
    else:
        hero = (
            f"[ZONE 3 HERO, dominant] {chosen['diagonal']['text']} "
            f"One strong photo of a freshly mowed striped lawn / working team under the diagonal. "
            f"On the solid side, three words stacked HUGE white heavy sans: '{headline}'. "
            f"Then green '{L['tagline']}'."
        )

    qr = (
        f"QR code bottom-right on white with caption 'Napište nám'." if show_qr else
        "No QR code (too far to scan at banner distance)."
    )

    prompt = f"""{chosen['opener']['text']}
Format: {fmt} ({spec['note']}). Aspect {spec['aspect']}. CMYK, print-ready.

{photo_rules}
=== BRAND CHASSIS (identical across all formats) ===
Logo top-left: rounded square {C['forest']} with four grass blades (2 white + 2 {C['light_blade']}
growing up) + wordmark '{L['web']}' geometric sans-serif semibold, capital T mid-word.
Colors LOCKED: {C['primary']} primary, {C['dark_green']} dark, {C['forest']} forest,
{C['light_blade']} light blade, {C['yellow']} yellow (max once), white, {C['text_dark']} dark.
Never invent colors.

=== RENDER ONLY THESE EXACT STRINGS ===
'{L['web']}' | '{location}' | '{L['tags']}' | '{headline}' | '{L['tagline']}' |
'{L['proof']}' | '{L['cta_label']}' | '{L['phone']}' | 'Napište nám'

=== ELEMENT COUNT LOCK ===
Exactly 1 logo lockup (top-left), 1 diagonal (42-45°), 1 green edge line, 1 CTA panel,
1 phone number, {'1 QR code' if show_qr else '0 QR codes'}, max 1 yellow accent. Never duplicate any element.

=== ZONES top to bottom ===
[ZONE 1] logo lockup + '{L['web']}'.
[ZONE 2] '{location}' + tag row '{L['tags']}'.
{hero}
[ZONE 4] '{L['tagline']}' green + '{L['proof']}' smaller.
[ZONE 5 CTA] {chosen['cta_block']['text']} {qr}
[FOOTER] thin strip '{L['web']} · {L['region']}'.

=== DIACRITICS (mandatory) ===
{dia}

=== MUST NEVER DO ===
Never render font names or dimension numbers as text. Never duplicate logo, diagonal,
CTA, or phone. Never invent prices. Never space out letters inside a word.
Never misspell as: {', '.join(patterns['common_misspellings'])}.

NEGATIVE PROMPT: {', '.join(negatives)}."""

    return {
        "prompt": prompt.strip(),
        "chosen_variant_ids": chosen_ids,
        "aspect": spec["aspect"],
        "negative": negatives,
        "model_hint": "image" if uses_photos else "image_text",
        "show_qr": show_qr,
    }

def _build_editorial(variables, patterns, spec):
    """Editorial Immersive — the house style: full-bleed REAL photo, centered
    composition, two-tier headline, glassmorphism pills, one yellow CTA. People
    and scene come from the reference photo and must never be regenerated.
    """
    L, C = patterns["locked_strings"], patterns["colors"]
    negatives = list(patterns["base_negative"]) + list(patterns["common_misspellings"]) + [
        "AI-generated people", "regenerated faces", "replaced team", "illustrated people",
        "stock-photo look",
    ]
    headline_top = variables.get("headline_top", "👋 " + variables.get("service_headline", "Krásná zahrada"))
    headline_big = variables.get("headline_big", "bez starostí.")
    question = variables.get("question", "")
    pills = variables.get("pills", [
        "🌱 Sekání a údržba zahrad",
        "🤝 Férový přístup",
        "☀️ Rychlý termín",
    ])
    cta_label = variables.get("cta_label", "OZVI SE →")
    cta_action = variables.get("cta_action", "Napiš nám do zpráv")
    location = variables.get("location", L["region"])
    dia = "; ".join(f"{w}: {b}" for w, b in patterns["diacritics"].items())
    pill_lines = " | ".join(f"'{p}'" for p in pills)

    prompt = f"""Create a FINAL PRODUCTION vertical 9:16 advertising poster (4K) for Czech garden
service SeknuTo.cz, editorial immersive house style. Finished artwork — render NO dimension
markers, px/mm labels, wireframe boxes, or instruction text.

=== REAL ASSETS — DO NOT REGENERATE ===
IMAGE 1 = a REAL photo of the SeknuTo team / scene outdoors. Use as the FULL-BLEED background.
Preserve the real people, faces, uniforms, tools and scene exactly — never regenerate, replace,
illustrate, or restyle them. Apply only a mild grade (+4% saturation, +3% contrast) and a soft
dark gradient at the very top for text legibility. The customer must recognise the actual team.
IMAGE 2 = SeknuTo.cz logo (green square, 4 grass blades). Use as-is, do not redraw.

=== BRAND COLORS (locked) ===
{C['primary']} primary green, {C['forest']} forest, {C['light_blade']} light blade,
{C['yellow']} yellow (used EXACTLY ONCE = CTA label), white, {C['text_dark']} near-black.

=== RENDER ONLY THESE EXACT STRINGS ===
'{L['web']}' | '{location}' | '{headline_top}' | '{headline_big}' | {"'" + question + "' | " if question else ""}{pill_lines} | '{cta_label}' | '{cta_action}'

=== CANVAS TOP TO BOTTOM (centered composition) ===
[TOP] soft dark gradient over the photo. Centered: IMAGE 2 logo, under it '{L['web']}' white
semibold (capital S + capital T).
[HEADLINE] centered two tiers, tight leading: line 1 '{headline_top}' white extra-bold; line 2
'{headline_big}' MASSIVE near-black {C['text_dark']} heavy sans over the brightest part of the photo.
[SUBLINE] centered green {C['primary']} bold '{L['web']} · {location}'.
[DIVIDER] one short centered green {C['primary']} line.
{"[QUESTION] centered white italic '" + question + "'." if question else ""}
[PILLS] exactly {len(pills)} glassmorphism pills, evenly stacked, near full width, fully rounded:
dark translucent fill (deep green-black ~55% opacity) with subtle backdrop blur and a 1px hairline
light border at low opacity. Emoji left, white bold text: {pill_lines}.
[CTA] centered small-caps yellow {C['yellow']} '{cta_label}' wide letter-spacing; below large white
heavy sans '{cta_action}'.
[FOOTER] centered white '{L['web']}'.

=== DIACRITICS (mandatory) ===
{dia}

=== MUST NEVER DO ===
Never regenerate or replace the real people/scene from IMAGE 1 (grade only). Never render font
names or dimension numbers. Never duplicate logo, headline, or CTA. Never use more than one yellow
element. Never space out letters inside a single word. Diacritics pixel-perfect.
Never misspell as: {', '.join(patterns['common_misspellings'])}.

NEGATIVE PROMPT: {', '.join(negatives)}."""

    return {
        "prompt": prompt.strip(),
        "chosen_variant_ids": {},   # editorial has no bandit slots yet; deterministic
        "aspect": "9:16",
        "negative": negatives,
        "model_hint": "image",
        "show_qr": False,
    }
