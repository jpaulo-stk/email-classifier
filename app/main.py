from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.classify import router as classify_router
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status":"ok","app_env": settings.APP_ENV}

app.include_router(classify_router)
