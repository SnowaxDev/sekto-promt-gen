# SeknuTo Forge — Workspace (React + shadcn-style)

A richer "working space" front-end for the SeknuTo Forge pipeline: create from a brief,
generate / refine / series, **edit the live knowledge DB**, watch **usage & credits**, and a
**live activity** feed. Built with Vite + React + TypeScript + Tailwind + shadcn-style components.

> The original zero-build dashboard (`../webui/index.html`) still works and is what `make run`
> serves. This app is an optional richer workspace that needs Node.

## Run

```bash
# 1) start the backend (from the repo root, in another terminal)
python -m uvicorn seknuto_forge.api:app --host 127.0.0.1 --port 8000

# 2) start the workspace
cd webui-app
npm install
npm run dev            # -> http://localhost:5173
```

The dev server proxies all JSON endpoints to the backend on `127.0.0.1:8000`, so there are no
CORS issues. To point elsewhere, build with `VITE_API_BASE=https://host npm run build`.

## Build (static)

```bash
npm run build          # outputs to dist/
npm run preview
```

## Panels

- **Studio** — brief → plan, format/mode/ladder/chips, upload refs, editable prompt, Generate /
  Refine / Series, result with rubric checks + hard-fail/baseline badges + refine history.
- **Knowledge** — the live editable DB: every prompt variant with its mean score + uses; edit /
  add / delete (persists to `data/patterns.json`); failure log, negative prompt, copy banks.
- **Usage** — generations, ratings, average score, estimated cost, score trend, per mode/format.
- **Aktivita** — live feed (polls every 4 s) of recent generations, scores, series, hard fails.
