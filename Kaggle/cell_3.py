%%writefile api.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class EmbedRequest(BaseModel):
    texts: list[str]

class ChatRequest(BaseModel):
    prompt: str

@app.post("/embed")
async def generate_embeddings(req: EmbedRequest):
    embeddings = []
    for text in req.texts:
        res = requests.post("http://localhost:11434/api/embeddings", json={
            "model": "nomic-embed-text",
            "prompt": text
        })
        embeddings.append(res.json().get("embedding"))
    return {"embeddings": embeddings}

@app.post("/chat")
async def chat_with_ai(req: ChatRequest):
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3:8b",
        "prompt": req.prompt,
        "stream": False
    })
    return {"answer": res.json().get("response")}