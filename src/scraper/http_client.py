import requests
import certifi
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WebScraperDownloader/1.0)"
}

RETRYABLE_EXCEPTIONS = (
    requests.Timeout,
    requests.ConnectionError,
    requests.exceptions.ChunkedEncodingError,
)

@retry(
    reraise=True,
    stop=stop_after_attempt(3),                 # 3 tentativas
    wait=wait_exponential(multiplier=1, min=1, max=8),  # backoff: 1s, 2s, 4s... até 8s
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
)
def get(url: str, timeout_s: int = 20) -> requests.Response:
    resp = requests.get(
        url,
        headers=DEFAULT_HEADERS,
        timeout=timeout_s,
        verify=certifi.where(),  # corrige seu SSL no Windows
    )
    resp.raise_for_status()
    return resp

@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
)
def download(url: str, timeout_s: int = 25) -> requests.Response:
    resp = requests.get(
        url,
        headers=DEFAULT_HEADERS,
        timeout=timeout_s,
        verify=certifi.where(),
        stream=True,
    )
    resp.raise_for_status()
    return resp