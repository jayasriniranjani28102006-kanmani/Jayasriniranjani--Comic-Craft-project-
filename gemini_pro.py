from google import genai
from pydantic import BaseModel
from app.config import get_settings
from app.schemas import PromptRequest

class StoryPanel(BaseModel):
    panel_number: int
    caption: str
    narration: str
    dialogue: str

class StoryResponse(BaseModel):
    title: str
    panels: list[StoryPanel]

def _client():
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is missing in .env")
    return genai.Client(api_key=settings.gemini_api_key)

def generate_story(request: PromptRequest, outline: list[dict]) -> dict:
    settings = get_settings()
    outline_text = "\n".join(
        f"Panel {p['panel_number']}: {p['title']} — {p['scene_description']}"
        for p in outline
    )
    prompt = f"""
Write the complete narrative for this {settings.panel_count}-panel comic.

User brief:
Story: {request.story_prompt}
Character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Outline:
{outline_text}

Return:
- A short, memorable comic title.
- Exactly {settings.panel_count} story panels.
- Each panel needs a short caption, 1-3 sentences of narration, and natural
  dialogue. Dialogue may be empty when nobody speaks.
- Keep character, plot, setting, and tone consistent.
- Do not add panels outside the supplied outline.
"""
    response = _client().models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": StoryResponse,
        },
    )
    parsed = response.parsed
    if not parsed:
        raise RuntimeError("Gemini returned no structured story.")
    if len(parsed.panels) != settings.panel_count:
        raise RuntimeError(f"Gemini returned {len(parsed.panels)} story panels.")
    return parsed.model_dump()
