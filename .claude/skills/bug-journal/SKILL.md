---
name: bug-journal
description: Update docs/BUG_JOURNAL.md with today's bugs (from git history, uncommitted changes and this session), then remind the owner to push to their current branch (never main). Use daily around 3pm on days the repo was worked on, or when asked to update the bug journal.
---

# Update the bug journal

Goal: keep `docs/BUG_JOURNAL.md` accurate, without inventing anything and without touching git history.

## Steps

1. **Check there was work today.** Run `git log --since=midnight --oneline`, `git status --short` and `git diff --stat`. If there are no commits and no changes today, say "No activity today, journal unchanged." and stop.
2. **Read** `docs/BUG_JOURNAL.md` (format and the highest existing `BUG-###` number) and, if it exists, `docs/DECISIONS.md`.
3. **Collect candidate bugs** from: today's commit messages and diffs (`git log -p --since=midnight`), the uncommitted diff, failing or newly added tests, and anything the current session diagnosed or fixed. A bug is a defect with a symptom and a root cause, including test-tooling and process errors that cost time. Feature work and refactors are not bugs.
4. **Deduplicate.** Skip anything already in the journal (match by title, commit hash or root cause). If an existing entry's status changed (for example *fixed, uncommitted* is now committed), update that entry's status and commit hash instead of adding a new one.
5. **Write entries** under a heading for today's date (`## YYYY-MM-DD`, newest day first; create it if missing). Continue numbering from the highest `BUG-###`. Use exactly this shape:

   ```
   ### BUG-### — short title
   - **Status:** fixed (`abc1234`) | fixed, uncommitted | open
   - **Symptom:** what was observed
   - **Root cause:** why it happened
   - **Fix:** what changed
   - **Prevention:** what stops it coming back
   ```

   Only state facts you verified from git, the code or the session. If the root cause is unknown, say so and mark the entry *open*.
6. **Do not commit, stage, push or create branches.** Only edit `docs/BUG_JOURNAL.md`. Pushing straight to `main` is bad practice here because it redeploys production.
7. **Finish with a push reminder.** Run `git branch --show-current`, `git status --short` and `git rev-list --count @{u}..HEAD` (ignore an error if there is no upstream), then fill in real values:

   - **On a feature branch** (anything other than `main`/`master`):

     > Journal updated: N new / M changed entries.
     > Reminder: commit and push to your current branch `<branch>` (K uncommitted files, U unpushed commits): `git push -u origin <branch>`.

   - **On `main`/`master`:**

     > Journal updated: N new / M changed entries.
     > Reminder: you are on `main`, so do not push there — a push to `main` redeploys production. Create a branch first: `git switch -c <suggested-branch-name>`, commit today's work (including the journal), then `git push -u origin <suggested-branch-name>` and open a pull request.

   Suggest a branch name from today's work (for example `feature/streamlit-optimizer-port`). Never run `git push`, `git commit` or `git switch` yourself; the reminder is all you do.
