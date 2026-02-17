from pathlib import Path
from typing import List
from urllib.parse import urlparse

import requests


def _safe_filename_from_url(url: str, default: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    if not name:
        return default
    # remove query-like junk if any got into path
    return name.split("?")[0].split("#")[0] or default


def download_images(image_urls: List[str], out_dir: Path, timeout_s: int = 25) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WebScraperDownloader/1.0)"
    }

    for idx, url in enumerate(image_urls, start=1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout_s, stream=True)
            resp.raise_for_status()
            fname = _safe_filename_from_url(url, default=f"img_{idx}.jpg")
            path = out_dir / fname

            # evita sobrescrever com mesmo nome
            if path.exists():
                path = out_dir / f"{path.stem}_{idx}{path.suffix or '.jpg'}"

            with path.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            saved.append(str(path))
        except Exception:
            # não falha o item inteiro só por 1 imagem
            continue

    return saved