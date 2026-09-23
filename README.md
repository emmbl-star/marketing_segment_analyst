# marketing_segment_analyst

Portfolio project: automating the analysis and optimization of marketing segments.

**Portfolio Allocation Optimizer** — split a marketing budget across **Portfolio → Brands → Categories → Segments**, enter actual campaign results, and compare them against budget.

- **Live app:** https://marketseg-analyst.streamlit.app (Streamlit Community Cloud, redeploys on every push to `main`)

## What it does

- Edit allocation percentages or budgets at every level, with a suggestion strip that redistributes whatever is left to reach 100%
- Enter results per segment, category or brand, or import them from a CSV
- Compare Result vs Budget (variance and rank)
- Report tab with a sunburst (brightness = % of target achieved), a brand radar, and a filterable segment table with simple over/under-target suggestions

State lives in the browser session and resets on reload. See [docs/PORTFOLIO_OPTIMIZER.md](docs/PORTFOLIO_OPTIMIZER.md) for the full spec, the list of differences from the original prototype, and open questions.

## Getting started

```bash
cp .env.example .env               # optional for now
make install_dev_requirements
make streamlit                     # http://localhost:8501
make pytest
```

## Documentation

| File | What it is | Read it when |
|---|---|---|
| [docs/PORTFOLIO_OPTIMIZER.md](docs/PORTFOLIO_OPTIMIZER.md) | Product spec: data model, budget formula, tabs, features, CSV format, design tokens, deviations of the Streamlit port, open questions | You want to know what the app should do |
| [docs/FIGMA_MAKE.md](docs/FIGMA_MAKE.md) | Reference for the original Figma Make React + Vite + Tailwind prototype (source not in this repo): stack, build, structure, rules | You are working on the React front-end |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Decision log: what was chosen, why, alternatives, and which choices are still provisional | You want the reasoning behind a choice, or need to confirm one |
| [docs/BUG_JOURNAL.md](docs/BUG_JOURNAL.md) | Journal of bugs: symptom, root cause, fix, prevention (kept up to date by the `/bug-journal` skill) | You hit a problem that may have happened before |
| [AGENTS.md](AGENTS.md) | Briefing for AI coding agents: layout, commands, architecture notes, deploy gotchas | You are an agent (or a person) changing this repo |

## Repo layout

- `app.py` — Streamlit entry point (must stay at the repo root)
- `optimizer/` — model, CSV import, charts and views
- `tests/` — pytest suite
- `docs/` — specs and reference docs
- `agents/`, `gcp/`, `utils/` — empty placeholders for planned work
- `raw_data/` — local datasets (git-ignored)
