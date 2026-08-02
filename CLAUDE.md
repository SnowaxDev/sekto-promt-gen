# CLAUDE.md — rules for this repo

You are working in **SeknuTo Forge**: a local pipeline that builds brand-locked image
prompts, generates them on Replicate, stores + auto-critiques the results, and learns
which prompt phrasings score best. Read this before doing anything. These rules are hard.

## What this repo is
A Python package `seknuto_forge/` + a single-file web UI (`webui/index.html`) + a JSON
knowledge file (`data/patterns.seed.json`). It runs fully on the user's PC. Storage is a
local JSON file unless `MONGO_URI` is set. See `ALGORITHM.md` for the exact flow.

## Brand & design authority — read before any visual
`docs/DESIGN_SYSTEM.md` is the **Dark Emerald v3.0** master brand & design identity — the
single source of truth for how SeknuTo.cz looks (tokens, 5-layer canvas, headline ladder,
14 components, QA rubric, negative prompt, failure log). Its machine-readable slice lives in
`data/design_system.json` (tokens, copy banks, §13 rubric, master negative, diacritics). The
`dark_emerald` chassis mode builds prompts from it; `evaluate.critique` scores against its
§13 rubric with HARD FAIL rules. Never contradict it; when a request conflicts, surface it.

## Non-negotiable brand rules (never violate, never "improve away")
1. **No fixed prices.** Customer-facing output shows only `Cena na míru` / `Kalkulace ZDARMA`. Never Kč, never per m².
2. **Locked strings** come from `data/patterns.seed.json → locked_strings`. Never invent alternatives: web `SeknuTo.cz` (capital T), phone `730 588 372`, region `Dvůr Králové a okolí`, tagline `Staráme se o váš pozemek od A do Z.`, hero `Sekáme. Kácíme. Čistíme.`
3. **One yellow accent per canvas** (`#FFD54F`). Never a second yellow element.
4. **QR is always a gray placeholder** in generated art — never a real/scannable code. Real QR is composited in print.
5. **Real assets, never regenerate people.** In `editorial_immersive`, the team/scene comes from the reference photo; the model may only color-grade, never redraw faces or replace people.
6. **Czech diacritics are mandatory.** Every rendered word must appear in `patterns → diacritics`. `ů` is a RING (Dvůr, stromů, pozemků), not an acute.
7. **One diagonal** (42–45°) in modes A/B, with a `#3FA34D` edge line. Never two.
8. **Colors are locked** to `patterns → colors`. Never introduce new hex values.

## Modes (mode = which hero the chassis uses)
- `A_transformace` — before/after diagonal (letáky). Needs before + after + logo images.
- `B_sluzby` — services + diagonal (plakát/banner). Hero photo + logo.
- `editorial_immersive` — house style: full-bleed real photo, centered, glass pills, one yellow CTA. Real photo + logo.

## How to run (the user is on a normal PC)
```bash
make install          # pip install -r requirements.txt
cp .env.example .env   # fill REPLICATE_API_TOKEN + ANTHROPIC_API_KEY
make run              # uvicorn -> web UI at http://127.0.0.1:8000
```
Windows: `run.bat`. No frontend build step exists — the UI is one static HTML file.

## Common tasks (do these, don't reinvent)
- **Preview a prompt (cost 0):** `python -m seknuto_forge.cli prompt --format A3 --mode B_sluzby`
- **Generate:** `python -m seknuto_forge.cli generate --format DL --mode A_transformace --img <before> --img <after> --img <logo>`
- **Rate a result:** `python -m seknuto_forge.cli rate <id> 85`
- **See what's winning:** `python -m seknuto_forge.cli leaderboard`

## Adding / changing a prompt phrasing (the learnable part)
Edit `data/patterns.seed.json → variants.<slot>`; append `{"id":"...","text":"...","uses":0,"score_sum":0}`.
Delete `data/patterns.json` (the live copy) to reseed, or leave it to keep learned scores.
Do NOT hardcode phrasing inside `chassis.py` — chassis assembles, `variants` supply wording.

## Editing rules for the agent
- Change one thing at a time; after editing `chassis.py` run `python -m seknuto_forge.cli prompt ...` to verify the prompt still assembles.
- If you add a new rendered Czech word anywhere, add its breakdown to `patterns → diacritics` and its common misspelling to `common_misspellings` in the same change.
- Never remove a brand rule to satisfy a request. If a request conflicts with the rules above, surface the conflict instead of silently breaking a rule.
- Keep the web UI a single dependency-free file. No React/build tooling in this repo.

## Files
`chassis.py` assemble · `knowledge.py` patterns+bandit · `generate.py` Replicate ·
`evaluate.py` vision critic · `store.py` DB · `learn.py` loop · `api.py` FastAPI+UI ·
`cli.py` terminal · `data/patterns.seed.json` brand knowledge · `webui/index.html` dashboard.
