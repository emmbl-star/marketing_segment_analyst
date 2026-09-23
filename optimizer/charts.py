from __future__ import annotations

import plotly.graph_objects as go

from .model import (
    Portfolio,
    brand_budget,
    brand_seg_ids,
    cat_budget,
    cat_seg_ids,
    dense_rank,
    seg_budget,
    sum_results,
    target_ratio,
)

BRAND_COLORS = [
    "#4ade80",
    "#60a5fa",
    "#f472b6",
    "#fbbf24",
    "#a78bfa",
    "#f87171",
    "#34d399",
    "#22d3ee",
]
TEXT = "#e8eaf0"
MUTED = "#6b7280"
BORDER = "#2a2f3d"


def brand_color(index: int) -> str:
    return BRAND_COLORS[index % len(BRAND_COLORS)]


def shade(hex_color: str, ratio: float | None) -> str:
    """Brightness encodes result / budget: dark at 0, medium at 1, bright at 1.5+.

    No result entered keeps the full brand colour.
    """
    if ratio is None:
        factor = 1.0
    elif ratio <= 1:
        factor = 0.15 + 0.55 * max(ratio, 0.0)
    else:
        factor = min(1.0, 0.70 + 0.60 * (ratio - 1))
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    return f"#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}"


def _hover(name, alloc, budget, result, rank) -> str:
    ratio = target_ratio(budget, result)
    lines = [f"<b>{name}</b>", f"Allocation: {alloc:.1f}%", f"Budget: Can${budget:,.0f}K"]
    if result is None:
        lines.append("Result: not entered")
    else:
        lines += [
            f"Result: Can${result:,.0f}K",
            f"% of target: {ratio:.0%}" if ratio is not None else "% of target: n/a",
            f"Var: {result - budget:+,.0f}K",
            f"Score: #{rank}",
        ]
    return "<br>".join(lines)


def sunburst_figure(portfolio: Portfolio) -> go.Figure:
    ids, labels, parents, values, colors, hovers = [], [], [], [], [], []

    brand_results = [sum_results(portfolio, brand_seg_ids(b)) for b in portfolio.brands]
    brand_ranks = dense_rank(brand_results)
    all_cats = [(b, c) for b in portfolio.brands for c in b.categories]
    cat_results = [sum_results(portfolio, cat_seg_ids(c)) for _, c in all_cats]
    cat_ranks = dict(zip((c.id for _, c in all_cats), dense_rank(cat_results)))
    cat_result_by_id = dict(zip((c.id for _, c in all_cats), cat_results))
    all_segs = [(b, c, s) for b, c in all_cats for s in c.segments]
    seg_results = [portfolio.results.get(s.id) for _, _, s in all_segs]
    seg_ranks = dict(zip((s.id for _, _, s in all_segs), dense_rank(seg_results)))

    for bi, brand in enumerate(portfolio.brands):
        base = brand_color(bi)
        budget = brand_budget(portfolio, brand)
        result = brand_results[bi]
        ids.append(brand.id)
        labels.append(brand.name)
        parents.append("")
        values.append(0)
        colors.append(shade(base, target_ratio(budget, result)))
        hovers.append(_hover(brand.name, brand.value, budget, result, brand_ranks[bi]))

        for cat in brand.categories:
            budget = cat_budget(portfolio, brand, cat)
            result = cat_result_by_id[cat.id]
            ids.append(cat.id)
            labels.append(cat.name)
            parents.append(brand.id)
            values.append(0)
            colors.append(shade(base, target_ratio(budget, result)))
            hovers.append(_hover(cat.name, cat.value, budget, result, cat_ranks[cat.id]))

            for seg in cat.segments:
                budget = seg_budget(portfolio, brand, cat, seg)
                result = portfolio.results.get(seg.id)
                ids.append(seg.id)
                labels.append(seg.name)
                parents.append(cat.id)
                values.append(max(budget, 0))
                colors.append(shade(base, target_ratio(budget, result)))
                hovers.append(_hover(seg.name, seg.value, budget, result, seg_ranks[seg.id]))

    fig = go.Figure(
        go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="remainder",
            marker=dict(colors=colors, line=dict(color="#0d0f12", width=1)),
            hovertext=hovers,
            hoverinfo="text",
            insidetextorientation="radial",
        )
    )
    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT),
        height=620,
    )
    return fig


def radar_figure(portfolio: Portfolio) -> go.Figure:
    names = [b.name for b in portfolio.brands]
    values = [b.value for b in portfolio.brands]
    fig = go.Figure()
    if names:
        even = 100 / len(names)
        closed = names + names[:1]
        fig.add_trace(
            go.Scatterpolar(
                r=values + values[:1],
                theta=closed,
                fill="toself",
                name="Allocation",
                line=dict(color=BRAND_COLORS[0]),
                fillcolor="rgba(74, 222, 128, 0.25)",
                hovertemplate="%{theta}: %{r:.1f}%<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=[even] * len(closed),
                theta=closed,
                mode="lines",
                name="Equal split",
                line=dict(color=MUTED, dash="dash"),
                hovertemplate="Equal split: %{r:.1f}%<extra></extra>",
            )
        )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(ticksuffix="%", gridcolor=BORDER, linecolor=BORDER),
            angularaxis=dict(gridcolor=BORDER, linecolor=BORDER),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT),
        legend=dict(orientation="h", y=-0.1),
        margin=dict(t=30, l=40, r=40, b=40),
        height=460,
    )
    return fig
