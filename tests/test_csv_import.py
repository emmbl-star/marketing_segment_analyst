import pytest

from optimizer.csv_import import parse_results_csv
from optimizer.model import default_portfolio

CSV = """Brand,Category,Segment,Result
Brand A,Cat A1,Seg A1-1,1500
Brand A,Cat A1,,4500
Brand B,,,12000
"""


def test_rows_resolve_at_segment_category_and_brand_level():
    p = default_portfolio()
    report = parse_results_csv(CSV, p)
    assert report.errors == []
    assert report.applied_rows == 3

    a_cat1 = p.brands[0].categories[0]
    assert len(report.results) == 3 + 15
    for seg in a_cat1.segments:
        assert report.results[seg.id] == pytest.approx(1500)
    assert all(
        report.results[s.id] == pytest.approx(800)
        for c in p.brands[1].categories
        for s in c.segments
    )


def test_import_is_idempotent_when_applied_twice():
    p = default_portfolio()
    p.results.update(parse_results_csv(CSV, p).results)
    first = dict(p.results)
    p.results.update(parse_results_csv(CSV, p).results)
    assert p.results == first


def test_matching_is_case_insensitive_and_bom_tolerant():
    p = default_portfolio()
    report = parse_results_csv(
        "\ufeffbrand,category,segment,result\nBRAND a,cat a1,SEG A1-2,42\n", p
    )
    assert report.errors == [] and list(report.results.values()) == [42]


def test_errors_are_collected_per_line():
    p = default_portfolio()
    report = parse_results_csv(
        "Brand,Category,Segment,Result\n"
        "Nope,,,1\n"
        "Brand A,Nope,,1\n"
        "Brand A,Cat A1,Nope,1\n"
        "Brand A,,Seg A1-1,1\n"
        "Brand A,Cat A1,Seg A1-1,abc\n",
        p,
    )
    assert report.applied_rows == 0 and len(report.errors) == 5


def test_missing_column_raises():
    with pytest.raises(ValueError, match="Result"):
        parse_results_csv("Brand,Category,Segment\nBrand A,,\n", default_portfolio())
