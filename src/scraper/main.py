import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

from scraper.io_utils import read_csv_urls, ensure_dir, write_json
from scraper.extractor import SimpleHtmlExtractor
from scraper.downloader import download_images
from scraper.report import ReportRow, write_report_csv


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
    parser = argparse.ArgumentParser(description="Web Scraper Downloader (CSV -> JSON + imagens)")
    parser.add_argument("--input", required=True, help="Caminho do CSV com coluna 'url'")
    parser.add_argument("--output", required=True, help="Pasta de saída")
    args = parser.parse_args()

    csv_path = Path(args.input)
    out_base = Path(args.output)

    ensure_dir(out_base)

    urls = read_csv_urls(csv_path)
    extractor = SimpleHtmlExtractor()

    report_rows = []

    for idx, url in enumerate(urls, start=1):
        item_dir = make_item_dir(out_base, url, idx)
        images_dir = item_dir / "images"
        try:
            data = extractor.extract(url)
            saved_images = download_images(data.image_urls, images_dir)

            payload = {
                "url": data.url,
                "title": data.title,
                "description": data.description,
                "images": saved_images,
            }
            ensure_dir(item_dir)
            write_json(item_dir / "data.json", payload)

            report_rows.append(ReportRow(url=url, status="ok", output_dir=str(item_dir)))
            print(f"[OK] {url} -> {item_dir}")
        except Exception as e:
            report_rows.append(ReportRow(url=url, status="error", output_dir=str(item_dir), error=str(e)))
            print(f"[ERR] {url} -> {e}")

    write_report_csv(out_base / "report.csv", report_rows)
    print(f"\nRelatório gerado em: {out_base / 'report.csv'}")


if __name__ == "__main__":
    main()