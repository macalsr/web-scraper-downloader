import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class ReportRow:
    url: str
    status: str  # "ok" | "error"
    output_dir: str
    error: str = ""


def write_report_csv(path: Path, rows: List[ReportRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "status", "output_dir", "error"])
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "url": r.url,
                "status": r.status,
                "output_dir": r.output_dir,
                "error": r.error,
            })