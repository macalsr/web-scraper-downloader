# Web Scraper Downloader (CSV → JSON + Images)

CLI tool that reads URLs from a CSV file, extracts structured data (title/description/images), downloads assets into a local folder per item, and generates:
- `data.json` per URL
- `report.csv` summary (success/error)

Built as a portfolio-friendly MVP for common freelancing tasks like “extract and download data from websites”.

---

## Features
- CSV input (column: `url`)
- Extracts: title, description, image URLs
- Downloads images into a per-item folder
- Generates `data.json` per item
- Generates `report.csv` with status + error
- Safe defaults (timeouts, limited images per page)

---

## Project Structure
```

web-scraper-downloader/
src/
scraper/
main.py
io_utils.py
extractor.py
downloader.py
report.py
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

### Option A — Simple
```bash
py -m pip install -r requirements.txt
````

### Option B — Virtual environment (recommended)

**PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

---

## Run

### Git Bash / macOS / Linux

```bash
PYTHONPATH=src python src/scraper/main.py --input sample/input.csv --output output
```

### PowerShell

```powershell
$env:PYTHONPATH="src"
python src\scraper\main.py --input sample\input.csv --output output
```

---

## Input CSV format

`sample/input.csv` must contain a column named `url`:

```csv
url
https://httpbin.org/html
https://www.iana.org/domains/reserved
```

---

## Output

After running, you will get:

* `output/<item>/data.json`
* `output/<item>/images/*`
* `output/report.csv`

Example `data.json`:

```json
{
  "url": "https://example.com/page",
  "title": "Page title",
  "description": "Short description...",
  "images": [
    "output/item/images/img_1.jpg",
    "output/item/images/img_2.jpg"
  ]
}
```

---

## Scope / Limitations

* MVP supports simple/static HTML pages
* No CAPTCHA/anti-bot bypass
* Login-protected content is out of scope unless explicitly authorized
* Dynamic JS-rendered pages can be added later (Playwright mode)

---

## Future Improvements

* Retry/backoff for network errors
* Rate limiting between requests
* Per-domain adapters (site-specific extractors)
* Optional Playwright engine for dynamic sites
* Package as an executable (PyInstaller)

---

## License

MIT (or choose your preferred license)

```
```
