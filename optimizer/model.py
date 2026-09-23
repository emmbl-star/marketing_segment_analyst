from __future__ import annotations

import uuid
from dataclasses import dataclass, field

TOLERANCE = 0.01
DEFAULT_PORTFOLIO_VALUE = 10_000.0


@dataclass
class Seg:
    id: str
    name: str
    value: float


@dataclass
class Cat:
    id: str
    name: str
    value: float
    segments: list[Seg] = field(default_factory=list)


@dataclass
class Brand:
    id: str
    name: str
    value: float
    categories: list[Cat] = field(default_factory=list)


@dataclass
class Portfolio:
    value: float = DEFAULT_PORTFOLIO_VALUE
    brands: list[Brand] = field(default_factory=list)
    results: dict[str, float] = field(default_factory=dict)


@dataclass
class SegRow:
    brand: Brand
    cat: Cat
    seg: Seg
    budget: float
    result: float | None


def new_id() -> str:
    return uuid.uuid4().hex[:8]


def _split(n: int) -> list[float]:
    base = round(100 / n, 2)
    values = [base] * n
    values[-1] = round(100 - base * (n - 1), 2)
    return values


def default_portfolio(n_brands: int = 5, n_cats: int = 5, n_segs: int = 3) -> Portfolio:
    brands = []
    for bi, bval in enumerate(_split(n_brands)):
        letter = chr(ord("A") + bi)
        cats = []
        for ci, cval in enumerate(_split(n_cats), start=1):
            segs = [
                Seg(new_id(), f"Seg {letter}{ci}-{si}", sval)
                for si, sval in enumerate(_split(n_segs), start=1)
            ]
            cats.append(Cat(new_id(), f"Cat {letter}{ci}", cval, segs))
        brands.append(Brand(new_id(), f"Brand {letter}", bval, cats))
    return Portfolio(brands=brands)


def new_brand(portfolio: Portfolio) -> Brand:
    n = len(portfolio.brands) + 1
    while any(b.name == f"Brand {n}" for b in portfolio.brands):
        n += 1
    seg = Seg(new_id(), "Seg 1", 100.0)
    cat = Cat(new_id(), "Cat 1", 100.0, [seg])
    return Brand(new_id(), f"Brand {n}", 0.0, [cat])


def remove_brand(portfolio: Portfolio, brand_id: str) -> None:
    for brand in portfolio.brands:
        if brand.id == brand_id:
            for _, _, seg in _segments_of(brand):
                portfolio.results.pop(seg.id, None)
    portfolio.brands = [b for b in portfolio.brands if b.id != brand_id]


def _segments_of(brand: Brand):
    for cat in brand.categories:
        for seg in cat.segments:
            yield brand, cat, seg


def brand_budget(portfolio: Portfolio, brand: Brand) -> float:
    return portfolio.value * brand.value / 100


def cat_budget(portfolio: Portfolio, brand: Brand, cat: Cat) -> float:
    return brand_budget(portfolio, brand) * cat.value / 100


def seg_budget(portfolio: Portfolio, brand: Brand, cat: Cat, seg: Seg) -> float:
    return cat_budget(portfolio, brand, cat) * seg.value / 100


def flatten(portfolio: Portfolio) -> list[SegRow]:
    rows = []
    for brand in portfolio.brands:
        for _, cat, seg in _segments_of(brand):
            rows.append(
                SegRow(
                    brand,
                    cat,
                    seg,
                    seg_budget(portfolio, brand, cat, seg),
                    portfolio.results.get(seg.id),
                )
            )
    return rows


def level_total(items) -> float:
    return sum(i.value for i in items)


def is_balanced(items) -> bool:
    return abs(level_total(items) - 100) <= TOLERANCE


def imbalanced_levels(portfolio: Portfolio) -> list[str]:
    problems = []
    if portfolio.brands and not is_balanced(portfolio.brands):
        problems.append(f"Brands sum to {level_total(portfolio.brands):.2f}%")
    for brand in portfolio.brands:
        if brand.categories and not is_balanced(brand.categories):
            problems.append(
                f"{brand.name}: categories sum to {level_total(brand.categories):.2f}%"
            )
        for cat in brand.categories:
            if cat.segments and not is_balanced(cat.segments):
                problems.append(
                    f"{brand.name} / {cat.name}: segments sum to "
                    f"{level_total(cat.segments):.2f}%"
                )
    return problems


def apply_slack_to_item(items, target_id: str) -> None:
    slack = 100 - level_total(items)
    for item in items:
        if item.id == target_id:
            item.value = round(max(0.0, item.value + slack), 4)


def spread_slack(items, exclude_id: str | None = None) -> None:
    others = [i for i in items if i.id != exclude_id]
    if not others:
        return
    slack = 100 - level_total(items)
    pool = sum(i.value for i in others)
    for item in others:
        share = item.value / pool if pool > 0 else 1 / len(others)
        item.value = round(max(0.0, item.value + slack * share), 4)


def apply_level_edits(items, rows: list[dict], parent_budget: float) -> bool:
    """Apply edited table rows (name, pct, budget) back onto items.

    A changed percentage wins over a changed budget. A changed budget is
    converted back to a percentage of the parent budget.
    """
    changed = False
    for item, row in zip(items, rows):
        name = row.get("name")
        if isinstance(name, str) and name.strip() and name.strip() != item.name:
            item.name = name.strip()
            changed = True

        pct, budget = row.get("pct"), row.get("budget")
        current_budget = parent_budget * item.value / 100
        if pct is not None and pct == pct and abs(pct - item.value) > 1e-9:
            item.value = float(max(0.0, pct))
            changed = True
        elif (
            budget is not None
            and budget == budget
            and parent_budget > 0
            and abs(budget - current_budget) > 1e-6
        ):
            item.value = float(max(0.0, budget / parent_budget * 100))
            changed = True
    return changed


def set_seg_results(portfolio: Portfolio, seg_ids: list[str], total: float) -> None:
    if not seg_ids:
        return
    each = total / len(seg_ids)
    for seg_id in seg_ids:
        portfolio.results[seg_id] = each


def cat_seg_ids(cat: Cat) -> list[str]:
    return [s.id for s in cat.segments]


def brand_seg_ids(brand: Brand) -> list[str]:
    return [seg.id for _, _, seg in _segments_of(brand)]


def sum_results(portfolio: Portfolio, seg_ids: list[str]) -> float | None:
    present = [portfolio.results[i] for i in seg_ids if i in portfolio.results]
    return sum(present) if present else None


def dense_rank(values: list[float | None]) -> list[int | None]:
    """Dense rank by value descending (#1 = highest); None stays unranked."""
    distinct = sorted({v for v in values if v is not None}, reverse=True)
    position = {v: i + 1 for i, v in enumerate(distinct)}
    return [position[v] if v is not None else None for v in values]


def target_ratio(budget: float, result: float | None) -> float | None:
    if result is None or budget <= 0:
        return None
    return result / budget
