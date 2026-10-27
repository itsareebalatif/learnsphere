# app/main.py
from fastapi import FastAPI
from nicegui import ui
from app.config import settings

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@ui.page("/")
def home():
    ui.label("LearnSphere is running").classes("text-h4 q-ma-md")

ui.run_with(app, storage_secret=settings.STORAGE_SECRET)