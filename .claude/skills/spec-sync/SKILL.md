---
name: spec-sync
description: Reconcile docs/PORTFOLIO_OPTIMIZER.md, docs/DECISIONS.md and AGENTS.md with the code after a behaviour or structure change; find spec-vs-code drift and log new decisions. Use after changing optimizer/*.py, app.py or tests, or when asked to sync the spec or log a decision.
---

# Sync the spec, decisions and agent docs with the code

Direction: **the code is the truth for what exists; the docs must say so honestly.** Edit docs only. If the drift means the *code* is wrong, report it and stop; do not change code in this skill.

## Steps

1. **Find what changed.** `git status --short`, `git diff --stat`, and `git log --oneline main..HEAD` (or `--since=midnight` on `main`). Read the changed files under `optimizer/`, `app.py`, `tests/`.
2. **Verify the spec's checkable claims** against the code and report each mismatch:
   - `docs/PORTFOLIO_OPTIMIZER.md` "Streamlit port" table: every listed path exists.
   - "Tabs" table: every `views.*` function named exists in `optimizer/views.py`.
   - "Deviations" table: each listed deviation is still true, and no *new* deviation exists (a spec feature with no implementation, or a UI behaviour the spec does not mention).
   - "Open questions" table, column "Streamlit port currently": CSV import replaces (`csv_import.py` assigns per segment, never adds); brands are a dynamic list (`new_brand` / `remove_brand`); validation warns only (`imbalanced_levels`, `slack_strip`, no blocking); spread is proportional (`spread_slack`, button label); Score ranks by Result (`dense_rank` on results).
   - Suggestion thresholds in the spec (120% / 80%) equal `OVER_TARGET` / `UNDER_TARGET` in `views.py`.
   - `AGENTS.md` layout table: every path exists, and every new top-level file or folder is listed. Commands match the `Makefile`.
   - Every `D-##` referenced anywhere exists in `docs/DECISIONS.md`.
3. **Log decisions.** For each non-obvious choice made in the changes (a behaviour picked between alternatives, a feature deliberately not built, a dependency added or removed), append an entry to `docs/DECISIONS.md` using the existing shape: `## D-## — title`, then Decision / Why / Alternatives / Consequence as needed. Use the next free number, add a row to the Summary table, and set **Status: Provisional** unless the owner explicitly confirmed it in this session (then **Confirmed**). Do not rewrite or renumber existing entries; to reverse one, add a new entry that supersedes it and mark the old status *Superseded by D-##*.
4. **Update the docs** to match the code: deviations, open questions, layout table, commands. Keep the status headers accurate. Never remove an Open question unless the owner confirmed the decision; then move it into `DECISIONS.md` as Confirmed.
5. **Write the report**: N mismatches fixed, M decisions logged, and a list of items that need an owner decision (Provisional entries whose behaviour just changed).
6. **Do not commit, push or switch branches.** End with a one-line reminder to commit to the current branch (not `main`, which redeploys production).

## Notes

- Never invent a rationale. If the reason for a choice is unknown, write "Why: not recorded" and ask the owner.
- Keep entries short; the log is read by agents that start with no context.
- Bugs go in `docs/BUG_JOURNAL.md` via the `bug-journal` skill, not here.
