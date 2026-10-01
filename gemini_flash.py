from google import genai
from pydantic import BaseModel, Field
from app.config import get_settings
from app.schemas import PromptRequest

class OutlinePanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str

class OutlineResponse(BaseModel):
    panels: list[OutlinePanel]

def _client():
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is missing in .env")
    return genai.Client(api_key=settings.gemini_api_key)

def generate_outline(request: PromptRequest) -> list[dict]:
    settings = get_settings()
    prompt = f"""
Create a coherent {settings.panel_count}-panel comic outline.

Story idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Requirements:
- Exactly {settings.panel_count} panels.
- Keep the same main character and visual identity throughout.
- Panel 1 establishes the situation.
- Middle panels develop a clear conflict or discovery.
- Final panel gives a satisfying ending.
- Each image_prompt must describe only visible visual content, composition,
  character appearance, environment, lighting, camera angle, and art style.
- Do not put speech bubbles, captions, logos, watermarks, or readable text in images.
"""
    response = _client().models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": OutlineResponse,
        },
    )
    parsed = response.parsed
    if not parsed:
        raise RuntimeError("Gemini returned no structured outline.")
    if len(parsed.panels) != settings.panel_count:
        raise RuntimeError(f"Gemini returned {len(parsed.panels)} panels; expected {settings.panel_count}.")
    return [p.model_dump() for p in parsed.panels]
