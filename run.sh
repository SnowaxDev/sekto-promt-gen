#!/usr/bin/env bash
set -e
[ -f .env ] && export $(grep -v '^#' .env | xargs) || true
python -m pip install -r requirements.txt
echo "SeknuTo Forge -> http://127.0.0.1:8000"
uvicorn seknuto_forge.api:app --host 127.0.0.1 --port 8000
