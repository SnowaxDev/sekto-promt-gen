"""The closed loop. Ties chassis + generate + evaluate + knowledge + store together.

run_once():   build prompt -> generate -> critique -> store -> credit variants
rate():       attach a human score, re-blend, re-credit
retrieve():   warm-start a new request from the best past generation like it
leaderboard(): which prompt variants are winning
"""
from __future__ import annotations
import uuid
from typing import Any
from . import chassis, generate, evaluate, knowledge, store, config


def run_once(variables: dict[str, Any], image_urls: list[str] | None = None,
             auto_evaluate: bool = True) -> dict[str, Any]:
    patterns = knowledge.load_patterns()
    built = chassis.build_prompt(variables, patterns)

    gen = generate.generate(built, image_urls=image_urls)

    rec = store.new_generation(
        format=variables.get("format"), mode=variables.get("mode"),
        variables=variables, prompt=built["prompt"],
        chosen_variant_ids=built["chosen_variant_ids"],
        input_images=image_urls or [], output_url=gen["output_url"],
        model=gen["model"], params={k: v for k, v in gen["params"].items() if k != "prompt"},
    )

    if auto_evaluate:
        crit = evaluate.critique(gen["output_url"], mode=variables.get("mode", "B_sluzby"))
        rec.update(auto_score=crit["auto_score"], auto_checks=crit["checks"],
                   auto_defects=crit["defects"], hard_fail=crit.get("hard_fail", False))
        rec["final_score"] = evaluate.blend_final(crit["auto_score"], None)

    db = store.get_store()
    _id = db.insert(rec)

    # credit the variants with whatever score we have so far
    if rec.get("final_score") is not None:
        knowledge.credit_variants(patterns, built["chosen_variant_ids"], rec["final_score"])
        _auto_promote(patterns, db)
        knowledge.save_patterns(patterns)

    rec["_id"] = _id
    return rec


def refine(variables: dict[str, Any], image_urls: list[str] | None = None,
           max_iters: int | None = None, target: float | None = None) -> dict[str, Any]:
    """Auto-improve loop: generate -> critique -> Claude fixes the prompt to kill the
    reported defects (brand-safely) -> regenerate. Keeps the best result. Stops when the
    score hits `target` or after `max_iters` renders (hard-capped — each render costs money).

    Every iteration is stored and credits the variant bandit, so the library keeps learning
    across runs; the best result is what warm-start (retrieve) will reuse next time.
    Returns {best, history, iterations}.
    """
    max_iters = config.REFINE_MAX_ITERS if max_iters is None else int(max_iters)
    max_iters = max(1, min(max_iters, 8))  # never runaway on cost
    target = config.REFINE_TARGET_SCORE if target is None else float(target)

    patterns = knowledge.load_patterns()
    db = store.get_store()
    history: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    prompt_override: str | None = None

    for i in range(max_iters):
        built = chassis.build_prompt(variables, patterns)
        if prompt_override:
            built["prompt"] = prompt_override

        gen = generate.generate(built, image_urls=image_urls)
        rec = store.new_generation(
            format=variables.get("format"), mode=variables.get("mode"),
            variables=variables, prompt=built["prompt"],
            chosen_variant_ids=built["chosen_variant_ids"],
            input_images=image_urls or [], output_url=gen["output_url"],
            model=gen["model"], params={k: v for k, v in gen["params"].items() if k != "prompt"},
            refine_iter=i + 1,
        )

        crit = evaluate.critique(gen["output_url"], mode=variables.get("mode", "B_sluzby"))
        hard = crit.get("hard_fail", False)
        rec.update(auto_score=crit["auto_score"], auto_checks=crit["checks"],
                   auto_defects=crit["defects"], hard_fail=hard)
        rec["final_score"] = evaluate.blend_final(crit["auto_score"], None)
        rec["is_baseline"] = (rec["final_score"] is not None and rec["final_score"] >= 92 and not hard)

        _id = db.insert(rec)
        rec["_id"] = _id
        knowledge.credit_variants(patterns, built["chosen_variant_ids"], rec["final_score"])
        _auto_promote(patterns, db)
        knowledge.save_patterns(patterns)

        score = rec["final_score"] or 0.0
        history.append({"iter": i + 1, "id": _id, "score": round(score, 1),
                        "hard_fail": hard, "output_url": gen["output_url"], "defects": crit["defects"]})
        # a passing (non-hard-fail) result always beats a hard-failed one, then by score
        def _rank(r): return (0 if r.get("hard_fail") else 1, r.get("final_score") or -1)
        if best is None or _rank(rec) > _rank(best):
            best = rec

        if not hard and score >= target:
            break  # good enough — stop spending
        if i < max_iters - 1:
            # §13.3 action ladder: hard fail or <65 -> throw away this wording, let the
            # bandit pick a fresh variant vector next pass; 65-79 -> one targeted prompt fix.
            if hard or score < 65:
                prompt_override = None
            else:
                prompt_override = evaluate.improve_prompt(
                    built["prompt"], crit["checks"], crit["defects"], patterns)

    discovered = _maybe_discover_style(variables, patterns, best)
    if discovered:
        knowledge.save_patterns(patterns)
    return {"best": best, "history": history, "iterations": len(history), "discovered": discovered}


def _maybe_discover_style(variables, patterns, best) -> dict[str, Any] | None:
    """After a good Dark Emerald run, let Claude invent a NEW value for the least-explored
    style axis and add it to the pool — the system discovers fresh styles, not just the seeds."""
    if not config.DE_DISCOVER or variables.get("mode") != "dark_emerald" or not best:
        return None
    if best.get("hard_fail") or (best.get("final_score") or 0) < config.DE_DISCOVER_MIN_SCORE:
        return None
    de_slots = [s for s in patterns["variants"] if s.startswith("de_")]
    if not de_slots:
        return None
    # least-explored axis with room to grow
    open_slots = [s for s in de_slots if len(patterns["variants"][s]) < config.DE_MAX_VARIANTS_PER_AXIS]
    if not open_slots:
        return None
    axis = min(open_slots, key=lambda s: sum(v["uses"] for v in patterns["variants"][s]))
    existing = [v["text"] for v in patterns["variants"][axis]]
    text = evaluate.propose_style_variant(axis, existing)
    if not text:
        return None
    vid = knowledge.add_variant(patterns, axis, text)
    return {"axis": axis, "id": vid, "text": text} if vid else None


def _default_series_plan(design: dict[str, Any], count: int) -> list[dict[str, Any]]:
    """A cohesive multi-post carousel plan: same style, a narrative role per slide."""
    B = design["banks"]
    lad = B["ladder"]
    roles = [
        {"series_role": "Hook — upoutání", "ladder": lad[0]},
        {"series_role": "Služby — co děláme", "ladder": lad[1 % len(lad)], "chips": B["chips"][:3]},
        {"series_role": "Důkaz — proč my", "ladder": lad[2 % len(lad)], "proof": B["proof"][0]},
        {"series_role": "Výzva — ozvi se", "ladder": lad[3 % len(lad)],
         "cta": B["cta"][0], "micro": B["micro"][0]},
    ]
    plan = []
    for i in range(count):
        r = dict(roles[i % len(roles)])
        r["service_headline"] = " ".join(r["ladder"])   # so A/B print series vary too
        plan.append(r)
    return plan


def series(variables: dict[str, Any], image_urls: list[str] | None = None, count: int = 3,
           plan: list[dict[str, Any]] | None = None, auto_evaluate: bool = True) -> dict[str, Any]:
    """Generate a cohesive, connected content set (e.g. an IG carousel). The whole series locks
    onto ONE style vector so every piece looks consistent; only the copy/role changes per piece."""
    count = max(1, min(int(count), 8))
    patterns = knowledge.load_patterns()
    design = knowledge.load_design()
    db = store.get_store()
    mode = variables.get("mode", "dark_emerald")

    group = "de" if mode == "dark_emerald" else "ab"
    fixed = knowledge.best_vector(patterns, group)          # the shared, proven style
    plan = (plan or _default_series_plan(design, count))[:count]
    series_id = uuid.uuid4().hex[:12]
    slides: list[dict[str, Any]] = []

    for idx, override in enumerate(plan):
        v = {**variables, **override, "_fixed_axes": fixed}
        built = chassis.build_prompt(v, patterns)
        gen = generate.generate(built, image_urls=image_urls)
        rec = store.new_generation(
            format=variables.get("format"), mode=mode, variables=v, prompt=built["prompt"],
            chosen_variant_ids=built["chosen_variant_ids"], input_images=image_urls or [],
            output_url=gen["output_url"], model=gen["model"],
            params={k: val for k, val in gen["params"].items() if k != "prompt"},
            series_id=series_id, slide_index=idx + 1, series_role=override.get("series_role"),
        )
        if auto_evaluate:
            crit = evaluate.critique(gen["output_url"], mode=mode)
            rec.update(auto_score=crit["auto_score"], auto_checks=crit["checks"],
                       auto_defects=crit["defects"], hard_fail=crit.get("hard_fail", False))
            rec["final_score"] = evaluate.blend_final(crit["auto_score"], None)
        _id = db.insert(rec)
        rec["_id"] = _id
        if rec.get("final_score") is not None:
            knowledge.credit_variants(patterns, built["chosen_variant_ids"], rec["final_score"])
        slides.append({"slide": idx + 1, "role": override.get("series_role"), "id": _id,
                       "output_url": gen["output_url"], "score": rec.get("final_score"),
                       "hard_fail": rec.get("hard_fail", False), "prompt": built["prompt"]})

    _auto_promote(patterns, db)
    knowledge.save_patterns(patterns)
    return {"series_id": series_id, "count": len(slides), "style": fixed, "slides": slides}


def rate(generation_id: str, human_score: float) -> dict[str, Any]:
    """Ground-truth a generation. Re-blends final score and re-credits variants
    (removing the earlier auto-only credit, adding the blended one)."""
    db = store.get_store()
    rec = db.get(generation_id)
    if not rec:
        raise KeyError(generation_id)
    patterns = knowledge.load_patterns()

    old = rec.get("final_score")
    new = evaluate.blend_final(rec.get("auto_score"), human_score)

    # adjust variant credit by the delta so re-rating stays consistent
    if old is not None:
        _adjust_variant_credit(patterns, rec["chosen_variant_ids"], -old, -1)
    _adjust_variant_credit(patterns, rec["chosen_variant_ids"], new, +1)

    db.update(generation_id, {"human_score": human_score, "final_score": new})
    _auto_promote(patterns, db)
    knowledge.save_patterns(patterns)
    rec.update(human_score=human_score, final_score=new)
    return rec


def _adjust_variant_credit(patterns, chosen_ids, score_delta, use_delta):
    for slot, vid in chosen_ids.items():
        for v in patterns["variants"].get(slot, []):
            if v["id"] == vid:
                v["uses"] += use_delta
                v["score_sum"] += score_delta
                break


def _auto_promote(patterns, db):
    recent = sorted(db.all(), key=lambda g: g.get("ts", 0))[-config.DEFECT_WINDOW:]
    defects = [d for g in recent for d in g.get("auto_defects", [])]
    knowledge.maybe_promote_defect(patterns, defects)


def retrieve(variables: dict[str, Any]) -> dict[str, Any] | None:
    """Best past generation with the same format+mode+service — 'lock & reuse' automated."""
    db = store.get_store()
    cand = [g for g in db.all()
            if g.get("format") == variables.get("format")
            and g.get("mode") == variables.get("mode")
            and g.get("final_score") is not None]
    if not cand:
        return None
    return max(cand, key=lambda g: g["final_score"])


def leaderboard() -> dict[str, list[dict]]:
    """Ranked variants per slot — shows what the loop has learned."""
    patterns = knowledge.load_patterns()
    out: dict[str, list[dict]] = {}
    for slot, variants in patterns["variants"].items():
        ranked = sorted(variants, key=knowledge.variant_mean, reverse=True)
        out[slot] = [{"id": v["id"], "mean": round(knowledge.variant_mean(v), 1),
                      "uses": v["uses"]} for v in ranked]
    return out
