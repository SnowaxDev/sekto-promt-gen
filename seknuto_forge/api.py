"""FastAPI surface. Drops into your SekTo backend.

  POST /prompt        -> assemble a prompt without generating (preview / cost 0)
  POST /generate      -> build + generate (+ auto-critique) + store
  POST /rate          -> attach human 0-100 score to a generation
  GET  /best          -> best exemplar for a format+mode (warm start)
  GET  /leaderboard   -> which prompt variants are winning
  GET  /generations   -> raw log

Run:  uvicorn seknuto_forge.api:app --reload
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from . import chassis, learn, store, knowledge, intent, tasks, blocks, assets, config

app = FastAPI(title="SeknuTo Forge", version="1.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# local asset library (outputs/ on the user's PC) served for the Soubory panel
config.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(config.OUTPUTS_DIR)), name="outputs")

_UI = Path(__file__).resolve().parent.parent / "webui" / "index.html"


@app.get("/")
def home():
    # no-store so the browser never shows a stale cached dashboard after a git pull
    return FileResponse(_UI, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


class Variables(BaseModel):
    # extra="allow" lets Dark Emerald copy fields (ladder, chips, eyebrow, status,
    # proof, body, micro, cta, chip_filled_index) pass through without listing each.
    model_config = ConfigDict(extra="allow")
    format: str = "DL"
    mode: str = "B_sluzby"
    service_headline: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    uses_photos: Optional[bool] = None
    style_ref: Optional[bool] = None  # last image is a style reference to match


class GenerateReq(BaseModel):
    variables: Variables
    image_urls: list[str] = []
    auto_evaluate: bool = True
    prompt_override: Optional[str] = None   # hand-edited prompt from the workspace


class VariantReq(BaseModel):
    action: str            # "add" | "edit" | "delete"
    slot: str
    id: Optional[str] = None
    text: Optional[str] = None


class RefineReq(BaseModel):
    variables: Variables
    image_urls: list[str] = []
    max_iters: Optional[int] = None      # hard-capped in learn.refine
    target: Optional[float] = None       # stop early at this score


class SeriesReq(BaseModel):
    variables: Variables
    image_urls: list[str] = []
    count: int = 3
    auto_evaluate: bool = True


class RateReq(BaseModel):
    generation_id: str
    human_score: float  # 0-100


def _vars(v: Variables) -> dict[str, Any]:
    return {k: val for k, val in v.model_dump().items() if val is not None}


class BriefReq(BaseModel):
    brief: str
    action: str = "plan"           # "plan" (cost 0), "generate", or "series"
    image_urls: list[str] = []
    auto_evaluate: bool = True


@app.post("/prompt")
def preview_prompt(v: Variables):
    return chassis.build_prompt(_vars(v))


@app.post("/brief")
def brief(req: BriefReq):
    """Free-text brief -> brand-locked plan (+ prompt preview). Optionally generate / make a series."""
    try:
        plan = intent.interpret(req.brief)
        built = chassis.build_prompt(plan)
        out = {"variables": plan, "prompt": built["prompt"], "aspect": built["aspect"],
               "model_hint": built["model_hint"], "show_qr": built["show_qr"]}
        if req.action == "series" or (req.action == "generate" and plan.get("series")):
            out["series"] = learn.series(plan, req.image_urls or None, plan.get("count", 3),
                                         None, req.auto_evaluate)
        elif req.action == "generate":
            out["generation"] = learn.run_once(plan, req.image_urls or None, req.auto_evaluate)
        return out
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/generate")
def generate(req: GenerateReq):
    try:
        return learn.run_once(_vars(req.variables), req.image_urls or None,
                              req.auto_evaluate, req.prompt_override)
    except Exception as e:  # surface Replicate/Anthropic errors cleanly
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/refine")
def refine(req: RefineReq):
    """Auto-improve loop: generate -> critique -> fix prompt -> regenerate, keep best."""
    try:
        return learn.refine(_vars(req.variables), req.image_urls or None,
                            req.max_iters, req.target)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/series")
def series(req: SeriesReq):
    """Generate a cohesive, connected content set (e.g. an IG carousel), one consistent style."""
    try:
        return learn.series(_vars(req.variables), req.image_urls or None, req.count, None, req.auto_evaluate)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/rate")
def rate(req: RateReq):
    try:
        return learn.rate(req.generation_id, req.human_score)
    except KeyError:
        raise HTTPException(status_code=404, detail="generation not found")


@app.get("/best")
def best(format: str = "DL", mode: str = "B_sluzby"):
    return learn.retrieve({"format": format, "mode": mode}) or {}


@app.get("/leaderboard")
def leaderboard():
    return learn.leaderboard()


@app.get("/generations")
def generations():
    return store.get_store().all()


@app.get("/knowledge")
def get_knowledge():
    p = knowledge.load_patterns()
    return {"failure_log": p["failure_log"], "base_negative": p["base_negative"]}


@app.get("/patterns")
def get_patterns():
    """Full learnable state for the workspace knowledge editor."""
    p = knowledge.load_patterns()
    return {"variants": p["variants"], "banks": knowledge.load_design().get("banks", {}),
            "failure_log": p["failure_log"], "base_negative": p["base_negative"],
            "locked_strings": p["locked_strings"], "colors": p["colors"]}


@app.post("/variant")
def edit_variant(req: VariantReq):
    """Live-edit the knowledge DB: add / edit / delete a prompt variant, persisted to disk."""
    p = knowledge.load_patterns()
    if req.action == "add":
        vid = knowledge.add_variant(p, req.slot, req.text or "", cap=False)
        ok = vid is not None
    elif req.action == "edit":
        ok = knowledge.edit_variant(p, req.slot, req.id or "", req.text or "")
    elif req.action == "delete":
        ok = knowledge.delete_variant(p, req.slot, req.id or "")
    else:
        raise HTTPException(status_code=400, detail="action must be add|edit|delete")
    if not ok:
        raise HTTPException(status_code=400, detail="edit rejected (missing/duplicate/last-in-slot)")
    knowledge.save_patterns(p)
    return {"ok": True, "slot": req.slot, "variants": p["variants"].get(req.slot, [])}


@app.get("/usage")
def usage():
    return learn.usage_stats()


class TaskReq(BaseModel):
    kind: str                       # generate | refine | series
    variables: dict = {}
    image_urls: list[str] = []
    count: int = 3
    auto_evaluate: bool = True
    prompt_override: Optional[str] = None


class BlockReq(BaseModel):
    name: str
    kind: str                       # generate | refine | series
    variables: dict = {}
    image_urls: list[str] = []
    count: int = 3
    prompt_override: Optional[str] = None


@app.get("/files")
def files():
    """Everything saved locally in outputs/ (image + metadata), newest first."""
    return assets.list_files()


@app.post("/task")
def create_task(req: TaskReq):
    """Queue a job; the worker runs jobs sequentially. Watch progress via GET /tasks."""
    try:
        return tasks.create(req.kind, {"variables": req.variables, "image_urls": req.image_urls,
                                       "count": req.count, "auto_evaluate": req.auto_evaluate,
                                       "prompt_override": req.prompt_override})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tasks")
def get_tasks():
    return tasks.list_tasks()


@app.get("/blocks")
def get_blocks():
    return blocks.list_blocks()


@app.post("/blocks")
def add_block(req: BlockReq):
    try:
        return blocks.add(req.name, req.kind, {"variables": req.variables,
                                               "image_urls": req.image_urls, "count": req.count,
                                               "prompt_override": req.prompt_override})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/blocks/{bid}")
def del_block(bid: str):
    if not blocks.delete(bid):
        raise HTTPException(status_code=404, detail="block not found")
    return {"ok": True}


@app.post("/blocks/{bid}/run")
def run_block(bid: str):
    t = blocks.run(bid)
    if not t:
        raise HTTPException(status_code=404, detail="block not found")
    return t
