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
{{
  "title": "Roadmap для {request.level} {request.position}",
  "steps": [
    {{
      "month": 1,
      "title": "Назва етапу",
      "description": "Опис що вивчати",
      "skills": ["навичка1", "навичка2"],
      "resources": ["ресурс1", "ресурс2"]
    }}
  ]
}}

Зроби 6 етапів (по місяцях)."""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                headers={
                    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 2000,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail=f"HuggingFace API error: {response.text}")
            
            result = response.json()
            
            # HuggingFace повертає список
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            else:
                generated_text = str(result)
            
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