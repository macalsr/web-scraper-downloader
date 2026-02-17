from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ExtractedItem:
    url: str
    title: str
    description: str
    image_urls: List[str]

    # extras (genéricos)
    h1: str = ""
    canonical_url: str = ""
    og: Dict[str, str] = None
    text_preview: str = ""
    links: List[str] = None


class BaseExtractor:
    def supports(self, url: str) -> bool:
        raise NotImplementedError

    def extract(self, url: str) -> ExtractedItem:
        raise NotImplementedError