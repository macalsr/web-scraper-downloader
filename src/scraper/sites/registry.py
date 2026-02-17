from typing import List
from scraper.sites.base import BaseExtractor
from scraper.sites.generic import GenericHtmlExtractor
from scraper.sites.generic import GenericHtmlExtractor

EXTRACTORS: List[BaseExtractor] = [
    # Exemplo futuro: BethaExtractor(),
    GenericHtmlExtractor(),  # sempre por último como fallback
]

def pick_extractor(url: str, *, max_images: int = 20, max_links: int = 30, text_preview: int = 700):
    for ex in EXTRACTORS:
        if ex.supports(url):
            return ex
    return GenericHtmlExtractor(max_images=max_images, max_links=max_links, text_preview=text_preview)