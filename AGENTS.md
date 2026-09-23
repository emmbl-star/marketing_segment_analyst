# marketing_segment_analyst — agent briefing

> **Status: current.** Verified against the repo and the Streamlit Cloud deploy logs on 2026-09-23. If this file disagrees with the code, trust the code and fix this file.

**Which doc is authoritative for what:** product behaviour → [docs/PORTFOLIO_OPTIMIZER.md](docs/PORTFOLIO_OPTIMIZER.md); repo layout, commands and deployment → this file; the React prototype's tooling → [docs/FIGMA_MAKE.md](docs/FIGMA_MAKE.md) (reference only, its source is not in this repo); why something is the way it is → [docs/DECISIONS.md](docs/DECISIONS.md); past defects → [docs/BUG_JOURNAL.md](docs/BUG_JOURNAL.md).

## What this project is

A portfolio project: a **Portfolio Allocation Optimizer** for marketing budgets, split across Portfolio → Brands → Categories → Segments, with actual results compared against budget. It is implemented as a Streamlit app (`app.py` + `optimizer/`) and deployed on Streamlit Community Cloud.

- Repo: `github.com/emmbl-star/marketing_segment_analyst` (branch `main`)
- Live app: `marketseg-analyst.streamlit.app` (redeploys on every push to `main`)
- State is in-memory (`st.session_state`); there is no database or backend.
- UI text is English. The owner works in French and English.

## Layout

| Path | State | Purpose |
|---|---|---|
| `app.py` | working | Streamlit entry point: page config, sidebar, view switcher. **Must stay at the repo root** (Streamlit Cloud, devcontainer and Makefile reference it) |
| `optimizer/model.py` | working | Dataclasses, default portfolio, budget cascade, validation, slack redistribution, table-edit logic, ranking. No Streamlit imports |
| `optimizer/csv_import.py` | working | Results CSV parser (replace semantics). No Streamlit imports |
| `optimizer/charts.py` | working | Plotly sunburst and radar |
| `optimizer/views.py` | working | All Streamlit rendering: overview, brand tabs, results, report |
| `tests/` | working | pytest suite: model, CSV import, and AppTest smoke tests |
| `.streamlit/config.toml` | working | Dark theme built from the design tokens |
| `docs/PORTFOLIO_OPTIMIZER.md` | spec | Product spec, Streamlit deviations, open questions |
| `docs/FIGMA_MAKE.md` | reference | Figma Make React prototype: stack, build, structure, rules |
| `docs/DECISIONS.md` | living | Why each non-obvious choice was made; marks which are provisional |
| `docs/BUG_JOURNAL.md` | living | Every defect with symptom, root cause, fix, prevention |
| `.claude/skills/bug-journal/` | working | `/bug-journal`: updates the journal and reminds to push to the current branch (never `main`) |
| `.claude/skills/design-tokens-sync/` | working | `/design-tokens-sync`: keeps colours identical across the spec, `.streamlit/config.toml` and `optimizer/*.py` |
| `.claude/skills/spec-sync/` | working | `/spec-sync`: reconciles the spec, `DECISIONS.md` and this file with the code, and logs new decisions |
| `agents/`, `gcp/`, `utils/` | empty | `__init__.py` only; unused placeholders. Do not fill them without a feature that needs them |
| `docker/Dockerfile` | empty | Not used by the deploy |
| `raw_data/` | git-ignored | Local datasets; never commit |
| `.devcontainer/devcontainer.json` | working | Python 3.11 dev container running `streamlit run app.py` on 8501 |
| `requirements.txt`, `requirements-dev.txt` | working | Runtime deps (Streamlit Cloud installs this one); dev adds pytest |

## Commands

```bash
cp .env.example .env               # ANTHROPIC_API_KEY is listed but currently unused
make install_dev_requirements      # runtime + pytest
make streamlit                     # http://localhost:8501
make pytest                        # python -m pytest -q
make clean                         # remove __pycache__ dirs
```

Test with `streamlit.testing.v1.AppTest`: drive views with `at.session_state["view"] = "results"` (the view switcher is a `st.segmented_control`, which `AppTest` can't `set_value` on). `AppTest` cannot edit `st.data_editor` cells, so editing logic is tested through the pure functions in `optimizer/model.py` instead.

## Architecture notes

- **Keep logic out of `views.py`.** Anything testable (math, parsing, validation) belongs in `model.py` / `csv_import.py`.
- **`data_editor` edit loop:** each level editor is keyed with `st.session_state.ver`. After applying edits to the model, call `_bump()` (increments `ver`, then `st.rerun()`) so the editor resets against the new data. Without the bump, edits are re-applied on top of already-updated data.
- **Results are keyed by segment id** in `portfolio.results`. Category and brand results are derived sums; editing them distributes evenly across segments.
- **Validation never blocks.** Levels not summing to 100% show a warning and a suggestion strip; budgets use the raw percentages.

## Configuration

- `ANTHROPIC_API_KEY` is the only variable in `.env.example` and nothing reads it yet.
- Git-ignored: `.env`, `.env.yaml`, `.envrc`, `raw_data/`, `trash/`, `.python-version`. Never commit secrets.
- `.python-version` contains `marketing_segment_analyst` (a pyenv virtualenv name, not a Python version).

## Dependencies

`requirements.txt` is deliberately unpinned. The app uses `streamlit`, `pandas` and `plotly` (and `numpy` through pandas). `anthropic`, `joblib`, `huggingface-hub`, `requests`, `python-dotenv` and `scikit-learn` are **currently unused**; they slow every deploy and each one is another wheel that must exist for Python 3.14.

## Deployment gotchas

- **Streamlit Cloud runs Python 3.14.x** (seen: 3.14.7); the devcontainer uses 3.11 and local tests may run on another version. A dependency without a 3.14 wheel is built from source and the deploy hangs on "your app is in the oven". `scikit-learn==1.6.1` did this and the pin was removed. **Do not pin packages without checking they publish wheels for 3.14.**
- The main file path (`app.py`) is set when the app is created and cannot be edited afterwards. Moving the entry point means deleting and redeploying the app.
- Streamlit Cloud auto-swaps `pyarrow` 25 for 24 (known segfault); that log line is expected.
- A healthy deploy log ends with `Uvicorn server started on :::8501`.
- Pushing to `main` redeploys production, so confirm with the owner before pushing.

## Conventions and pitfalls

- Do not create a directory named `streamlit/` (it shadows the package).
- Do not nest a git repository inside this one. An accidental nested clone and a stray file named `\001` were removed in commit `3fb2a01`.
- Keep changes small and match the existing style. Commit subjects are short and imperative.
- When you change behaviour, update `docs/PORTFOLIO_OPTIMIZER.md` (deviations or open questions) in the same change.
