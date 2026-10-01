from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.schemas import PromptRequest, ComicResponse
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

router = APIRouter()
templates = Jinja2Templates(directory=str(get_settings().static_dir.parent / "templates"))

def run_pipeline(request_data: PromptRequest) -> ComicResponse:
    outline = generate_outline(request_data)
    story = generate_story(request_data, outline)

    image_paths = []
    for panel in outline:
        # Pass art style through the prompt because the image service is independent.
        visual_prompt = (
            f"{panel['image_prompt']}. Required art style: {request_data.art_style}. "
            f"Tone: {request_data.tone}. Main character: {request_data.character_name}."
        )
        image_paths.append(generate_image(visual_prompt, panel["panel_number"], panel["title"]))

    layout = build_comic_layout(outline, story, image_paths)
    pdf_path = save_pdf(story["title"], layout)
    return ComicResponse(title=story["title"], panels=layout, pdf_path=pdf_path)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        comic = run_pipeline(data)
        return templates.TemplateResponse(
            "comic_preview.html",
            {"request": request, "comic": comic.model_dump()},
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": str(exc)},
            status_code=500,
        )

@router.post("/generate-comic/json", response_model=ComicResponse)
async def generate_json(payload: PromptRequest):
    try:
        return run_pipeline(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    try:
        path = generate_image(prompt, 0, "test")
        return {"success": True, "image_url": "/" + str(Path(path).relative_to(get_settings().static_dir)).replace("\\", "/")}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/download/{filename}")
async def download_pdf(filename: str):
    settings = get_settings()
    path = settings.export_dir / Path(filename).name
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(path, media_type="application/pdf", filename=path.name)

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse("export_success.html", {"request": request})
