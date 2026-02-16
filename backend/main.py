import json
import os
import re

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="IT Career Compass API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class RoadmapRequest(BaseModel):
    level: str
    position: str


class RoadmapResponse(BaseModel):
    skills: list[str]
    roadmap: dict[str, list[str]]
    checklist: list[str]


PROMPT_TEMPLATE = """Створи детальний roadmap для {level} {position} в українському IT.

Вимоги:
- Реалістичні навички за стандартами DOU/Djinni
- Практичні, конкретні дії
- План підготовки на 3-4 тижні
- Кожен тиждень — 4-6 конкретних задач
- Checklist — 8-12 пунктів готовності

Дай відповідь ТІЛЬКИ у форматі JSON (без markdown, без ```):
{{
  "skills": ["навичка1", "навичка2", ...],
  "roadmap": {{
    "week1": ["задача1", "задача2", ...],
    "week2": ["задача1", "задача2", ...],
    "week3": ["задача1", "задача2", ...],
    "week4": ["задача1", "задача2", ...]
  }},
  "checklist": ["пункт1", "пункт2", ...]
}}"""


@app.post("/generate-roadmap", response_model=RoadmapResponse)
async def generate_roadmap(req: RoadmapRequest):
    if not req.position.strip():
        raise HTTPException(status_code=400, detail="Position is required")

    if req.level not in ("Trainee", "Junior", "Middle", "Senior"):
        raise HTTPException(status_code=400, detail="Invalid level")

    prompt = PROMPT_TEMPLATE.format(level=req.level, position=req.position.strip())

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "stepfun/step-3.5-flash:free",
                    "messages": [{"role": "user", "content": prompt}],
                },
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"OpenRouter error: {response.text}",
            )

        result = response.json()
        raw = result["choices"][0]["message"]["content"].strip()

        # strip DeepSeek <think>...</think> blocks
        raw = re.sub(r"<think>[\s\S]*?</think>", "", raw).strip()

        # strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        data = json.loads(raw)
        return RoadmapResponse(
            skills=data["skills"],
            roadmap=data["roadmap"],
            checklist=data["checklist"],
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="Failed to parse AI response")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API error: {e}")


@app.get("/health")
async def health():
    return {"status": "ok"}
