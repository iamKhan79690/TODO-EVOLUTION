import os
import time
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from task_agent import task_agent

app = FastAPI(title="Taska Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()

runner = Runner(
    agent=task_agent,
    app_name="taska",
    session_service=session_service,
)

# Simple in-memory rate limiter: 20 requests per minute per user
_rate_limits: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 20
RATE_WINDOW = 60


def _check_rate_limit(user_id: str) -> bool:
    now = time.time()
    timestamps = _rate_limits[user_id]
    _rate_limits[user_id] = [t for t in timestamps if now - t < RATE_WINDOW]
    if len(_rate_limits[user_id]) >= RATE_LIMIT:
        return False
    _rate_limits[user_id].append(now)
    return True


class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: str = "default"

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[dict] = []


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not _check_rate_limit(req.user_id):
        return ChatResponse(reply="You're sending messages too quickly. Please wait a moment.", tool_calls=[])

    session = await session_service.get_session(
        app_name="taska",
        user_id=req.user_id,
        session_id=req.session_id,
    )
    if session is None:
        session = await session_service.create_session(
            app_name="taska",
            user_id=req.user_id,
            session_id=req.session_id,
            state={"user_id": req.user_id},
        )

    user_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=f"[user_id={req.user_id}] {req.message}")],
    )

    reply_parts = []
    tool_calls = []

    try:
        async for event in runner.run_async(
            user_id=req.user_id,
            session_id=req.session_id,
            new_message=user_message,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        reply_parts.append(part.text)
                    if part.function_call:
                        tool_calls.append({
                            "name": part.function_call.name,
                            "args": dict(part.function_call.args) if part.function_call.args else {},
                        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        err_str = str(e).lower()
        if "resource_exhausted" in err_str or "429" in err_str:
            return ChatResponse(
                reply="I'm temporarily unavailable due to API limits. Please try again in a minute.",
                tool_calls=[],
            )
        return ChatResponse(
            reply="Something went wrong on my end. Please try again shortly.",
            tool_calls=[],
        )

    reply = " ".join(reply_parts).strip() if reply_parts else "Done!"

    return ChatResponse(reply=reply, tool_calls=tool_calls)


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "taska"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
