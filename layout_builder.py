from app.schemas import Panel

def build_comic_layout(outline: list[dict], story: dict, image_paths: list[str]) -> list[dict]:
    story_by_number = {p["panel_number"]: p for p in story["panels"]}
    layout = []
    for item, image_path in zip(outline, image_paths):
        narrative = story_by_number.get(item["panel_number"], {})
        panel = Panel(
            panel_number=item["panel_number"],
            title=item["title"],
            scene_description=item["scene_description"],
            image_prompt=item["image_prompt"],
            caption=narrative.get("caption", ""),
            narration=narrative.get("narration", ""),
            dialogue=narrative.get("dialogue", ""),
            image_path=image_path,
        )
        layout.append(panel.model_dump())
    return layout
