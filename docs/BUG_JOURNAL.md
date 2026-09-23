# Bug journal

> **Status: living document, newest day first.** Every real defect we hit, with symptom, root cause, fix and how to prevent it. Updated by the `bug-journal` skill (`/bug-journal`). Decisions that came out of a bug are in [DECISIONS.md](DECISIONS.md).

Entry format: `BUG-### — title`, then **Symptom**, **Root cause**, **Fix**, **Prevention**. Status is one of *fixed (commit)*, *fixed, uncommitted*, or *open*.

---

## 2026-09-23

### BUG-001 — Streamlit Cloud stuck on "your app is in the oven"
- **Status:** fixed (`31f62f6`)
- **Symptom:** after a push the deployed app sat on the loading screen for minutes; log stopped after `Resolved 62 packages`.
- **Root cause:** Streamlit Cloud builds with **Python 3.14.7**. `scikit-learn==1.6.1` has no wheel for 3.14, so `uv` tried to compile it from source.
- **Fix:** removed the pin. The next deploy resolved `scikit-learn 1.9.1` (has a 3.14 wheel), installed 62 packages in about 2 seconds, and the server started.
- **Prevention:** never pin a package without checking it publishes wheels for Python 3.14. Prune unused dependencies (`scikit-learn`, `anthropic`, `joblib`, `huggingface-hub`, `requests`, `python-dotenv` are unused). Read the Cloud log for the Python version first.

### BUG-002 — Repository embedded inside itself
- **Status:** fixed (`3fb2a01`)
- **Symptom:** `git ls-files` listed `marketing_segment_analyst` as a single entry (mode `160000`, a gitlink) and the folder contained its own `.git`, README and LICENSE.
- **Root cause:** the repo was cloned inside its own working tree and then committed with `git add`.
- **Fix:** untracked the gitlink and moved the clone out of the project (it only held the "Initial commit", already in the parent).
- **Prevention:** run `git status` after a broad `git add`; never clone into an existing working tree.

### BUG-003 — Empty file named `\001` committed
- **Status:** fixed (`3fb2a01`)
- **Symptom:** a blank-looking entry in `ls`; `git ls-files` showed `"\001"`, a 0-byte file whose name is a control character.
- **Root cause:** accidental `touch` with a stray keystroke, swept in by `git add .`.
- **Fix:** `git rm --cached` and deleted the file.
- **Prevention:** stage files by name; check `git status` before committing.

### BUG-004 — Entry point in the wrong place; Makefile and devcontainer pointed at a missing file
- **Status:** fixed (`3fb2a01`)
- **Symptom:** `make streamlit` and the devcontainer ran `streamlit run app.py`, but the only app was `streamlit/app.py`. The commit "Move app.py to root directory for Streamlit Cloud" did not match the tree. The Makefile also carried dead targets (`install` without a `setup.py`, `clean` removing a non-existent `model.joblib`, a Heroku heading).
- **Root cause:** file moved to a directory named `streamlit/` (which also shadows the `streamlit` package) and template Makefile content never adapted.
- **Fix:** moved `streamlit/app.py` to `app.py`; rewrote the Makefile; removed the empty directories.
- **Prevention:** keep the entry point at the root (D-02); never name a folder after an imported package.

### BUG-005 — Wrong advice about Streamlit Cloud's "Main file path" (process error)
- **Status:** closed (no code impact)
- **Symptom:** I told you to change **Main file path** under Settings → General; the field was not there.
- **Root cause:** that path is set when the app is created and is not editable afterwards; I stated it as fact without verifying.
- **Fix:** checked the app list instead, which showed `marketing_segment_analyst · main · app.py`, so nothing needed changing.
- **Prevention:** verify platform UI claims (or say they are unverified) before giving step-by-step instructions.

### BUG-006 — `.gitignore` had lost its Python entries
- **Status:** fixed, uncommitted
- **Symptom:** running the tests would have left `__pycache__/` and `.pytest_cache/` as untracked files.
- **Root cause:** commit `129b2e7` ("Add raw_data to .gitignore") replaced the 218-line template with a single line.
- **Fix:** appended `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.venv/`.
- **Prevention:** edit `.gitignore` by appending, and review the diff before committing.

### BUG-007 — Charts crashed: wrong argument passed to `sum_results`
- **Status:** fixed, uncommitted (caught before first run)
- **Symptom:** `sum_results(portfolio.results, …)` in `optimizer/charts.py` passed the results dict where a `Portfolio` is expected, which would fail with an `AttributeError` when the Report tab rendered.
- **Root cause:** signature mismatch between `optimizer/model.py` and its caller.
- **Fix:** pass `portfolio`.
- **Prevention:** the AppTest smoke test renders every view (including Report), so this class of error is now caught by `make pytest`.

### BUG-008 — CSV import rejected a file starting with a BOM
- **Status:** fixed, uncommitted
- **Symptom:** `parse_results_csv` raised `Missing column(s): Brand` for text starting with the UTF-8 byte-order mark (Excel exports add one).
- **Root cause:** the BOM was only stripped when the input was `bytes`, not for `str`.
- **Fix:** always strip a leading `\ufeff`. The test file also contained a *literal* invisible BOM character, replaced with the `\ufeff` escape so it is visible in review.
- **Prevention:** unit test `test_matching_is_case_insensitive_and_bom_tolerant`; avoid pasting invisible characters into source.

### BUG-009 — Smoke test could not find the view selector
- **Status:** fixed, uncommitted
- **Symptom:** `IndexError` in `tests/test_app.py`: `at.get("segmented_control")` returned nothing, and `set_value` on the control raised `TypeError`.
- **Root cause:** `AppTest` exposes the control as `at.segmented_control` / `button_group` and its `set_value` does not work with custom `format_func` labels in this Streamlit version.
- **Fix:** drive views through `at.session_state["view"]`.
- **Prevention:** documented in `AGENTS.md` ("Commands").

### BUG-010 — Contradictions in the product spec
- **Status:** open (provisional choices made; see D-06 to D-10)
- **Symptom:** the spec said CSV import both "sets" and "accumulates"; tabs are "Brand A–E" but brands can be added/removed; "Spread evenly" is described as proportional; the 100% rule has no defined failure behaviour; Score ranks by absolute spend.
- **Root cause:** the spec was written from a prototype without reconciling the sections.
- **Fix:** the Streamlit port picked one behaviour each and lists them under "Open questions" in `PORTFOLIO_OPTIMIZER.md`.
- **Prevention:** confirm or change the provisional decisions; update spec and code together.

### Watch list (not bugs)
- Streamlit Cloud replaces `pyarrow` 25 with 24 during install (known segfault upstream). Expected log line; no action.
- The Streamlit port has not been clicked through in a browser; `st.data_editor` edits are only covered by unit tests of the underlying logic.
