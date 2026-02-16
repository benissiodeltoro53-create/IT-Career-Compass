# IT Career Compass

Персональний roadmap для IT-кар'єри за стандартами DOU та Djinni. Генерує навички, план підготовки та checklist за допомогою Google Gemini AI.

## Структура

```
frontend/   — React + Tailwind (Vite)
backend/    — FastAPI + Gemini API
```

## Отримання Gemini API ключа

1. Перейди на https://aistudio.google.com/apikey
2. Натисни **Create API Key**
3. Скопіюй ключ

## Локальний запуск

### Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Додай свій GEMINI_API_KEY в .env

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Відкрий http://localhost:5173

## Deploy

### Backend — Render

1. Створи **Web Service** на [render.com](https://render.com)
2. Root directory: `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Додай змінну `GEMINI_API_KEY` в Environment

### Frontend — Vercel

1. Створи проєкт на [vercel.com](https://vercel.com)
2. Root directory: `frontend`
3. Framework preset: Vite
4. Додай змінну `VITE_API_URL` = URL бекенду з Render
5. Deploy
