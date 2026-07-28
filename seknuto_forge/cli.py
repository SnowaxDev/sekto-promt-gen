"""Tiny CLI so you can drive the loop from a terminal.

  python -m seknuto_forge.cli prompt --format DL --mode A_transformace
  python -m seknuto_forge.cli generate --format DL --mode A_transformace \
        --img before.jpg --img after.jpg --img logo.png
  python -m seknuto_forge.cli rate <generation_id> 85
  python -m seknuto_forge.cli leaderboard
"""
from __future__ import annotations
import argparse, json
from . import chassis, learn


def _vars(a) -> dict:
    v = {"format": a.format, "mode": a.mode}
    if a.headline: v["service_headline"] = a.headline
    if a.location: v["location"] = a.location
    return v


def main(argv=None):
    p = argparse.ArgumentParser(prog="seknuto_forge")
    sub = p.add_subparsers(dest="cmd", required=True)

    for name in ("prompt", "generate"):
        s = sub.add_parser(name)
        s.add_argument("--format", default="DL")
        s.add_argument("--mode", default="B_sluzby")
        s.add_argument("--headline", default=None)
        s.add_argument("--location", default=None)
        if name == "generate":
            s.add_argument("--img", action="append", default=[], help="image URL/path (repeat)")
            s.add_argument("--no-eval", action="store_true")

    r = sub.add_parser("rate"); r.add_argument("id"); r.add_argument("score", type=float)
    sub.add_parser("leaderboard")

    a = p.parse_args(argv)

    if a.cmd == "prompt":
        print(chassis.build_prompt(_vars(a))["prompt"])
    elif a.cmd == "generate":
        rec = learn.run_once(_vars(a), a.img or None, auto_evaluate=not a.no_eval)
        print(json.dumps(rec, ensure_ascii=False, indent=2))
    elif a.cmd == "rate":
        print(json.dumps(learn.rate(a.id, a.score), ensure_ascii=False, indent=2))
    elif a.cmd == "leaderboard":
        print(json.dumps(learn.leaderboard(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
