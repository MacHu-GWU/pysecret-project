---
description: "The release sequence from a finished change to PyPI and a GitHub tag and release: who does each step, the publish and release tasks, and the approval gate before each public step. Read when publishing a new version."
---

# Release

---

## 1. Sequence

| Step | Who | How |
| :--- | :--- | :--- |
| 1. Bump the version (`21-versioning-and-changelog.md`) | AI, after the user's yes on the number | edit `pyproject.toml`, then `mise run inst` |
| 2. Write that version's changelog section | AI | `21-versioning-and-changelog.md` |
| 3. Verify | AI | `mise run cov`, `mise run lint`, `mise run build-doc` all pass |
| 4. Commit and push to `main` | AI, after the user's yes | git |
| 5. Publish to PyPI | AI, after the user's yes | `mise run publish` (builds, then `uv publish` with `PYPI_TOKEN`) |
| 6. Create the GitHub tag and release | AI, after the user's yes | `mise run release` (idempotent) |

---

## 2. Rules

- **Steps 5 and 6 are irreversible and public.** One yes per step (`03-mise.md` section 3): a yes to publish is not a yes to release.
- **Never delete or move a published tag or PyPI release.** Fix a bad release with a new PATCH version.
- **A missing or rejected token** is reported by its variable name, and the release stops there (`01-secrets.md`).
