from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field

from .model import Portfolio, brand_seg_ids, cat_seg_ids

REQUIRED_COLUMNS = ("Brand", "Category", "Segment", "Result")


@dataclass
class ImportReport:
    results: dict[str, float] = field(default_factory=dict)
    applied_rows: int = 0
    errors: list[str] = field(default_factory=list)


def _norm(text: str | None) -> str:
    return (text or "").strip().lower()


def parse_results_csv(raw: bytes | str, portfolio: Portfolio) -> ImportReport:
    """Parse a results CSV into segment results (Can$K).

    Each row sets (replaces) results, so importing the same file twice gives
    the same outcome. Blank Segment spreads the value evenly across the
    category; blank Category and Segment spreads it across the brand.
    """
    text = (raw.decode("utf-8") if isinstance(raw, bytes) else raw).lstrip("\ufeff")
    reader = csv.DictReader(io.StringIO(text))
    headers = {_norm(h): h for h in (reader.fieldnames or [])}
    missing = [c for c in REQUIRED_COLUMNS if c.lower() not in headers]
    if missing:
        raise ValueError(f"Missing column(s): {', '.join(missing)}")

    report = ImportReport()
    brands = {_norm(b.name): b for b in portfolio.brands}

    for line_no, row in enumerate(reader, start=2):
        cell = {c: row.get(headers[c.lower()]) for c in REQUIRED_COLUMNS}
        brand_name, cat_name, seg_name = (
            _norm(cell["Brand"]),
            _norm(cell["Category"]),
            _norm(cell["Segment"]),
        )
        if not (brand_name or cat_name or seg_name or _norm(cell["Result"])):
            continue

        try:
            value = float(_norm(cell["Result"]).replace(",", ""))
        except ValueError:
            report.errors.append(f"Line {line_no}: invalid Result '{cell['Result']}'")
            continue

        brand = brands.get(brand_name)
        if brand is None:
            report.errors.append(f"Line {line_no}: unknown brand '{cell['Brand']}'")
            continue

        if not cat_name:
            if seg_name:
                report.errors.append(f"Line {line_no}: Segment given without Category")
                continue
            targets = brand_seg_ids(brand)
        else:
            cat = next((c for c in brand.categories if _norm(c.name) == cat_name), None)
            if cat is None:
                report.errors.append(
                    f"Line {line_no}: unknown category '{cell['Category']}' in {brand.name}"
                )
                continue
            if not seg_name:
                targets = cat_seg_ids(cat)
            else:
                seg = next((s for s in cat.segments if _norm(s.name) == seg_name), None)
                if seg is None:
                    report.errors.append(
                        f"Line {line_no}: unknown segment '{cell['Segment']}' in {cat.name}"
                    )
                    continue
                targets = [seg.id]

        if not targets:
            report.errors.append(f"Line {line_no}: no segments to receive the result")
            continue
        for seg_id in targets:
            report.results[seg_id] = value / len(targets)
        report.applied_rows += 1

    return report
