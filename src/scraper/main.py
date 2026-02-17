import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

from scraper.io_utils import read_csv_urls, ensure_dir, write_json
from scraper.downloader import download_images
from scraper.report import ReportRow, write_report_csv

from scraper.rate_limiter import RateLimiter
from scraper.sites.registry import pick_extractor


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "item"


def make_item_dir(base_out: Path, url: str, idx: int) -> Path:
    parsed = urlparse(url)
    host = parsed.netloc or "site"
    path = parsed.path.strip("/") or "root"
    slug = slugify(f"{host}-{path}-{idx}")
    return base_out / slug


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--rate", type=float, default=0.8, help="Min seconds between URLs")
    parser.add_argument("--max-images", type=int, default=20, help="Max images extracted per page")
    parser.add_argument("--max-links", type=int, default=30, help="Max links extracted per page")
    parser.add_argument("--text-preview", type=int, default=700, help="Max chars for text preview")
    parser.add_argument("--only-domain", default="", help="Process only URLs that match this domain (e.g. example.com)")

    args = parser.parse_args()

    csv_path = Path(args.input)
    out_base = Path(args.output)
    ensure_dir(out_base)

    urls = read_csv_urls(csv_path)

    if args.only_domain:
        urls = [u for u in urls if args.only_domain in u]

    limiter = RateLimiter(min_interval_s=args.rate)
    report_rows = []

    for idx, url in enumerate(urls, start=1):
        limiter.wait()  # ✅ rate limit antes de cada URL

        item_dir = make_item_dir(out_base, url, idx)
        images_dir = item_dir / "images"

        try:
            extractor = pick_extractor(
                url,
                max_images=args.max_images,
                max_links=args.max_links,
                text_preview=args.text_preview
            )
            data = extractor.extract(url)

            saved_images = download_images(data.image_urls, images_dir)

            payload = {
                "url": data.url,
                "title": data.title,
                "h1": data.h1,
                "description": data.description,
                "canonical_url": data.canonical_url,
                "og": data.og or {},
                "text_preview": data.text_preview,
                "links": data.links or [],
                "counts": {
                    "images_found": len(data.image_urls),
                    "links_found": len(data.links or []),
                    "images_downloaded": len(saved_images),
                },
                "images": saved_images,
                "domain" : urlparse(url).netloc
            }

            ensure_dir(item_dir)
            write_json(item_dir / "data.json", payload)

            report_rows.append(ReportRow(url=url, status="ok", output_dir=str(item_dir)))
            print(f"[OK] {url} -> {item_dir}")

        except Exception as e:
            report_rows.append(ReportRow(url=url, status="error", output_dir=str(item_dir), error=str(e)))
            print(f"[ERR] {url} -> {e}")

    write_report_csv(out_base / "report.csv", report_rows)
    print(f"\nReport: {out_base / 'report.csv'}")


if __name__ == "__main__":
    main()