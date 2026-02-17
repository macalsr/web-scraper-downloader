# Web Scraper Downloader (CSV → JSON + Assets + Consolidated CSV)

CLI tool that reads URLs from a CSV, fetches each page, extracts structured data, downloads assets (e.g., images), and outputs:
- `data.json` per URL (optional)
- `data.csv` consolidated (optional)
- `report.csv` summary (success/error/skipped)

This is a portfolio-focused MVP that matches common freelancing tasks like “extract and download data from websites”.

---

## What it does

Given a CSV with URLs, for each URL the tool:

1. **Rate-limits requests** (waits between URLs to reduce blocking)
2. **Fetches the HTML** with SSL verification using `certifi`
3. **Retries on network errors** using exponential backoff (1s, 2s, 4s…)
4. **Extracts data** (title/description/h1/canonical/OG tags/text preview/links/images)
5. **Downloads images** into an organized local folder
6. Writes outputs:
   - per-item `data.json` (optional)
   - consolidated `data.csv` (optional)
   - `report.csv` (always)

---

## Features

### Reliability
- Retry + exponential backoff for network failures (timeouts, connection errors)
- SSL verification via `certifi` (more stable on Windows)
- Rate limiting between URLs (reduces 403/429 blocks)

### Data extraction (generic)
- `title`
- `description` (meta/og/first paragraph fallback)
- `h1`
- `canonical_url`
- `og` (Open Graph tags like `og:title`, `og:description`, `og:image`)
- `text_preview` (first N chars of extracted text)
- `links` (limited list)
- `image_urls` found on the page
- Downloaded image paths + counts

### Outputs
- `data.json` per URL
- `data.csv` consolidated (one row per URL)
- `report.csv` with `ok` / `error` / `skipped`

### Extensibility
- Per-domain adapters (site-specific extractors)
  - `GenericHtmlExtractor` works as a fallback for most pages
  - Add custom extractors for specific domains later

---

## Project Structure

```

web-scraper-downloader/
src/
scraper/
main.py
io_utils.py
report.py
exporter.py             # consolidated data.csv
downloader.py
http_client.py          # retry/backoff + SSL
rate_limiter.py         # rate limiting between URLs
sites/
base.py               # ExtractedItem + BaseExtractor
generic.py            # Generic extractor (fallback)
registry.py           # pick_extractor(url)
sample/
input.csv
requirements.txt
README.md

````

---

## Requirements
- Python 3.10+ (Windows/macOS/Linux)

---

## Install

> Windows tip: avoid `pip` directly. Prefer `py -3.14 -m pip ...` or a virtual environment.

### Option A — Simple
```bash
py -3.14 -m pip install -r requirements.txt
````

### Option B — Virtual environment (recommended)

**PowerShell**

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Git Bash**

```bash
py -3.14 -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Input CSV format

The CSV must contain a column named `url`.

Example `sample/input.csv`:

```csv
url
https://httpbin.org/html
https://www.iana.org/domains/reserved
```

---

## Run

### Git Bash / macOS / Linux

```bash
PYTHONPATH=src python src/scraper/main.py --input sample/input.csv --output output --rate 1.2 --format both
```

### PowerShell

```powershell
$env:PYTHONPATH="src"
python src\scraper\main.py --input sample\input.csv --output output --rate 1.2 --format both
```

---

## CLI Parameters

* `--input` : path to CSV
* `--output` : output directory
* `--rate` : minimum seconds between URLs (rate limiting)
* `--format` : `json` | `csv` | `both` (default: `both`)
* `--resume` : skip URLs already processed (checks for `data.json` in the item folder)

### Examples

Generate both JSON per item and a consolidated CSV:

```bash
PYTHONPATH=src python src/scraper/main.py --input sample/input.csv --output output --rate 1.2 --format both
```

Only consolidated CSV:

```bash
PYTHONPATH=src python src/scraper/main.py --input sample/input.csv --output output --rate 1.2 --format csv
```

Resume after a partial run (skip already processed):

```bash
PYTHONPATH=src python src/scraper/main.py --input sample/input.csv --output output --rate 1.2 --resume
```

---

## Output

After running, you will get:

* `output/<item>/data.json` (if `--format json|both`)
* `output/<item>/images/*` (downloaded assets)
* `output/data.csv` (if `--format csv|both`)
* `output/report.csv` (always)

### Example `data.json`

```json
{
  "url": "https://example.com/page",
  "title": "Page title",
  "h1": "Main heading",
  "description": "Short description...",
  "canonical_url": "https://example.com/page",
  "og": {
    "og:title": "Page title",
    "og:description": "Short description...",
    "og:image": "https://example.com/image.jpg"
  },
  "text_preview": "First characters of the page text...",
  "links": [
    "https://example.com/about",
    "https://example.com/contact"
  ],
  "counts": {
    "images_found": 5,
    "links_found": 30,
    "images_downloaded": 3
  },
  "images": [
    "output/item/images/img_1.jpg",
    "output/item/images/img_2.jpg"
  ]
}
```

### Example `data.csv` (consolidated)

One row per URL, with flattened fields such as `url`, `title`, `h1`, `canonical_url`, `og_title`, `og_description`, `og_image`, `images_found`, `images_downloaded`, `links_found`, `text_preview`.

### Example `report.csv`

```csv
url,status,output_dir,error
https://httpbin.org/html,ok,output/httpbin-org-html-1,
https://site-that-fails,error,output/site-that-fails-2,"Timeout"
https://already-processed,skipped,output/already-processed-3,
```

---

## Limitations

* Designed for static HTML pages (requests + BeautifulSoup).
* Does not bypass CAPTCHA / anti-bot systems.
* Some domains may block scraping or require permission.
* JavaScript-heavy pages require a browser engine (future improvement).

---

## How to add a site-specific extractor (adapter)

1. Create a new extractor in `src/scraper/sites/` (e.g. `mydomain.py`) implementing `BaseExtractor`
2. Make `supports(url)` return `True` for that domain
3. Add it to `EXTRACTORS` in `registry.py` **before** `GenericHtmlExtractor`

This allows precise extraction (price/SKU/author/date/etc.) for that specific site.

---

## Future improvements

* Optional Playwright engine for JS-rendered pages
* Package as an executable (PyInstaller)
* Better normalization for images and file names
* Concurrency with safe rate limiting

---

## License

MIT (or choose your preferred license)

