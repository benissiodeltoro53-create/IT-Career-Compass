from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import json
import re

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
    
    prompt = f"""Create a detailed 6-month roadmap for {request.level} {request.position} developer in Ukrainian.

Response format - ONLY valid JSON (no explanations, no markdown):
{{
  "title": "Roadmap для {request.level} {request.position}",
  "steps": [
    {{
      "month": 1,
      "title": "Назва етапу",
      "description": "Опис що вивчати цього місяця",
      "skills": ["навичка1", "навичка2", "навичка3"],
      "resources": ["ресурс1", "ресурс2"]
    }},
    {{
      "month": 2,
      "title": "Назва етапу",
      "description": "Опис що вивчати цього місяця",
      "skills": ["навичка1", "навичка2"],
      "resources": ["ресурс1", "ресурс2"]
    }}
  ]
}}

Generate 6 steps (months 1-6). Return ONLY the JSON, nothing else."""

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
            generated_text = result["choices"][0]["message"]["content"]
            
            # Видалити markdown
            generated_text = re.sub(r'```json\s*', '', generated_text)
            generated_text = re.sub(r'```\s*', '', generated_text)
            generated_text = generated_text.strip()
            
            # Парсинг JSON
            try:
                roadmap_data = json.loads(generated_text)
                
                # Валідація структури
                if not isinstance(roadmap_data.get("steps"), list):
                    raise ValueError("Invalid steps format")
                
                # Переконатись що є хоча б 1 крок
                if len(roadmap_data["steps"]) == 0:
                    raise ValueError("No steps generated")
                
                return roadmap_data
                
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback - створити базовий roadmap
                return {
                    "title": f"Roadmap для {request.level} {request.position}",
                    "steps": [
                        {
                            "month": 1,
                            "title": "Основи програмування",
                            "description": "Вивчення базових концепцій та синтаксису мови програмування",
                            "skills": ["Синтаксис мови", "Змінні та типи даних", "Умови та цикли"],
                            "resources": ["Офіційна документація", "Онлайн курси"]
                        },
                        {
                            "month": 2,
                            "title": "Структури даних",
                            "description": "Вивчення основних структур даних та алгоритмів",
                            "skills": ["Масиви", "Об'єкти", "Базові алгоритми"],
                            "resources": ["LeetCode", "Книги з алгоритмів"]
                        },
                        {
                            "month": 3,
                            "title": "Фреймворки",
                            "description": "Освоєння популярних фреймворків для розробки",
                            "skills": ["React/Vue/Angular", "State management", "Routing"],
                            "resources": ["Офіційна документація фреймворку"]
                        },
                        {
                            "month": 4,
                            "title": "Бекенд основи",
                            "description": "Вивчення серверної розробки та баз даних",
                            "skills": ["REST API", "Бази даних", "Аутентифікація"],
                            "resources": ["Node.js/Python документація"]
                        },
                        {
                            "month": 5,
                            "title": "Тестування та DevOps",
                            "description": "Автоматизація тестування та deployment",
                            "skills": ["Unit тести", "Git", "CI/CD"],
                            "resources": ["Jest/Pytest документація"]
                        },
                        {
                            "month": 6,
                            "title": "Pet проект та портфоліо",
                            "description": "Створення повноцінного проекту для портфоліо",
                            "skills": ["Full-stack розробка", "Deploy", "Документація"],
                            "resources": ["GitHub", "Vercel/Netlify"]
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