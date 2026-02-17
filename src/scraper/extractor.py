from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin
import certifi
import requests
from bs4 import BeautifulSoup

@dataclass
class ExtractedItem:
    url: str
    title: str
    description: str
    image_urls: List[str]

class SimpleHtmlExtractor:
    """
    Extrator genérico (funciona em muitos sites simples).
    Para sites específicos, você cria um extrator dedicado.
    """

    def __init__(self, timeout_s: int = 20):
        self.timeout_s = timeout_s

    def fetch_html(self, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WebScraperDownloader/1.0)"
        }
        resp = requests.get(
            url,
            headers=headers,
            timeout=self.timeout_s,
            verify=certifi.where()
        )
        resp.raise_for_status()
        return resp.text

    def extract(self, url: str) -> ExtractedItem:
        html = self.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        title = self._get_title(soup) or ""
        description = self._get_description(soup) or ""
        image_urls = self._get_images(soup, base_url=url)

        return ExtractedItem(
            url=url,
            title=title.strip(),
            description=description.strip(),
            image_urls=image_urls,
        )

    def _get_title(self, soup: BeautifulSoup) -> Optional[str]:
        og = soup.select_one('meta[property="og:title"]')
        if og and og.get("content"):
            return og["content"]
        if soup.title and soup.title.text:
            return soup.title.text
        h1 = soup.select_one("h1")
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)
        return None

    def _get_description(self, soup: BeautifulSoup) -> Optional[str]:
        og = soup.select_one('meta[property="og:description"]')
        if og and og.get("content"):
            return og["content"]
        meta = soup.select_one('meta[name="description"]')
        if meta and meta.get("content"):
            return meta["content"]
        p = soup.select_one("p")
        if p and p.get_text(strip=True):
            return p.get_text(strip=True)
        return None

    def _get_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        urls: List[str] = []

        # 1) og:image
        og = soup.select_one('meta[property="og:image"]')
        if og and og.get("content"):
            urls.append(urljoin(base_url, og["content"]))

        # 2) imagens comuns
        for img in soup.select("img"):
            src = img.get("src") or ""
            src = src.strip()
            if not src:
                continue
            full = urljoin(base_url, src)
            urls.append(full)

        # remove duplicados preservando ordem
        seen = set()
        out = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                out.append(u)
        return out[:15]  # limite para não baixar infinito