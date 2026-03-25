from fastapi import FastAPI, Request, Depends, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import os
import json
from pathlib import Path

from state_manager import StateManager
from ai_service import generate_reply, SCENARIOS, analyze_message  # for potential debugging
from analytics_service import get_analytics

app = FastAPI()

import os
API_KEY = os.environ.get("APP_API_KEY")

def get_api_key(x_api_key: str = Header(None)):
    if API_KEY is None:
        return
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# Serve static assets from the 'static' folder
BASE = Path(__file__).parent
if not os.path.isdir(str(BASE / 'static')):
    # create folder if missing to keep project runnable in simple environments
    (BASE / 'static').mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(BASE / 'static')), name="static")

# Serve a minimal HTML interface from templates/index.html
@app.get("/")
async def index():
    html_path = BASE / "templates" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.post("/message")
async def message(req: Request, api_key: object = Depends(get_api_key)):
    data = await req.json()
    session_id = data.get("session_id") or "default"
    client_message = data.get("client_message", "")

    # Ensure session exists
    StateManager.ensure_session(session_id)
    mode = StateManager.get_mode()

    # Update history with client message pre-flight
    session = StateManager.get_session(session_id)
    history = session.get("history", [])
    # Normalize history format
    if not isinstance(history, list):
        history = []
    # Call offline/online engine to craft reply
    result = generate_reply(client_message, history, mode=mode)

    # Update history with the interaction
    new_history = history + [{"role": "client", "text": client_message}, {"role": "manager", "text": result.get("best_reply", "")}]
    StateManager.update_session(session_id, {"history": new_history})

    response = {
        "stage": result.get("stage"),
        "objection_type": result.get("objection_type"),
        "reply_options": result.get("reply_options"),
        "tactic": result.get("tactic"),
        "next_step": result.get("next_step"),
        "history": new_history,
    }
    return response


@app.post("/config")
async def set_config(req: Request, api_key: object = Depends(get_api_key)):
    data = await req.json()
    mode = data.get("mode", "OFFLINE").upper()
    StateManager.set_mode(mode)
    return {"mode": mode}


@app.get("/config")
async def get_config(api_key: object = Depends(get_api_key)):
    return {"mode": StateManager.get_mode()}


@app.get("/analytics")
async def analytics(req: Request):
    session_id = req.query_params.get("session_id") or "default"
    StateManager.ensure_session(session_id)
    sess = StateManager.get_session(session_id)
    history = sess.get("history", [])
    data = get_analytics(history)
    return data


if __name__ == "__main__":
    # Run with: python main.py
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
