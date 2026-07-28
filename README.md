# SeknuTo Forge

Self-improving prompt + image pipeline for SeknuTo.cz marketing materials.
Generates on **Replicate** (nano-banana-2 / ideogram), logs every result to a
**database**, auto-critiques with a vision model, and **learns which prompt phrasings
win** — feeding them back as defaults. Recurring defects auto-append to the failure log.

## What it actually does (honest scope)

It is a **bandit loop**, not magic self-training:

1. **Assemble** a production prompt deterministically from the locked Unified Print
   Chassis (locked strings, single 42° diagonal, element-count lock, diacritics, negatives).
   The only "free" text is a small set of interchangeable phrasings ("variants") per slot.
2. **Generate** on Replicate with your real before/after/logo as references.
3. **Critique** the output with a vision model against your checklist (diacritics,
   single diagonal, no duplicate logo, brand colors, headline present…) → a 0–100 score.
4. **Store** the full record (prompt, variant IDs, params, image URL, score, defects).
5. **Learn** — credit the variants that produced the score; the best phrasing per slot
   rises to the top and becomes the default. Explore occasionally (`EXPLORE_EPSILON`).
6. **Promote defects** — a defect recurring ≥N times auto-appends to the failure log
   and to the negative prompt, so the same mistake stops happening.
7. **Retrieve** — a new request warm-starts from the best past generation like it
   ("lock & reuse", automated).

What it does **not** do: invent better prompts with zero signal, or fine-tune the image
model. The reward signal comes from the auto-critic + your 1-click ratings. Keep rating
a sample of outputs — the critic is a fast proxy, your eye is ground truth.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env         # fill REPLICATE_API_TOKEN + ANTHROPIC_API_KEY
```

Storage runs with **zero infra** (local `data/store.json`). To use the same MongoDB as
your SekTo backend, set `MONGO_URI` in `.env`.

## Run — web UI on your PC (easiest)

```bash
make install          # or: pip install -r requirements.txt
cp .env.example .env   # fill REPLICATE_API_TOKEN + ANTHROPIC_API_KEY
make run              # -> open http://127.0.0.1:8000
```
Windows: double-click `run.bat`. The dashboard (`webui/index.html`) is one static file —
no React, no build step. It lets you pick format + mode, preview the prompt (cost 0),
generate, see the auto-critic score + defects, rate results, and watch the leaderboard.

## Run in Claude Code

Open the folder in Claude Code. It reads `CLAUDE.md` automatically (brand rules + commands),
so you can just say things like *"vygeneruj DL leták v módu A"* or *"přidej variantu do
cta_block"* and it will run the right command and respect every locked rule. See `ALGORITHM.md`
for the full step-by-step the agent follows.

## Run — API only (drops into SekTo)

```bash
uvicorn seknuto_forge.api:app --reload
```
Serves the UI at `/` and the JSON endpoints below.

| Endpoint | Purpose |
|---|---|
| `POST /prompt` | assemble a prompt, generate nothing (cost 0 — preview) |
| `POST /generate` | build + generate + auto-critique + store |
| `POST /rate` | attach a human 0–100 score to a generation |
| `GET /best?format=DL&mode=B_sluzby` | best exemplar (warm start) |
| `GET /leaderboard` | which prompt variants are winning |
| `GET /generations` | raw log |
| `GET /knowledge` | current failure log + negative list |

`POST /generate` body:
```json
{
  "variables": {"format":"DL","mode":"A_transformace","service_headline":"Zkracování + čištění tújí"},
  "image_urls": ["https://.../before.jpg","https://.../after.jpg","https://.../logo.png"],
  "auto_evaluate": true
}
```

## Run — CLI

```bash
python -m seknuto_forge.cli prompt --format DL --mode A_transformace
python -m seknuto_forge.cli generate --format banner_horizontal --mode B_sluzby \
    --img https://.../lawn.jpg --img https://.../logo.png
python -m seknuto_forge.cli rate <generation_id> 85
python -m seknuto_forge.cli leaderboard
```

## Formats supported

`DL`, `A5`, `A4`, `A3`, `banner_vertical`, `banner_horizontal`, `rollup`, `social` — each maps to the
right aspect ratio and reading-distance rules. QR auto-drops on distant banners.

Modes: `A_transformace` (before/after) · `B_sluzby` (services) · `editorial_immersive` (house style, real photo).

## Extending

- **Add a phrasing to test:** append a variant to a slot in `data/patterns.seed.json`
  (`uses:0, score_sum:0`). It gets an optimistic prior so it's tried, then judged.
- **Tighten a rule:** edit `RUBRIC` in `evaluate.py` — the check flows into the score.
- **Better retrieval:** `learn.retrieve` currently filters by format+mode; swap in
  embeddings (store a signature per generation, nearest-neighbour) if you want fuzzy match.
- **Image hosting:** Replicate needs public URLs — host before/after/logo on Vercel/S3
  and pass URLs in `image_urls`.

See `ARCHITECTURE.md` for the module map and data flow.
