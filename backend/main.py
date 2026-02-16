from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import json

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

class RoadmapRequest(BaseModel):
    level: str
    position: str

@app.post("/generate-roadmap")
async def generate_roadmap(request: RoadmapRequest):
    if not HUGGINGFACE_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    prompt = f"""Створи детальний roadmap для {request.level} {request.position} розробника українською мовою.

Формат відповіді - ТІЛЬКИ JSON (без пояснень, без markdown):
{{{{
  "title": "Roadmap для {request.level} {request.position}",
  "steps": [
    {{{{
      "month": 1,
      "title": "Назва етапу",
      "description": "Опис що вивчати",
      "skills": ["навичка1", "навичка2"],
      "resources": ["ресурс1", "ресурс2"]
    }}}}
  ]
}}}}

Зроби 6 етапів (по місяцях)."""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://router.huggingface.co/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/Mistral-7B-Instruct-v0.2",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail=f"HuggingFace API error: {response.text}")
            
            result = response.json()
            
            # Парсинг відповіді
            generated_text = result["choices"][0]["message"]["content"]
            
            # Парсинг JSON
            try:
                roadmap_data = json.loads(generated_text)
                return roadmap_data
            except json.JSONDecodeError:
                # Якщо не JSON, створюємо базовий roadmap
                return {
                    "title": f"Roadmap для {request.level} {request.position}",
                    "steps": [
                        {
                            "month": 1,
                            "title": "Основи",
                            "description": generated_text[:200],
                            "skills": ["Базові навички"],
                            "resources": ["Документація"]
                        }
                    ]
                }
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok", "message": "IT Career Compass API"}