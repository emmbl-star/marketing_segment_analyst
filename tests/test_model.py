import pytest

from optimizer.model import (
    apply_level_edits,
    apply_slack_to_item,
    brand_budget,
    cat_budget,
    default_portfolio,
    dense_rank,
    flatten,
    imbalanced_levels,
    is_balanced,
    level_total,
    remove_brand,
    seg_budget,
    set_seg_results,
    spread_slack,
)


def test_default_portfolio_shape_and_balance():
    p = default_portfolio()
    assert len(p.brands) == 5
    assert all(len(b.categories) == 5 for b in p.brands)
    assert all(len(c.segments) == 3 for b in p.brands for c in b.categories)
    assert imbalanced_levels(p) == []
    assert p.value == 10_000


def test_budget_cascades_multiplicatively():
    p = default_portfolio()
    brand = p.brands[0]
    cat = brand.categories[0]
    seg = cat.segments[0]
    assert brand_budget(p, brand) == pytest.approx(10_000 * brand.value / 100)
    assert cat_budget(p, brand, cat) == pytest.approx(
        brand_budget(p, brand) * cat.value / 100
    )
    assert seg_budget(p, brand, cat, seg) == pytest.approx(
        cat_budget(p, brand, cat) * seg.value / 100
    )
    assert sum(r.budget for r in flatten(p)) == pytest.approx(10_000)


def test_imbalance_is_reported_not_blocked():
    p = default_portfolio()
    p.brands[0].value = 40
    problems = imbalanced_levels(p)
    assert len(problems) == 1 and "Brands sum to" in problems[0]
    assert not is_balanced(p.brands)


def test_apply_slack_to_item_and_spread():
    p = default_portfolio()
    p.brands[0].value = 40
    apply_slack_to_item(p.brands, p.brands[1].id)
    assert level_total(p.brands) == pytest.approx(100)
    assert p.brands[1].value == pytest.approx(0)

    p = default_portfolio()
    p.brands[0].value = 40
    spread_slack(p.brands, exclude_id=p.brands[0].id)
    assert level_total(p.brands) == pytest.approx(100)
    assert p.brands[0].value == 40


def test_level_edit_pct_and_budget_roundtrip():
    p = default_portfolio()
    brands = p.brands
    rows = [
        {"name": b.name, "pct": b.value, "budget": p.value * b.value / 100}
        for b in brands
    ]
    assert apply_level_edits(brands, rows, p.value) is False

    rows[0]["budget"] = 3_000
    assert apply_level_edits(brands, rows, p.value) is True
    assert brands[0].value == pytest.approx(30)

    rows = [
        {"name": b.name, "pct": b.value, "budget": p.value * b.value / 100}
        for b in brands
    ]
    rows[1]["pct"] = 25
    rows[1]["name"] = "Renamed"
    assert apply_level_edits(brands, rows, p.value) is True
    assert brands[1].value == 25 and brands[1].name == "Renamed"


def test_result_distribution_and_rank():
    p = default_portfolio()
    cat = p.brands[0].categories[0]
    set_seg_results(p, [s.id for s in cat.segments], 900)
    assert all(p.results[s.id] == pytest.approx(300) for s in cat.segments)
    assert dense_rank([300, None, 500, 300]) == [2, None, 1, 2]


def test_remove_brand_drops_its_results():
    p = default_portfolio()
    brand = p.brands[0]
    seg = brand.categories[0].segments[0]
    p.results[seg.id] = 10
    remove_brand(p, brand.id)
    assert seg.id not in p.results and len(p.brands) == 4
