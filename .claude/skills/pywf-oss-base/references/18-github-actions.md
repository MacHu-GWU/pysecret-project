---
description: "The GitHub Actions workflow: the OS by Python matrix, each step and why (including the .venv cache key), triggers, keeping actions current, and diagnosing a red run from its log. Read when changing .github/workflows/main.yml, or when a CI run fails or shows warnings."
---

# GitHub Actions

---

## 1. The workflow: `.github/workflows/main.yml`

- **Matrix:** `ubuntu-latest` and `windows-latest`, times every supported Python (`04-python-versions.md`). A library must pass on both, which is why code uses `pathlib` and `path_enum` (`08-package-files.md`), never hard-coded `/` paths or shell-only commands.
- **Steps:**
  1. checkout;
  2. setup-python;
  3. setup-uv, with its own cache off, because the next step caches the whole `.venv`;
  4. restore the cached `.venv`, keyed on the OS, the **full** Python version from setup-python (such as 3.13.15, from `steps.setup-python.outputs.python-version`), and the hash of `uv.lock`;
  5. `uv sync --extra test`, **skipped on a cache hit** (the point of the cache);
  6. `uv run --extra test pytest tests --cov=<package_name> --cov-report=xml`;
  7. upload `coverage.xml` to Codecov, for the Python versions listed in `USING_COVERAGE`.
- **CI uses uv, not mise:** the `[env]` block of `mise.toml` reads local secrets the runner does not have (`01-secrets.md`).
- **Triggers** live in the `on:` block. A template-fresh repo may have only `workflow_dispatch`; enable `push` and `pull_request` on `main` once the repo is live.
- **Quick debugging:** the workflow keeps commented-out single-OS and single-version lines. Swap them in temporarily; never commit the narrowed matrix.

---

## 2. Keeping actions current

- Keep every action on its latest major version. Old majors first get warnings (a deprecated Node.js runtime, a removed input), then break.
- Use the floating major tag (`@v7`) when the action publishes one. setup-uv does not, so pin its full version (`@v10.3.0`).
- After any workflow change, read the run's **Annotations** panel: warnings appear there even on a green run.

---

## 3. Diagnosing a red run

Start from the log, never from a guess.

```bash
gh run list --limit 5                 # recent runs and their status
gh run view <run_id> --log-failed     # only the log lines of the failed steps
gh run rerun <run_id> --failed        # retry only the failed jobs (for flaky infrastructure)
gh workflow run main.yml              # start a run by hand (workflow_dispatch)
```

| Symptom | Usual cause | Fix |
| :--- | :--- | :--- |
| Fails only on `windows-latest` | Hard-coded `/` paths, shell-only commands, file encoding, or a file still open when it is deleted | `pathlib` / `path_enum`, `encoding="utf-8"`, and close files with `with` |
| Fails only on the newest Python | A dependency has no wheel for it yet, or a deprecated stdlib API was removed | Check the dependency's release notes. Cap the dependency, or wait before adding that Python to the matrix. |
| `uv sync` fails | `uv.lock` is out of date with `pyproject.toml` | Run `uv lock` locally, then commit `uv.lock` |
| Passes locally, fails in CI | It depends on local state: a file in `tmp/`, an environment variable, the working directory | Build the state inside the test (`tmp_path`, `path_enum`) |
| `Ignoring existing virtual environment linked to non-existent Python interpreter`, then `Failed to spawn: pytest` | A `.venv` cached under an older Python patch release points at a vanished interpreter, and `uv run` rebuilds it without the `test` extra | The full-version cache key and `uv run --extra test` (section 1) prevent this. In an older workflow, `gh cache delete --all`, then rerun. |
| Any other stale `.venv` | The cache key does not cover what changed | `gh cache delete --all`, then rerun |
