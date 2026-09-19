# ==============================================================================
# PRAVAH AI - FASTAPI WEB SERVER
# File: main.py
# Description: Serves static web assets (HTML/CSS/JS) and handles AI chat routing.
# ==============================================================================

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from knowledge_base import resolve_location_context
import uvicorn

# Internal AI Engine Module
from ai_engine import process_conversational_query

app = FastAPI(title="Pravah AI Risk Intelligence Platform")


# ==============================================================================
# 1. STATIC FILE MOUNTING
# ==============================================================================
# Mounts root directory under '/static' so HTML can read style.css & script.js
app.mount("/static", StaticFiles(directory="."), name="static")


# ==============================================================================
# 2. DATA MODELS FOR API
# ==============================================================================
class QueryRequest(BaseModel):
    message: str
    history: list
    language: str


# ==============================================================================
# 3. APPLICATION ROUTES & ENDPOINTS
# ==============================================================================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the primary HTML UI dashboard directly from root directory."""
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/chat")
async def chat_endpoint(req: QueryRequest):
    # 1. Resolve location status
    loc_context = resolve_location_context(req.message, req.history)
    
    # 2. Check if the user is just saying hello
    if loc_context.get("status") == "greeting":
        return {"response": "Hello! I am PRAVAH, your disaster risk AI assistant for Nepal. How can I assist you today?"}

    # 3. Otherwise, process query normally
    bot_response = process_conversational_query(req.message, req.history, req.language)
    return {"response": bot_response}

# ==============================================================================
# 4. SERVER ENTRYPOINT
# ==============================================================================

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=7860, reload=True)