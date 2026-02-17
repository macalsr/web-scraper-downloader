import csv
from pathlib import Path
from typing import Any, Dict, List


def export_data_csv(out_path: Path, rows: List[Dict[str, Any]]) -> None:
    """
    Export a consolidated CSV with one row per scraped URL.
    This expects 'payload' dicts like the ones you already write to data.json.
    """
    if not rows:
        # still create an empty file with headers for predictability
        headers = [
            "url", "title", "h1", "description", "canonical_url",
            "og_title", "og_description", "og_image",
            "images_found", "images_downloaded", "links_found",
            "text_preview",
        ]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
        return

    def safe_get(d: Dict[str, Any], path: List[str], default: Any = "") -> Any:
        cur: Any = d
        for p in path:
            if not isinstance(cur, dict) or p not in cur:
                return default
            cur = cur[p]
        return cur

    flat_rows: List[Dict[str, Any]] = []
    for p in rows:
        og = p.get("og") or {}
        counts = p.get("counts") or {}

        flat_rows.append({
            "url": p.get("url", ""),
            "title": p.get("title", ""),
            "h1": p.get("h1", ""),
            "description": p.get("description", ""),
            "canonical_url": p.get("canonical_url", ""),
            "og_title": og.get("og:title", ""),
            "og_description": og.get("og:description", ""),
            "og_image": og.get("og:image", ""),
            "images_found": counts.get("images_found", ""),
            "images_downloaded": counts.get("images_downloaded", ""),
            "links_found": counts.get("links_found", ""),
            "text_preview": p.get("text_preview", ""),
        })

    headers = list(flat_rows[0].keys())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(flat_rows)