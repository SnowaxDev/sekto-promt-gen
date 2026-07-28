"""Image + evaluation database. Uses MongoDB when MONGO_URI is set (same cluster as
your SekTo backend), otherwise a local JSON file so the whole system runs with zero infra.

A 'generation' record is the unit of learning:
  {_id, ts, format, mode, variables, model, params, prompt, chosen_variant_ids,
   input_images, output_url, auto_score, auto_checks, auto_defects,
   human_score, final_score}
"""
from __future__ import annotations
import json, time, uuid
from typing import Any
from . import config


class _JSONStore:
    """Dependency-free fallback store."""
    def __init__(self, path):
        self.path = path
        if not self.path.exists():
            self._write({"generations": []})

    def _read(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def insert(self, doc: dict) -> str:
        data = self._read()
        doc.setdefault("_id", uuid.uuid4().hex)
        data["generations"].append(doc)
        self._write(data)
        return doc["_id"]

    def update(self, _id: str, fields: dict) -> None:
        data = self._read()
        for g in data["generations"]:
            if g["_id"] == _id:
                g.update(fields)
        self._write(data)

    def get(self, _id: str) -> dict | None:
        for g in self._read()["generations"]:
            if g["_id"] == _id:
                return g
        return None

    def all(self) -> list[dict]:
        return self._read()["generations"]


class _MongoStore:
    def __init__(self, uri: str, dbname: str):
        from pymongo import MongoClient  # imported lazily
        self.col = MongoClient(uri)[dbname]["generations"]

    def insert(self, doc: dict) -> str:
        doc.setdefault("_id", uuid.uuid4().hex)
        self.col.insert_one(doc)
        return doc["_id"]

    def update(self, _id: str, fields: dict) -> None:
        self.col.update_one({"_id": _id}, {"$set": fields})

    def get(self, _id: str) -> dict | None:
        return self.col.find_one({"_id": _id})

    def all(self) -> list[dict]:
        return list(self.col.find({}))


def get_store():
    if config.MONGO_URI:
        return _MongoStore(config.MONGO_URI, config.MONGO_DB)
    return _JSONStore(config.LOCAL_STORE)


def new_generation(**fields) -> dict:
    base = {"ts": time.time(), "auto_score": None, "human_score": None, "final_score": None}
    base.update(fields)
    return base
