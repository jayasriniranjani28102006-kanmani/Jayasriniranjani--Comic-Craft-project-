from pathlib import Path
from fpdf import FPDF
from PIL import Image
from app.config import get_settings

def _fit_image(path: str, max_w: float, max_h: float) -> tuple[float, float]:
    with Image.open(path) as img:
        w, h = img.size
    scale = min(max_w / w, max_h / h)
    return w * scale, h * scale

def save_pdf(title: str, layout: list[dict]) -> str:
    settings = get_settings()
    safe_title = "".join(c if c.isalnum() else "_" for c in title)[:50].strip("_") or "comic"
    filename = f"{safe_title}_{__import__('time').strftime('%Y%m%d_%H%M%S')}.pdf"
    output = settings.export_dir / filename

    pdf = FPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=False)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, f"Panel {panel['panel_number']}: {panel['title']}")
        pdf.ln(2)

        image_path = Path(panel["image_path"])
        if image_path.exists():
            x, y = 10, pdf.get_y()
            max_w, max_h = 190, 125
            w, h = _fit_image(str(image_path), max_w, max_h)
            pdf.image(str(image_path), x=x + (max_w - w) / 2, y=y, w=w, h=h)
            pdf.set_y(y + h + 6)

        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, panel["scene_description"])
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        if panel.get("caption"):
            pdf.multi_cell(0, 6, "Caption: " + panel["caption"])
        if panel.get("narration"):
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, "Narration: " + panel["narration"])
        if panel.get("dialogue"):
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, "Dialogue: " + panel["dialogue"])

    pdf.output(str(output))
    return output.as_posix()
