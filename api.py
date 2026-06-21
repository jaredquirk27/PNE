from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import initialize_database
from prompt_builder import build_ai_prompt
from llm_provider import generate_response
from chat import persist_chat_exchange

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn, cursor = initialize_database()


class ChatRequest(BaseModel):
    character: str
    message: str


@app.get("/")
def root():

    return {
        "status": "online",
        "engine": "Persistent Narrative Engine"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    prompt = build_ai_prompt(
        cursor,
        request.character,
        request.message
    )

    response = generate_response(
        prompt
    )

    found_memories = persist_chat_exchange(
        cursor,
        request.character,
        request.message,
        response,
        1
    )

    conn.commit()

    return {
        "response": response,
        "memory_candidates": found_memories
    }
