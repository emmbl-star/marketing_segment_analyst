# Decisions log

> **Status: living document.** One entry per non-obvious decision, so nobody (human or agent) has to reverse-engineer *why* from the code. Newest section last. **Provisional** means the assistant picked a default to keep building and the owner has not confirmed it yet; confirm or change it, then update the entry and the code together.

Legend: **Confirmed** = the owner asked for it or explicitly approved it. **Provisional** = assistant's pick, awaiting the owner.

## Summary

| ID | Decision | Status |
|---|---|---|
| D-01 | Port the optimizer to Streamlit | Confirmed |
| D-02 | `app.py` lives at the repo root | Confirmed |
| D-03 | Unpin `scikit-learn` to fix the deploy | Confirmed |
| D-04 | Remove the nested repo and the stray `\001` file | Confirmed |
| D-05 | Docs restructure (`docs/`, single stack source, status headers) | Confirmed |
| D-06 | CSV import **replaces** results | Provisional |
| D-07 | Brands are a **dynamic** list (five by default) | Provisional |
| D-08 | Validation **warns, never blocks** | Provisional |
| D-09 | "Spread" redistributes **proportionally** | Provisional |
| D-10 | Score ranks by absolute Result (as originally specified) | Provisional |
| D-11 | Report suggestions use a 120% / 80% of-target rule | Provisional |
| D-12 | View switcher instead of `st.tabs` | Assistant's call |
| D-13 | Logic separated from UI; editor-reset pattern | Assistant's call |
| D-14 | Some prototype features are not ported | Assistant's call |
| D-15 | Runtime vs dev requirements split | Assistant's call |
| D-16 | Bug journal + daily skill | Confirmed |

---

## D-01 — Port the optimizer to Streamlit
- **Decision:** build the Portfolio Allocation Optimizer in Streamlit (`app.py` + `optimizer/`), not as a separate React static site.
- **Why:** the repo, deployment (Streamlit Cloud) and dependencies are already Python/Streamlit; one deploy target instead of two.
- **Alternatives:** keep the Figma Make React prototype and deploy `dist/` separately (needs its own hosting and source in the repo).
- **Consequence:** the React source is not in this repo; `docs/FIGMA_MAKE.md` is reference only. Prototype features that have no Streamlit equivalent are listed in D-14.

## D-02 — `app.py` at the repo root
- **Decision:** entry point stays at `app.py` in the repo root; no `app/` folder.
- **Why:** the devcontainer, the Makefile and the Streamlit Cloud app (main file path shown as `app.py`) all point at the root. Renaming would have broken the deployment, whose main file path cannot be edited after creation.
- **Also avoided:** a `streamlit/` directory (it shadows the `streamlit` package).

## D-03 — Unpin `scikit-learn`
- **Decision:** remove `==1.6.1` from `requirements.txt`.
- **Why:** Streamlit Cloud runs Python 3.14.7, which has no wheel for 1.6.1, so the install compiled from source and hung. See BUG-001 in [BUG_JOURNAL.md](BUG_JOURNAL.md).
- **Open follow-up:** `scikit-learn`, `anthropic`, `joblib`, `huggingface-hub`, `requests` and `python-dotenv` are unused. Pruning them would be the cleaner fix; not done yet.

## D-04 — Remove nested repo and stray file
- **Decision:** untrack the `marketing_segment_analyst/` gitlink (an embedded clone containing only the "Initial commit") and the empty `\001` file.
- **Why:** the clone duplicated the parent's own first commit and the file was an accidental `touch`.
- **How:** the clone was **moved** to the session scratchpad rather than deleted (recoverable while that temp folder exists), then committed in `3fb2a01`.

## D-05 — Docs restructure
- **Decision:** specs live in `docs/`; the stack, build and env details exist only in `docs/FIGMA_MAKE.md`; every doc starts with a status header; `AGENTS.md` states which doc is authoritative for what.
- **Why:** the two spec files repeated the same stack facts, `DESIGN.md` was misnamed (it is tooling, not design), and docs described code that is not in the repo without saying so.

## D-06 — CSV import replaces (Provisional)
- **Contradiction in the spec:** "sets that specific segment" vs "importing twice accumulates".
- **Pick:** **replace** — each row sets its segments, so re-importing the same file changes nothing.
- **Alternatives:** accumulate (adds each import to existing values); a UI toggle to choose.
- **Revisit if:** you want to load results in several partial files that should add up.

## D-07 — Dynamic brand list (Provisional)
- **Contradiction:** tabs are "Brand A–E" but Overview can add/remove brands.
- **Pick:** dynamic; five brands by default, brand views follow the list. A new brand starts at 0% with one category and one segment at 100%.
- **Alternative:** fixed five brands, removing the add/remove buttons.

## D-08 — Validation warns, never blocks (Provisional)
- **Gap in the spec:** "each level must sum to 100%" without saying what happens otherwise.
- **Pick:** amber warning plus the suggestion strip; budgets are computed from the raw percentages; the Report tab lists every unbalanced level.
- **Alternatives:** block the edit; auto-normalize to 100%.
- **Why warn:** blocking makes multi-step edits (lower one, raise another) impossible; auto-normalizing silently changes numbers the user typed.

## D-09 — Proportional spread (Provisional)
- **Contradiction:** "Spread evenly" vs "distributes proportionally".
- **Pick:** proportional to current values (falls back to equal when all are zero); button labelled "Spread proportionally".

## D-10 — Score ranks by Result (Provisional)
- **Kept as specified:** dense rank by absolute Result descending.
- **Known weakness:** the segment with the biggest budget tends to rank first. Ranking by `Result ÷ Budget` would measure performance instead; that is a product decision, not a bug.

## D-11 — Suggestion rule (Provisional)
- **Gap:** the spec mentions a "suggestion engine" in the Report tab but never defines it.
- **Pick (assistant's invention):** ≥120% of target → "consider increasing"; ≤80% → "consider reducing"; otherwise "hold". Thresholds are constants in `optimizer/views.py` (`OVER_TARGET`, `UNDER_TARGET`).

## D-12 — Segmented control instead of `st.tabs`
- **Why:** Streamlit re-runs the whole script on every interaction and `st.tabs` renders every tab each time. With five brands that is roughly 35 editable tables per click. A segmented control renders only the active view.
- **Cost:** brand view names come from the brand list, and tests must drive it through `session_state["view"]`.

## D-13 — Logic separated from UI; editor-reset pattern
- Math, parsing and validation live in `optimizer/model.py` and `optimizer/csv_import.py` with no Streamlit imports, so they are unit-tested.
- Editable tables are keyed with `st.session_state.ver`; after applying edits the app bumps `ver` and reruns so the table resets against the updated model (otherwise the edit is applied twice).

## D-14 — Prototype features not ported
See the deviations table in [PORTFOLIO_OPTIMIZER.md](PORTFOLIO_OPTIMIZER.md#deviations-from-the-spec). In short: drag slider bar (no multi-handle slider in Streamlit), click-to-filter on the sunburst (replaced by dropdowns), radar category petals and vertex tooltips, DM Sans/DM Mono fonts, and per-level editing on the Overview tab (moved to brand views).

## D-15 — Runtime vs dev requirements
- `requirements.txt` is what Streamlit Cloud installs. `requirements-dev.txt` is `-r requirements.txt` plus `pytest`, for local development. Keeps test tooling out of the production deploy.

## D-16 — Bug journal and daily skill
- `docs/BUG_JOURNAL.md` records defects with symptom, root cause, fix and prevention. The `bug-journal` skill (`.claude/skills/bug-journal/`) updates it from git history and the day's work, and never commits or pushes by itself. It ends with a reminder to push to the **current branch**, and if you are on `main` it tells you to create a branch first, because a push to `main` redeploys production.
