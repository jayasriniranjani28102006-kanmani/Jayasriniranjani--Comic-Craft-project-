from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.routes import router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI comic story creator using Gemini and Hugging Face image generation.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
app.include_router(router)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "gemini_configured": bool(settings.gemini_api_key),
        "huggingface_configured": bool(settings.hf_token),
        "image_backend": settings.image_backend,
    }
