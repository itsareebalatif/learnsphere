from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.classes.router import router as classes_router
from app.core.config import settings
from app.schools.router import router as schools_router

app = FastAPI(title="LearnSphere")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(schools_router)
app.include_router(classes_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
