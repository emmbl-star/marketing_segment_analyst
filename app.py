import streamlit as st

from optimizer import views
from optimizer.model import default_portfolio

st.set_page_config(page_title="Portfolio Allocation Optimizer", page_icon="📊", layout="wide")


def reset() -> None:
    st.session_state.portfolio = default_portfolio()
    st.session_state.ver = st.session_state.get("ver", 0) + 1


if "portfolio" not in st.session_state:
    reset()

portfolio = st.session_state.portfolio

st.title("Portfolio Allocation Optimizer")
st.caption(
    "Portfolio → Brands → Categories → Segments. Each level's percentages should "
    "sum to 100%. State lives in your browser session and resets on reload."
)

with st.sidebar:
    portfolio.value = st.number_input(
        "Portfolio budget (Can$K)",
        min_value=0.0,
        value=float(portfolio.value),
        step=100.0,
        key="portfolio_value",
    )
    if st.button("Reset to defaults"):
        reset()
        st.rerun()

view_labels = {
    "overview": "Overview",
    **{b.id: b.name for b in portfolio.brands},
    "results": "Results",
    "report": "Report",
}
view = (
    st.segmented_control(
        "View",
        list(view_labels),
        format_func=view_labels.get,
        default="overview",
        key="view",
        label_visibility="collapsed",
    )
    or "overview"
)

if view == "overview":
    views.overview(portfolio)
elif view == "results":
    views.results_tab(portfolio)
elif view == "report":
    views.report_tab(portfolio)
else:
    brand = next((b for b in portfolio.brands if b.id == view), None)
    if brand is None:
        views.overview(portfolio)
    else:
        views.brand_tab(portfolio, brand)
