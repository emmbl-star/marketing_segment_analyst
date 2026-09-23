---
name: design-tokens-sync
description: Check that the design tokens (colours) are identical in docs/PORTFOLIO_OPTIMIZER.md, .streamlit/config.toml and the hard-coded colours in optimizer/*.py, report any drift, and fix the code to match the spec. Use after touching colours, the theme or charts, or when asked to sync/check design tokens.
---

# Sync design tokens

The colour tokens exist in three places. **The spec is the source of truth**; code follows it unless the owner says the spec should change.

## Where each token lives

| Token | Spec (`docs/PORTFOLIO_OPTIMIZER.md`, "Design tokens" block) | `.streamlit/config.toml` `[theme]` | Hard-coded in code |
|---|---|---|---|
| `--bg` | `#0d0f12` | `backgroundColor` | `optimizer/charts.py`: sunburst `marker.line.color` |
| `--surface` | `#151820` | `secondaryBackgroundColor` | — |
| `--surface-2` | `#1d2130` | — (no Streamlit equivalent) | — |
| `--border` | `#2a2f3d` | — | `charts.py`: `BORDER` |
| `--text` | `#e8eaf0` | `textColor` | `charts.py`: `TEXT` |
| `--muted` | `#6b7280` | — | `charts.py`: `MUTED` |
| `--accent` | `#4ade80` | `primaryColor` | `charts.py`: `BRAND_COLORS[0]`, radar `fillcolor` (`rgba(74, 222, 128, …)`), `views.py`: `color_var` (positive) |
| `--danger` | `#f87171` | — | `views.py`: `color_var` (negative) |
| `--warning` | `#fbbf24` | — | `charts.py`: `BRAND_COLORS` (amber entry). Warnings otherwise use Streamlit's built-in `st.warning` |

If a file in this table has moved or a token gained a new usage, update this table as part of the run.

## Steps

1. **Read the spec block**: `sed -n '/^## Design tokens/,/^---/p' docs/PORTFOLIO_OPTIMIZER.md`. Build the token → hex map from it.
2. **Read the theme**: `.streamlit/config.toml`.
3. **Find hard-coded colours** in code: `grep -nE '#[0-9a-fA-F]{6}|rgba?\(' optimizer/*.py app.py`.
4. **Compare** against the table above, case-insensitively. Flag:
   - a mapped location whose hex differs from the spec (*drift*);
   - a hex in code that is not a spec token and not a brand-palette colour (`BRAND_COLORS` in `charts.py` is allowed to hold extra series colours, but its first entry must equal `--accent`);
   - an `rgba(...)` whose RGB no longer matches `--accent` (ignore the transparent `rgba(0,0,0,0)` used for chart backgrounds);
   - a `BRAND_COLORS` entry equal to `--danger` (currently the red `#f87171`): a brand shaded like a negative variance is confusing. Report it as a design smell, do not change it without the owner;
   - a token in the spec with no known usage, other than `--surface-2` and `--warning` (expected).
5. **Report** a short table: token, spec value, where it differs, found value.
6. **Fix**: for drift, edit the *code* to match the spec (smallest change: a hex, not a refactor). If the owner says the *spec* is wrong, edit the spec block and `.streamlit/config.toml` and the code together, and add an entry to `docs/DECISIONS.md`.
7. **Verify** with `python -m pytest -q` (the app smoke tests render every view). If pytest is missing, say so instead of skipping silently.
8. **Do not commit, push or switch branches.** End with a one-line reminder to commit to the current branch (not `main`, which redeploys production).

## Notes

- Streamlit's theme cannot express `--surface-2`, `--border`, `--muted`, `--danger` or `--warning`; do not try to force them into `config.toml`.
- Do not introduce new colours without adding them to the spec's token block first.
