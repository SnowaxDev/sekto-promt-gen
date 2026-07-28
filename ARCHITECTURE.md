# Architecture

## Data flow (one cycle)

```
variables ─▶ chassis.build_prompt ─▶ generate.generate (Replicate) ─▶ image URL
                    │                                                      │
             picks best variant                                    evaluate.critique
             per slot (bandit)                                     (vision model)
                    │                                                      │
                    └────────────── store.insert(record) ◀────────────────┘
                                          │
                              learn.run_once credits the
                              chosen variants with the score
                                          │
                    ┌─────────────────────┼─────────────────────┐
              knowledge.credit      maybe_promote_defect    (later) learn.rate
              _variants             → failure_log grows      → human override
                    │                                            re-blends score
                    ▼
              next build_prompt uses the now-better defaults
```

## Modules

| File | Responsibility |
|---|---|
| `config.py` | env-driven settings; local-JSON vs MongoDB switch; model IDs; loop tuning |
| `knowledge.py` | load/save the pattern registry; **bandit** variant selection + crediting; failure-log auto-promote |
| `chassis.py` | deterministic prompt assembly from locked chassis + chosen variants; format→aspect map |
| `generate.py` | Replicate wrapper (nano-banana-2 photo refs / ideogram text-only) |
| `store.py` | generation database — MongoDB or local JSON, same interface |
| `evaluate.py` | vision auto-critic → score + checklist + defects; human-score blend |
| `learn.py` | orchestrates the loop; rating; exemplar retrieval; leaderboard |
| `api.py` | FastAPI endpoints for the SekTo backend |
| `cli.py` | terminal driver |
| `data/patterns.seed.json` | machine-readable brand knowledge + learnable variants |

## Why the learning is defensible

Each generation records exactly which variant it used per slot (`chosen_variant_ids`).
The score (auto-critic, optionally overridden by a human) is attributed back to those
variants. Over N generations, `variant_mean` separates good phrasings from bad, and
`pick_variants` exploits the leader while `EXPLORE_EPSILON` keeps testing challengers.
This is a contextual-free multi-armed bandit over prompt fragments — simple, transparent,
and it genuinely converges given signal. No black-box "self-training" claims.

## The knowledge pattern (self-updating failure log)

`data/patterns.seed.json` seeds the failure log from your design masterclass. When the
auto-critic reports the same defect ≥ `DEFECT_PROMOTE_THRESHOLD` times inside the last
`DEFECT_WINDOW` generations, `maybe_promote_defect` appends a new failure entry and adds
its terms to the base negative prompt. Your masterclass thus grows itself from real output,
and every subsequent prompt inherits the guard.

## Suggested rollout

1. Point `image_urls` at hosted before/after/logo, run `POST /generate` for a few DL
   flyers with `auto_evaluate:true`. Rate the best 2–3 by eye (`POST /rate`).
2. Watch `GET /leaderboard` — after ~15–20 rated generations the winning variants stabilise.
3. Lock the winners (they're already the defaults) and switch new formats to warm-start
   from `GET /best`. From here new materials are variable swaps, exactly as the design
   system intends.
```
