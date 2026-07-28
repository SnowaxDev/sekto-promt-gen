"""The closed loop. Ties chassis + generate + evaluate + knowledge + store together.

run_once():   build prompt -> generate -> critique -> store -> credit variants
rate():       attach a human score, re-blend, re-credit
retrieve():   warm-start a new request from the best past generation like it
leaderboard(): which prompt variants are winning
"""
from __future__ import annotations
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
        crit = evaluate.critique(gen["output_url"])
        rec.update(auto_score=crit["auto_score"], auto_checks=crit["checks"],
                   auto_defects=crit["defects"])
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
