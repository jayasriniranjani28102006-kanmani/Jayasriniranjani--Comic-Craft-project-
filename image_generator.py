import re
from pathlib import Path
from PIL import Image, ImageDraw
from huggingface_hub import InferenceClient
from app.config import get_settings

def _safe_name(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_")
    return value[:60] or "panel"

def _placeholder(prompt: str, path: Path, panel_number: int) -> str:
    image = Image.new("RGB", (768, 768), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 748, 748), outline="black", width=6)
    draw.text((45, 45), f"ComicCraft - Panel {panel_number}", fill="black")
    draw.multiline_text((45, 100), prompt[:700], fill="black", spacing=8)
    image.save(path, format="PNG")
    return path.as_posix()

def generate_image(prompt: str, panel_number: int, title: str) -> str:
    settings = get_settings()
    filename = f"{panel_number:02d}_{_safe_name(title)}.png"
    path = settings.panel_dir / filename

    if settings.image_backend.lower() in {"mock", "placeholder"}:
        return _placeholder(prompt, path, panel_number)

    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is missing in .env")

    client = InferenceClient(
        provider=settings.hf_provider,
        api_key=settings.hf_token,
        timeout=settings.image_timeout,
    )
    full_prompt = (
        "Comic book illustration, cohesive recurring character, clean composition, "
        f"{prompt}. Art direction: cinematic comic panel, {settings.art_style if hasattr(settings, 'art_style') else 'detailed'}."
    )
    image = client.text_to_image(
        full_prompt,
        model=settings.hf_image_model,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        negative_prompt="text, letters, captions, speech bubbles, watermark, logo, blurry, distorted anatomy",
    )
    image.save(path)
    return path.as_posix()
