# ALGORITHM — the whole system, step by step

This is the exact algorithm the pipeline runs. Every step is deterministic except the
variant selection (a transparent bandit) and the vision critic (an LLM). Nothing is a
black box.

## 0. Inputs
```
variables = { format, mode, service_headline?, location?, headline_top?, headline_big?,
              question?, pills?, cta_label?, cta_action?, uses_photos? }
image_urls = [ ... ]   # public URLs Replicate can fetch
```

## 1. Resolve format → aspect + reading rules   (chassis.FORMAT_SPECS)
```
DL/A5/rollup/banner_vertical/social -> 9:16
A4/A3                                -> 3:4
banner_horizontal                    -> 16:9
show_qr = format not in {banner_horizontal, banner_vertical}   # no QR at distance
```

## 2. Pick prompt wording  (knowledge.pick_variants — the learnable step)
For each slot in `patterns.variants` (opener, hero_after_desc, hero_before_desc,
diagonal, cta_block):
```
mean(v) = v.score_sum / v.uses           (unseen -> optimistic prior 60)
with prob (1 - EXPLORE_EPSILON): choose argmax mean(v)     # exploit best phrasing
with prob EXPLORE_EPSILON:       choose a random variant   # explore, keep learning
```
This is a stationary multi-armed bandit over prompt fragments. `editorial_immersive`
has no slots yet → fully deterministic.

## 3. Assemble the prompt  (chassis.build_prompt / _build_editorial)
Deterministic string assembly enforcing every brand rule:
- injects `locked_strings` verbatim (web, phone, region, tagline, headline)
- injects `colors` as exact hex, "yellow used exactly once"
- emits an ELEMENT COUNT LOCK (one logo/diagonal/CTA/phone/QR)
- emits the full `diacritics` table for the model
- emits `base_negative + common_misspellings` as the negative prompt
- mode chooses the hero block:
  - A_transformace → before/after triangles + service headline
  - B_sluzby → one hero photo under the diagonal + 3-word headline + tagline
  - editorial_immersive → full-bleed real photo, centered stack, glass pills, one yellow CTA, "never regenerate people"
Output: `{ prompt, chosen_variant_ids, aspect, negative, model_hint, show_qr }`.

## 4. Generate  (generate.generate → Replicate)
```
if model_hint == "image" and image_urls:  model = google/nano-banana-2
                                           input = {prompt, image_input, aspect_ratio, resolution:4K,
                                                    google_search, image_search, output_format:jpg}
else:                                      model = ideogram-ai/ideogram-v2
                                           input = {prompt, aspect_ratio, magic_prompt_option:Off, negative_prompt}
output_url = normalize(client.run(model, input))
```

## 5. Auto-critique  (evaluate.critique → vision model)
Send the output image + RUBRIC to the critic. It returns:
```
{ score 0-100, checks:{diacritics_ok, single_diagonal, logo_present, no_duplicate_elements,
   brand_colors_only, service_headline_present, phone_legible, no_technical_labels}, defects:[...] }
auto_score = 0.5*score + 0.5*(100 * passed_checks / total_checks)
```
The 50/50 blend stops a "pretty" image from passing while a Czech word is misspelled.

## 6. Store  (store — MongoDB or local JSON)
Persist the full record: prompt, chosen_variant_ids, params, input_images, output_url,
auto_score, auto_checks, auto_defects, human_score(null), final_score.

## 7. Credit the wording  (knowledge.credit_variants)
```
final_score (auto-only for now) is added to every variant used this run:
   v.uses += 1 ; v.score_sum += final_score
```
Good phrasings' means rise → step 2 exploits them next time. This is the learning.

## 8. Auto-promote recurring defects  (knowledge.maybe_promote_defect)
```
look at auto_defects across the last DEFECT_WINDOW generations
if a defect appears >= DEFECT_PROMOTE_THRESHOLD times and is new:
   append it to failure_log and to base_negative
```
The failure log grows itself from real output; every later prompt inherits the guard.

## 9. Human rating (optional, ground truth)  (learn.rate)
```
final = HUMAN_WEIGHT*human + (1-HUMAN_WEIGHT)*auto      (auto alone if no human)
```
Re-crediting is delta-correct: the earlier auto-only credit is subtracted, the blended
score added, so a re-rated generation never double-counts.

## 10. Warm start / lock & reuse  (learn.retrieve)
For a new request, return the highest-`final_score` past generation with the same
format+mode. That prompt is the starting point — "lock & reuse" automated. (Swap the
filter for embeddings later if you want fuzzy matching.)

## Tunables (env / config.py)
```
EXPLORE_EPSILON=0.15          exploration rate of the bandit
DEFECT_PROMOTE_THRESHOLD=3    defect recurrences before it enters the failure log
DEFECT_WINDOW=20             how many recent gens to scan
HUMAN_WEIGHT=0.7             weight of your rating vs the auto critic
CRITIC_MODEL=claude-sonnet-5  override when a newer model ships
IMAGE_MODEL=google/nano-banana-2
```

## Honest limits
- The reward signal is the auto-critic + your ratings. With zero signal nothing improves.
- It does not fine-tune the image model; the leverage is prompt wording + input photos.
- The critic is a proxy — rate a sample by eye so the bandit optimises toward your taste.
