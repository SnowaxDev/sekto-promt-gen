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
    "ig_post":          {"aspect": "1:1",   "note": "Instagram post 1080x1080, dark emerald"},
    "ig_portrait":      {"aspect": "4:5",   "note": "Instagram portrait 1080x1350, dark emerald"},
    "story":            {"aspect": "9:16",  "note": "IG/FB story 1080x1920, keep UI-safe top 9% / bottom 12%"},
    "og_banner":        {"aspect": "16:9",  "note": "OG/web banner 1920x1005, horizontal 55/45 split"},
}

# Modes: A_transformace (before/after diagonal), B_sluzby (services + diagonal),
# editorial_immersive (house style: full-bleed real photo, centered, glass pills),
# dark_emerald (Dark Emerald v3 digital system: 5-layer canvas, headline ladder, glass components).
VALID_MODES = ("A_transformace", "B_sluzby", "editorial_immersive", "dark_emerald")


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
    # A + B are brand hero-photo modes -> nano-banana-2. Only an explicit
    # uses_photos=False forces the text-only (ideogram) path.
    uses_photos = variables.get("uses_photos", mode in ("A_transformace", "B_sluzby"))
    location = variables.get("location", L["region"])
    headline = variables.get("service_headline", L["hero_headline"])
    show_qr = fmt not in ("banner_horizontal", "banner_vertical")

    if mode == "editorial_immersive":
        return _build_editorial(variables, patterns, spec)
    if mode == "dark_emerald":
        return _build_dark_emerald(variables, patterns, spec)

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

    style_line = (
        "\n=== STYLE REFERENCE ===\n"
        "The LAST reference image is a STYLE reference. Match its overall composition energy, "
        "color grading, lighting mood and typographic feel. Do NOT copy its text, logos or people "
        "— obey every SeknuTo brand rule, locked string, single diagonal and one-yellow limit below.\n"
        if variables.get("style_ref") else ""
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

{photo_rules}{style_line}
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
    style_line = (
        "\n=== STYLE REFERENCE ===\nThe LAST reference image is a STYLE reference: match its "
        "color grading, lighting mood and layout feel, while keeping IMAGE 1's real people/scene "
        "and every brand rule below.\n" if variables.get("style_ref") else ""
    )

    prompt = f"""Create a FINAL PRODUCTION vertical 9:16 advertising poster (4K) for Czech garden
service SeknuTo.cz, editorial immersive house style. Finished artwork — render NO dimension
markers, px/mm labels, wireframe boxes, or instruction text.

=== REAL ASSETS — DO NOT REGENERATE ===
IMAGE 1 = a REAL photo of the SeknuTo team / scene outdoors. Use as the FULL-BLEED background.
Preserve the real people, faces, uniforms, tools and scene exactly — never regenerate, replace,
illustrate, or restyle them. Apply only a mild grade (+4% saturation, +3% contrast) and a soft
dark gradient at the very top for text legibility. The customer must recognise the actual team.
IMAGE 2 = SeknuTo.cz logo (green square, 4 grass blades). Use as-is, do not redraw.
{style_line}
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


def _build_dark_emerald(variables, patterns, spec):
    """Dark Emerald v3.0 — the pro digital system (docs/DESIGN_SYSTEM.md §11): five-layer
    emerald canvas, three-tier headline ladder, glass components, one glowing CTA. Deterministic:
    tokens/negatives/rubric come from data/design_system.json; only the copy varies (from banks)."""
    ds = knowledge.load_design()
    L, T, B = patterns["locked_strings"], ds["tokens"], ds["banks"]

    # learnable style axes (§14.2) — the bandit explores new style combinations and learns
    chosen = knowledge.pick_variants(patterns, group="de")
    chosen_ids = {slot: v["id"] for slot, v in chosen.items()}
    ax = lambda k, d="": (chosen[k]["text"] if k in chosen else d)
    accent_id = chosen.get("de_accent_usage", {}).get("id", "none")
    yellow_n = 0 if accent_id == "none" else 1

    status   = variables.get("status", B["status"][0])
    eyebrow  = variables.get("eyebrow", B["eyebrow"][0])
    chips    = variables.get("chips", B["chips"][:3])
    filled   = int(variables.get("chip_filled_index", 1))
    ladder   = variables.get("ladder", B["ladder"][0])
    proof    = variables.get("proof", B["proof"][0])
    body     = variables.get("body", ["Sekání, kácení stromů, živé ploty, výsadba."])
    micro    = variables.get("micro", B["micro"][0])
    cta      = variables.get("cta", B["cta"][0])
    phone    = L["phone"]
    location = variables.get("location", L["region"])

    ladder = list(ladder)[:3]
    while len(ladder) < 3:
        ladder.append("")
    filled = max(0, min(filled, len(chips) - 1))

    strings = (["'" + L["web"] + "'", "'" + status + "'", "'" + eyebrow + "'"]
               + [f"'{c}'" for c in chips]
               + [f"'{l}'" for l in ladder if l]
               + ["'" + proof + "'"] + [f"'{b}'" for b in body]
               + ["'" + micro + "'", "'" + cta + "'", "'" + phone + "'"])
    chip_list = " | ".join(f"'{c}'" + (" (FILLED, gradient)" if i == filled else " (outline)")
                           for i, c in enumerate(chips))
    dia = "\n".join(f"{w} = {b}" for w, b in ds["diacritics"].items())
    negatives = ds["negative_master"] + ", " + ", ".join(patterns["common_misspellings"])

    ladder_treatment = ax("de_ladder_treatment", "line 1 faint white, line 2 white, line 3 green #3FA34D, full stop.")
    cta_style        = ax("de_cta_style", "full-width rounded button with a soft glow.")
    photo_treatment  = ax("de_photo_treatment", "Hero photo on the right, faded into the dark on the left.")
    accent_text      = ax("de_accent_usage", "No yellow anywhere on the canvas.")
    shaft_treatment  = ax("de_light_shaft", "")

    prompt = f"""[BLOCK 0 — PRODUCTION GUARD]
You are producing FINAL PRODUCTION artwork, ready to publish without any editing. Every
specification below is an INSTRUCTION for you to follow, NOT text to display. Render ZERO
technical annotations, dimension markers, px/mm labels, wireframe boxes, zone names, layer
names, font names, or construction lines.

[BLOCK 1 — CANVAS & SYSTEM]
Format: {spec['note']} (aspect {spec['aspect']}). SeknuTo.cz "Dark Emerald" brand system.
Build the background bottom to top, exactly these five layers:
 1. Radial emerald gradient, light centre upper-right: {T['canvas']['emerald_600']} into
    {T['canvas']['emerald_800']} into {T['canvas']['emerald_900']} into near-black {T['canvas']['void']} at the edges. Never a flat colour.
 2. Very faint technical grid of thin white lines at ~3.5% opacity, evenly spaced.
 3. EXACTLY ONE soft volumetric light shaft from the upper-right corner, angled down-left,
    pale green-white, low opacity. {shaft_treatment} Never two shafts.
 4. Radial vignette darkening all four edges.
 5. EXACTLY FOUR thin green corner brackets {T['brand']['green_500_primary']} at 65% opacity, one in
    each corner, L-shaped outlines only — never two, never filled.

[BLOCK 2 — REFERENCE IMAGES]
IMAGE 1 = SeknuTo.cz logo. Place as-is. NEVER redraw, restyle or reinterpret it (capital T mid-word).
IMAGE 2 (if provided) = the real brand worker photo. Preserve his face, clothing and pose exactly;
apply only +5% saturation / +3% contrast. Never regenerate the person. Blend the photo into the dark
canvas with a left-to-dark fade and a bottom scrim — no hard rectangular edge. Never rotate the photo.

[BLOCK 3 — RENDER ONLY THESE EXACT STRINGS]
{' | '.join(strings)}
No other text may appear anywhere on the canvas.

[BLOCK 4 — ELEMENT COUNT LOCK]
Exactly 1 logo lockup · exactly 1 status pill · exactly 1 headline ladder · exactly 1 glass proof
card · exactly 1 green CTA button (the ONLY glowing element) · exactly 4 corner brackets · exactly 1
light shaft · exactly {len(chips)} service chips ({chip_list}). Any element appearing twice is a failure.
Yellow accent used {yellow_n} time(s) here: {accent_text} No QR (digital).

[BLOCK 5 — CANVAS BUILD, TOP TO BOTTOM]
[SECTION 1 — BRAND LOCKUP, upper-left] IMAGE 1 logo + '{L['web']}' in a dark glass pill with a hairline border.
[SECTION 2 — STATUS PILL, upper-right] '{status}' with a small pulsing green dot {T['brand']['green_400_bright']}.
[SECTION 3 — EYEBROW LINE] '{eyebrow}' — first part uppercase tracked {T['brand']['green_200_light']}, place '·' divider then location in muted white.
[SECTION 4 — SERVICE CHIPS] {chip_list}. Outline chips = hairline green border; the FILLED chip uses the CTA gradient. Never more than 4.
[SECTION 5 — HEADLINE LADDER] stacked uppercase lines, condensed geometric extra-bold sans, tight leading,
left-aligned: '{ladder[0]}' / '{ladder[1]}' / '{ladder[2]}'. Treatment: {ladder_treatment}
[SECTION 6 — HERO PHOTO] IMAGE 2 worker, golden-hour rim light, shallow depth. {photo_treatment}
[SECTION 7 — GLASS PROOF CARD] frosted dark glass card, backdrop blur, hairline green border: '{proof}' (gold stars {T['accent']['star']} if a rating). Never over a face.
[SECTION 8 — ACCENT RULE + BODY] a 4px vertical green rule {T['brand']['green_500_primary']} left of: {' / '.join(body)}.
[SECTION 9 — MICRO CTA LINE] '{micro}' small, above the button.
[SECTION 10 — PRIMARY CTA] white bold centred label '{cta}', gradient {T['gradient']['cta_button']}, the ONLY
glowing element on the canvas. Style: {cta_style}
[SECTION 11 — CONTACT FOOTER] '{L['web']} · {phone}' — phone in heavy numerals, the second-largest element on the canvas.

Keep at least 35% of the canvas empty (silence is part of the luxury). Nothing touches the edges.

[BLOCK 6 — DIACRITICS VERIFICATION TABLE]
{dia}

[BLOCK 7 — MUST NEVER DO]
Never redraw the logo · never duplicate any element · never render font names · never render dimension
numbers · never show prices or Kč · never add a second glowing element · never use yellow more than once ·
never place letters of a Czech word apart · never rotate the input photos · never apply heavy filters or
lens flare · never translate the text to English · never a white background.

NEGATIVE PROMPT: {negatives}."""

    return {
        "prompt": prompt.strip(),
        "chosen_variant_ids": chosen_ids,   # §14.2 style axes — credited by the bandit
        "aspect": spec["aspect"],
        "negative": [negatives],
        "model_hint": "image",
        "show_qr": False,
        "google_search": False,     # §11.1 — grounding off for brand assets
        "image_search": False,
    }
