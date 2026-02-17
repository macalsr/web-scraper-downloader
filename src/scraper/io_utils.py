import csv
from pathlib import Path
from typing import List, Dict

def read_csv_urls(csv_path: Path) -> List[str]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if "url" not in reader.fieldnames:
            raise ValueError("CSV file must contain a 'url' column.")
        urls = []
        for row in reader:
            url = (row.get("url") or "").strip()
            if url:
                urls.append(url)
        return urls

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def write_json(path: Path, data: Dict) -> None:
    import json
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")