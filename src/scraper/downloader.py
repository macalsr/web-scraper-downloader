from pathlib import Path
from typing import List
from urllib.parse import urlparse

import requests
from scraper.http_client import download


def _safe_filename_from_url(url: str, default: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    if not name:
        return default
    return name.split("?")[0].split("#")[0] or default

def download_images(image_urls: List[str], out_dir: Path) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    for idx, url in enumerate(image_urls, start=1):
        try:
            resp = download(url)  # retry/backoff + SSL ok
            fname = _safe_filename_from_url(url, default=f"img_{idx}.jpg")
            path = out_dir / fname

            if path.exists():
                path = out_dir / f"{path.stem}_{idx}{path.suffix or '.jpg'}"

            with path.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            saved.append(str(path))
        except Exception:
            continue

    return saved