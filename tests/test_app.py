from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _views(at: AppTest) -> list[str]:
    brand_ids = [b.id for b in at.session_state["portfolio"].brands]
    return ["overview", *brand_ids, "results", "report"]


def test_every_view_renders_without_errors():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception

    for view in _views(at):
        at.session_state["view"] = view
        at.run()
        assert not at.exception, f"view {view!r} raised: {at.exception}"


def test_report_shows_no_imbalance_warning_by_default():
    at = AppTest.from_file(APP, default_timeout=30)
    at.session_state["view"] = "report"
    at.run()
    assert not at.exception
    assert not any("do not sum to 100%" in w.value for w in at.warning)


def test_editing_portfolio_budget_updates_state():
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.number_input(key="portfolio_value").set_value(2500.0).run()
    assert at.session_state["portfolio"].value == 2500.0
