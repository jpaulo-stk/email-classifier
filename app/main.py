from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.classify import router as classify_router
from app.config import settings
import re

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:5173", "http://127.0.0.1:8000", "https://email-classifier-rose.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "app_env": settings.APP_ENV}

app.include_router(classify_router)
