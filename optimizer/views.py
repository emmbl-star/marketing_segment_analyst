from __future__ import annotations

import pandas as pd
import streamlit as st

from .charts import radar_figure, sunburst_figure
from .csv_import import parse_results_csv
from .model import (
    TOLERANCE,
    Portfolio,
    apply_level_edits,
    apply_slack_to_item,
    brand_budget,
    brand_seg_ids,
    cat_budget,
    cat_seg_ids,
    dense_rank,
    flatten,
    imbalanced_levels,
    level_total,
    new_brand,
    remove_brand,
    seg_budget,
    set_seg_results,
    spread_slack,
    sum_results,
    target_ratio,
)

OVER_TARGET = 1.2
UNDER_TARGET = 0.8
CHIPS_PER_ROW = 6


def _bump() -> None:
    st.session_state.ver += 1
    st.rerun()


def _is_blank(value) -> bool:
    return value is None or value != value


def slack_strip(items, key: str) -> None:
    total = level_total(items)
    if abs(total - 100) <= TOLERANCE:
        st.caption("Sums to 100%")
        return

    slack = 100 - total
    st.warning(f"Sums to {total:.2f}% — {slack:+.2f}% left to redistribute.")
    for start in range(0, len(items) + 1, CHIPS_PER_ROW):
        chunk = items[start : start + CHIPS_PER_ROW]
        cols = st.columns(len(chunk) + (1 if start + CHIPS_PER_ROW > len(items) else 0))
        for col, item in zip(cols, chunk):
            if col.button(
                f"{item.name} {slack:+.1f}%",
                key=f"{key}_apply_{item.id}",
                disabled=item.value + slack < 0,
                help=f"Apply the full {slack:+.2f}% to {item.name}",
            ):
                apply_slack_to_item(items, item.id)
                _bump()
        if start + CHIPS_PER_ROW > len(items):
            if cols[-1].button("Spread proportionally", key=f"{key}_spread"):
                spread_slack(items)
                _bump()


def level_editor(items, parent_budget: float, key: str, name_label: str) -> None:
    df = pd.DataFrame(
        {
            name_label: [i.name for i in items],
            "Allocation %": [i.value for i in items],
            "Budget (Can$K)": [parent_budget * i.value / 100 for i in items],
        }
    )
    edited = st.data_editor(
        df,
        key=f"{key}_{st.session_state.ver}",
        hide_index=True,
        num_rows="fixed",
        width="stretch",
        column_config={
            "Allocation %": st.column_config.NumberColumn(
                min_value=0.0, max_value=100.0, step=0.1, format="%.2f"
            ),
            "Budget (Can$K)": st.column_config.NumberColumn(
                min_value=0.0, step=10.0, format="%.1f"
            ),
        },
    )
    rows = [
        {"name": r[name_label], "pct": r["Allocation %"], "budget": r["Budget (Can$K)"]}
        for r in edited.to_dict("records")
    ]
    if apply_level_edits(items, rows, parent_budget):
        _bump()
    slack_strip(items, key)


def overview(portfolio: Portfolio) -> None:
    st.subheader("Portfolio allocation")
    st.caption(
        "Edit a brand's allocation % or its budget; a budget edit is converted back "
        "to a percentage of the portfolio budget (set in the sidebar)."
    )
    level_editor(portfolio.brands, portfolio.value, "brands", "Brand")

    add_col, remove_col = st.columns(2)
    if add_col.button("Add brand"):
        portfolio.brands.append(new_brand(portfolio))
        _bump()
    if portfolio.brands:
        by_id = {b.id: b.name for b in portfolio.brands}
        chosen = remove_col.selectbox(
            "Remove brand", list(by_id), format_func=by_id.get, key="remove_choice"
        )
        if remove_col.button("Remove selected brand"):
            remove_brand(portfolio, chosen)
            _bump()

    with st.expander("Full budget tree (read-only)"):
        rows = []
        for brand in portfolio.brands:
            rows.append((brand.name, "", "", brand.value, brand_budget(portfolio, brand)))
            for cat in brand.categories:
                rows.append(
                    (brand.name, cat.name, "", cat.value, cat_budget(portfolio, brand, cat))
                )
                for seg in cat.segments:
                    rows.append(
                        (
                            brand.name,
                            cat.name,
                            seg.name,
                            seg.value,
                            seg_budget(portfolio, brand, cat, seg),
                        )
                    )
        st.dataframe(
            pd.DataFrame(
                rows,
                columns=["Brand", "Category", "Segment", "Allocation %", "Budget (Can$K)"],
            ),
            hide_index=True,
            width="stretch",
        )


def brand_tab(portfolio: Portfolio, brand) -> None:
    budget = brand_budget(portfolio, brand)
    st.subheader(brand.name)
    st.caption(f"{brand.value:.2f}% of the portfolio · Can${budget:,.0f}K")
    level_editor(brand.categories, budget, f"cats_{brand.id}", "Category")

    for cat in brand.categories:
        cat_b = cat_budget(portfolio, brand, cat)
        flag = "" if abs(level_total(cat.segments) - 100) <= TOLERANCE else "⚠ "
        with st.expander(
            f"{flag}{cat.name} — segments ({cat.value:.2f}% · Can${cat_b:,.0f}K)"
        ):
            level_editor(cat.segments, cat_b, f"segs_{cat.id}", "Segment")


def _results_editor(portfolio: Portfolio, specs: list[dict], key: str, sort_by_score: bool):
    results = [sum_results(portfolio, s["seg_ids"]) for s in specs]
    ranks = dense_rank(results)
    order = list(range(len(specs)))
    if sort_by_score:
        order.sort(key=lambda i: (ranks[i] is None, ranks[i] or 0))

    df = pd.DataFrame(
        {
            "Name": [specs[i]["name"] for i in order],
            "Budget (Can$K)": [specs[i]["budget"] for i in order],
            "Result (Can$K)": [results[i] for i in order],
            "Var (Can$K)": [
                None if results[i] is None else results[i] - specs[i]["budget"]
                for i in order
            ],
            "Score": [None if ranks[i] is None else f"#{ranks[i]}" for i in order],
        }
    )
    edited = st.data_editor(
        df,
        key=f"{key}_{st.session_state.ver}",
        hide_index=True,
        num_rows="fixed",
        width="stretch",
        disabled=["Name", "Budget (Can$K)", "Var (Can$K)", "Score"],
        column_config={
            "Budget (Can$K)": st.column_config.NumberColumn(format="%.1f"),
            "Result (Can$K)": st.column_config.NumberColumn(min_value=0.0, format="%.1f"),
            "Var (Can$K)": st.column_config.NumberColumn(format="%+.1f"),
        },
    )

    changed = False
    for pos, i in enumerate(order):
        new = edited["Result (Can$K)"].iloc[pos]
        old = results[i]
        if _is_blank(new) != (old is None) or (
            not _is_blank(new) and abs(float(new) - old) > 1e-6
        ):
            if _is_blank(new):
                for seg_id in specs[i]["seg_ids"]:
                    portfolio.results.pop(seg_id, None)
            else:
                set_seg_results(portfolio, specs[i]["seg_ids"], float(new))
            changed = True
    if changed:
        _bump()


def _csv_import(portfolio: Portfolio) -> None:
    with st.expander("Import results from CSV", expanded=False):
        st.caption(
            "Columns: Brand, Category, Segment, Result (Can$K). Blank Segment spreads "
            "the value across the category; blank Category and Segment spreads it "
            "across the brand. Importing replaces the affected results, so importing "
            "the same file twice changes nothing."
        )
        uploaded = st.file_uploader("CSV file", type="csv", key="results_csv")
        if uploaded is None:
            return
        try:
            report = parse_results_csv(uploaded.getvalue(), portfolio)
        except ValueError as exc:
            st.error(str(exc))
            return
        st.write(
            f"{report.applied_rows} row(s) ready · {len(report.results)} segment(s) affected"
        )
        for error in report.errors:
            st.warning(error)
        if st.button("Apply import", disabled=not report.results):
            portfolio.results.update(report.results)
            _bump()


def results_tab(portfolio: Portfolio) -> None:
    st.subheader("Results")
    st.caption(
        "Enter actual spend in Can$K. A category or brand result is spread evenly "
        "across its segments. Score is the dense rank by Result (#1 = highest)."
    )
    _csv_import(portfolio)

    top = st.columns([2, 1, 1])
    names = {b.id: b.name for b in portfolio.brands}
    brand_filter = top[0].selectbox(
        "Brand filter", ["all", *names], format_func=lambda x: "All brands" if x == "all" else names[x]
    )
    sort_by_score = top[1].checkbox("Sort by Score")
    if top[2].button("Clear all results", disabled=not portfolio.results):
        portfolio.results.clear()
        _bump()

    brands = [b for b in portfolio.brands if brand_filter in ("all", b.id)]
    brand_specs = [
        {
            "name": b.name,
            "budget": brand_budget(portfolio, b),
            "seg_ids": brand_seg_ids(b),
        }
        for b in brands
    ]
    cat_specs = [
        {
            "name": f"{b.name} › {c.name}",
            "budget": cat_budget(portfolio, b, c),
            "seg_ids": cat_seg_ids(c),
        }
        for b in brands
        for c in b.categories
    ]
    seg_specs = [
        {
            "name": f"{b.name} › {c.name} › {s.name}",
            "budget": seg_budget(portfolio, b, c, s),
            "seg_ids": [s.id],
        }
        for b in brands
        for c in b.categories
        for s in c.segments
    ]

    brand_tab_, cat_tab, seg_tab = st.tabs(["Brands", "Categories", "Segments"])
    with brand_tab_:
        _results_editor(portfolio, brand_specs, "res_brands", sort_by_score)
    with cat_tab:
        _results_editor(portfolio, cat_specs, "res_cats", sort_by_score)
    with seg_tab:
        _results_editor(portfolio, seg_specs, "res_segs", sort_by_score)


def _suggestion(ratio: float | None) -> str:
    if ratio is None:
        return "—"
    if ratio >= OVER_TARGET:
        return "Over target: consider increasing"
    if ratio <= UNDER_TARGET:
        return "Under target: consider reducing"
    return "On target: hold"


def report_tab(portfolio: Portfolio) -> None:
    st.subheader("Report")
    problems = imbalanced_levels(portfolio)
    if problems:
        st.warning(
            "Some levels do not sum to 100%, so budgets below are not fully allocated:\n\n"
            + "\n".join(f"- {p}" for p in problems)
        )

    chart_col, radar_col = st.columns([3, 2])
    with chart_col:
        st.markdown("**Allocation sunburst** — brands → categories → segments")
        st.plotly_chart(sunburst_figure(portfolio), width="stretch")
        st.caption(
            "Arc width = budget share. Brightness = result ÷ budget: very dark 0%, "
            "medium ~100%, bright 150%+. Full brand colour = no result entered."
        )
    with radar_col:
        st.markdown("**Brand radar** — share of portfolio")
        st.plotly_chart(radar_figure(portfolio), width="stretch")

    rows = flatten(portfolio)
    ranks = dense_rank([r.result for r in rows])
    table = pd.DataFrame(
        {
            "Brand": [r.brand.name for r in rows],
            "Category": [r.cat.name for r in rows],
            "Segment": [r.seg.name for r in rows],
            "Allocation %": [r.seg.value for r in rows],
            "Budget (Can$K)": [r.budget for r in rows],
            "Result (Can$K)": [r.result for r in rows],
            "% of target": [target_ratio(r.budget, r.result) for r in rows],
            "Var (Can$K)": [None if r.result is None else r.result - r.budget for r in rows],
            "Score": [None if k is None else f"#{k}" for k in ranks],
            "Suggestion": [_suggestion(target_ratio(r.budget, r.result)) for r in rows],
        }
    )

    f1, f2 = st.columns(2)
    brand_options = ["All brands", *dict.fromkeys(table["Brand"])]
    brand_pick = f1.selectbox("Filter by brand", brand_options, key="report_brand")
    if brand_pick != "All brands":
        table = table[table["Brand"] == brand_pick]
    cat_options = ["All categories", *dict.fromkeys(table["Category"])]
    cat_pick = f2.selectbox("Filter by category", cat_options, key="report_cat")
    if cat_pick != "All categories":
        table = table[table["Category"] == cat_pick]

    def color_var(value):
        if _is_blank(value):
            return ""
        return "color: #4ade80" if value >= 0 else "color: #f87171"

    styled = table.style.format(
        {
            "Allocation %": "{:.2f}",
            "Budget (Can$K)": "{:,.1f}",
            "Result (Can$K)": "{:,.1f}",
            "% of target": "{:.0%}",
            "Var (Can$K)": "{:+,.1f}",
        },
        na_rep="—",
    ).map(color_var, subset=["Var (Can$K)"])
    st.dataframe(styled, hide_index=True, width="stretch")
    st.caption(
        f"Suggestions are a simple rule: ≥{OVER_TARGET:.0%} of target → increase, "
        f"≤{UNDER_TARGET:.0%} → reduce, otherwise hold."
    )
