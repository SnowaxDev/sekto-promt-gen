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
from pydantic import BaseModel
from . import chassis, learn, store, knowledge

app = FastAPI(title="SeknuTo Forge", version="1.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_UI = Path(__file__).resolve().parent.parent / "webui" / "index.html"


@app.get("/")
def home():
    return FileResponse(_UI)


class Variables(BaseModel):
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


class RefineReq(BaseModel):
    variables: Variables
    image_urls: list[str] = []
    max_iters: Optional[int] = None      # hard-capped in learn.refine
    target: Optional[float] = None       # stop early at this score


class RateReq(BaseModel):
    generation_id: str
    human_score: float  # 0-100


def _vars(v: Variables) -> dict[str, Any]:
    return {k: val for k, val in v.model_dump().items() if val is not None}


@app.post("/prompt")
def preview_prompt(v: Variables):
    return chassis.build_prompt(_vars(v))


@app.post("/generate")
def generate(req: GenerateReq):
    try:
        return learn.run_once(_vars(req.variables), req.image_urls or None, req.auto_evaluate)
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
