from typing import List
from scraper.sites.base import BaseExtractor
from scraper.sites.generic import GenericHtmlExtractor

# aqui você vai adicionando extractors específicos depois
EXTRACTORS: List[BaseExtractor] = [
    # Exemplo futuro: BethaExtractor(),
    GenericHtmlExtractor(),  # sempre por último como fallback
]

def pick_extractor(url: str) -> BaseExtractor:
    for ex in EXTRACTORS:
        if ex.supports(url):
            return ex
    return GenericHtmlExtractor()