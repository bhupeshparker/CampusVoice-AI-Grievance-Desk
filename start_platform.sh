#!/bin/bash
echo "====================================================================="
echo " CampusVoice - AI Campus Incident Intelligence Platform"
echo "====================================================================="

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ ! -d ".venv" ]; then
    echo "[*] Initializing virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r backend/requirements.txt
else
    source .venv/bin/activate
fi

echo "[*] Starting CampusVoice on http://127.0.0.1:8000 ..."
python3 -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
