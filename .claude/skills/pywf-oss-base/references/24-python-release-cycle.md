---
description: "The yearly Python routine: what to change when a new CPython is released, and when the oldest reaches end of life. Read when a new CPython is released or the oldest reaches end of life, or when asked to add or drop a supported Python version."
---

# Following the Python Release Cycle

A new CPython is released every October, and the oldest supported one reaches end of life around then. The policy is in `04-python-versions.md`.

---

## 1. A new version is released

1. Add it to the CI matrix and to `USING_COVERAGE` (`18-github-actions.md`), and to the classifiers (`04-python-versions.md`).
2. Run the full CI. If a dependency does not support the new Python yet, leave it out of the matrix and classifiers until the dependency ships.
3. Raise the `requires-python` cap, if one is set.
4. Record it in the changelog as a Minor Improvement (`21-versioning-and-changelog.md`).

---

## 2. A version reaches end of life

1. Remove it from the CI matrix, `USING_COVERAGE`, and the classifiers.
2. Raise the `requires-python` floor.
3. Lift the dependency caps that existed only for the old floor (`05-uv-dependencies.md` section 2), through the process in `23-dependency-upgrades.md`.
4. Keep the `mise.toml` dev Python inside the range; `.readthedocs.yml` follows it (`04-python-versions.md`).
5. Record it in the changelog as a Breaking Change (`21-versioning-and-changelog.md`): users on that Python get no new releases.
