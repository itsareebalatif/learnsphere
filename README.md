# LearnSphere

Backend (FastAPI) and frontend (React) are separate apps.

## Backend

```bash
cd backend
source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in real keys
uvicorn app.main:app --reload
```

API: http://localhost:8000  
Health: http://localhost:8000/api/health

## Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://localhost:5173  
Vite proxies `/api` to the FastAPI server.
