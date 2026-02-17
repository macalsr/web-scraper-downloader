from typing import List, Optional, Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scraper.http_client import get
from scraper.sites.base import BaseExtractor, ExtractedItem


class GenericHtmlExtractor(BaseExtractor):

    def __init__(self, max_images: int = 20, max_links: int = 30, text_preview_limit: int = 700):
        self.max_images = max_images
        self.max_links = max_links
        self.text_preview_limit = text_preview_limit

    def supports(self, url: str) -> bool:
        return True  # fallback

    def extract(self, url: str) -> ExtractedItem:
        html = get(url).text
        soup = BeautifulSoup(html, "html.parser")

        title = self._get_title(soup) or ""
        description = self._get_description(soup) or ""
        image_urls = self._get_images(soup, base_url=url)

        h1 = self._get_h1(soup) or ""
        canonical_url = self._get_canonical(soup, base_url=url) or ""
        og = self._get_og(soup, base_url=url)
        text_preview = self._get_text_preview(soup, limit=700)
        links = self._get_links(soup, base_url=url, limit=30)

        return ExtractedItem(
            url=url,
            title=title.strip(),
            description=description.strip(),
            image_urls=image_urls,
            h1=h1.strip(),
            canonical_url=canonical_url.strip(),
            og=og,
            text_preview=text_preview,
            links=links,
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

    def _get_h1(self, soup: BeautifulSoup) -> Optional[str]:
        h1 = soup.select_one("h1")
        if h1:
            txt = h1.get_text(" ", strip=True)
            return txt if txt else None
        return None

    def _get_canonical(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        link = soup.select_one('link[rel="canonical"]')
        if link and link.get("href"):
            return urljoin(base_url, link["href"])
        return None

    def _get_og(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for m in soup.select('meta[property^="og:"]'):
            prop = (m.get("property") or "").strip()
            content = (m.get("content") or "").strip()
            if not prop or not content:
                continue
            if prop == "og:image":
                content = urljoin(base_url, content)
            out[prop] = content
        return out

    def _get_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        urls: List[str] = []

        og = soup.select_one('meta[property="og:image"]')
        if og and og.get("content"):
            urls.append(urljoin(base_url, og["content"]))

        for img in soup.select("img"):
            src = (img.get("src") or "").strip()
            if not src:
                continue
            urls.append(urljoin(base_url, src))

        # remove duplicados preservando ordem
        seen = set()
        out = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                out.append(u)
        return out[:20]

    def _get_links(self, soup: BeautifulSoup, base_url: str, limit: int = 10) -> List[str]:
        links: List[str] = []
        for a in soup.select("a[href]"):
            href = (a.get("href") or "").strip()
            if not href:
                continue
            links.append(urljoin(base_url, href))
        # dedupe
        seen = set()
        out = []
        for u in links:
            if u not in seen:
                seen.add(u)
                out.append(u)
        return out[:limit]

    def _get_text_preview(self, soup: BeautifulSoup, limit: int = 300) -> str:
        text = soup.get_text(" ", strip=True)
        text = " ".join(text.split())
        return text[:limit]