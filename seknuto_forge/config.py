"""Central configuration. Everything is env-driven so nothing sensitive is hardcoded.

The system runs out of the box with a local JSON store; point MONGO_URI at your
Atlas cluster to use the same MongoDB your SekTo backend already uses.
"""
from __future__ import annotations
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# --- API keys (set in .env or environment) ---
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# --- Storage ---
# If MONGO_URI is empty, we fall back to a local JSON file (data/store.json).
MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB = os.getenv("MONGO_DB", "seknuto_forge")
LOCAL_STORE = DATA_DIR / "store.json"

# --- Models ---
# Image model: your locked default (accepts real before/after/logo as references).
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "google/nano-banana-2")
# Text-only print fallback (no photo references): ideogram.
IMAGE_MODEL_TEXT = os.getenv("IMAGE_MODEL_TEXT", "ideogram-ai/ideogram-v2")

# Critic model (vision). See https://docs.claude.com/en/docs/about-claude/models
# for current IDs — override via env when Anthropic ships a newer one.
CRITIC_MODEL = os.getenv("CRITIC_MODEL", "claude-sonnet-5")

# --- Learning loop ---
# epsilon-greedy: chance of exploring a non-best variant to keep learning.
EXPLORE_EPSILON = float(os.getenv("EXPLORE_EPSILON", "0.15"))
# a defect seen this many times in the recent window auto-appends to failure_log.
DEFECT_PROMOTE_THRESHOLD = int(os.getenv("DEFECT_PROMOTE_THRESHOLD", "3"))
DEFECT_WINDOW = int(os.getenv("DEFECT_WINDOW", "20"))

# Human rating overrides the auto score when present, with this blend weight.
# final = HUMAN_WEIGHT*human + (1-HUMAN_WEIGHT)*auto   (auto used alone if no human)
HUMAN_WEIGHT = float(os.getenv("HUMAN_WEIGHT", "0.7"))

PATTERNS_SEED = DATA_DIR / "patterns.seed.json"
PATTERNS_LIVE = DATA_DIR / "patterns.json"  # mutable working copy the loop updates
