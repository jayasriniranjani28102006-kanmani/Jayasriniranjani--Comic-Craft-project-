# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 application that creates a five-panel comic from a user prompt.

## Architecture

1. Gemini generates a structured five-panel outline.
2. Gemini generates the title, captions, narration and dialogue.
3. Hugging Face Inference Providers generate the panel illustrations.
4. The layout builder combines text and images.
5. FPDF2 creates a downloadable PDF.

The original project document describes Gemini Flash/Pro plus Stable Diffusion and the same five-panel workflow. This implementation uses the current Google GenAI Python SDK and Hugging Face `InferenceClient` APIs.

## Windows / VS Code

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and add your own API keys.

Run:

```powershell
python -m uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## Test without image API

Set:

```text
IMAGE_BACKEND=mock
```

You still need a Gemini key for story generation. This mode creates local placeholder panel images so you can test the whole web/PDF pipeline without spending image inference credits.

## API example

POST `/generate-comic/json`

```json
{
  "story_prompt": "A brave fox discovers a hidden library beneath an enchanted forest.",
  "character_name": "Luna",
  "setting": "Enchanted forest",
  "tone": "Adventure",
  "art_style": "Comic book"
}
```

## Troubleshooting

- `GEMINI_API_KEY is missing`: create `.env` and set `GEMINI_API_KEY`.
- `HF_TOKEN is missing`: set `HF_TOKEN` when `IMAGE_BACKEND=huggingface`.
- Image provider/model errors: temporarily use `IMAGE_BACKEND=mock` to verify the rest of the application.
- PowerShell activation blocked: run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again.
