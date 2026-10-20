---
description: "The supported Python policy (floor 3.11, every CPython not at end of life) and the four places a Python version number lives. Read when checking or changing where a Python version number is written, or when those numbers disagree."
---

# Python Versions

---

## 1. Policy

- **The floor is 3.11.** Code uses 3.11+ syntax.
- **The supported range is every CPython version not at end of life** (schedule: <https://devguide.python.org/versions/>). A few months' lag either way is fine.

---

## 2. Where each number lives

| Where | What it means |
| :--- | :--- |
| `pyproject.toml` `requires-python` | The supported range, for example `">=3.11,<4.0"` |
| `pyproject.toml` classifiers | One `Programming Language :: Python :: 3.x` per supported version |
| `.github/workflows/main.yml` `python-version` and `USING_COVERAGE` | Every supported version, tested in CI |
| `mise.toml` `[tools] python` | The one dev Python, for `.venv` and the Read the Docs build; must lie inside the range |

The dev Python is written only in `mise.toml`:

- `mise.toml` `[env]` sets `UV_PYTHON = "python"`, so every `uv venv` and `uv sync` run through mise uses the first `python` on PATH, which is the mise one. Without it, uv prefers its own managed Pythons and a global `~/.config/uv/.python-version` pin, and `uv sync` silently rebuilds `.venv` with that version.
- `.readthedocs.yml` reads `[tools] python` from `mise.toml` and passes it to `uv venv --python`. Its `build.tools.python` stays `"3"`: it only runs `pip install uv` and that lookup. So `[tools] python` must be a plain version such as `"3.12"`, never `"latest"` or a list.

uv resolves dependencies against `requires-python`, whatever the dev Python is.

When the range changes, change `requires-python`, the classifiers, and the CI matrix together, in one commit. Change the dev Python only if it falls outside the new range.
