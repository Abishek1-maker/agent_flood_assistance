from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from ai_engine import process_conversational_query

app = FastAPI()

class QueryRequest(BaseModel):
    message: str
    history: list
    language: str

@app.post("/api/chat")
async def chat_endpoint(req: QueryRequest):
    bot_response = process_conversational_query(req.message, req.history, req.language)
    return {"response": bot_response}

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=7860, reload=True)