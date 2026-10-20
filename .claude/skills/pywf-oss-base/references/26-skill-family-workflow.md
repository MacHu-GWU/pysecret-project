---
description: "Choosing and chaining the invokers: which skill does which job and which base files it reads, handoffs, typical flows (new machine and repo, feature, bug fix, maintenance, template upgrade), and what each handoff guarantees. Read when unsure which skill fits a job, when a skill finishes and the next step is unclear, or when planning a multi-step job."
---

# Skill Family Workflow

Which invoker does which job, and the order they run in. Each invoker loads the base itself.

---

## 1. Which skill to use

| Skill | Use it when | Example request | Reads from this base |
| :--- | :--- | :--- | :--- |
| `pywf-oss-setup-machine` | A new machine needs setup, a token needs rotating, or a task fails for a missing tool or token. | "set up my new MacBook" | `01-secrets.md`, `02-machine-setup.md` |
| `pywf-oss-setup-repo` | A freshly generated repo must go live on GitHub, Codecov, and Read the Docs. | "put this new repo online" | `01-secrets.md`, `03-mise.md`, `18-github-actions.md`, `19-codecov.md`, `20-readthedocs.md` |
| `pywf-oss-add-module` | A new module, subpackage, or feature area is needed, with its test file and `api.py` export. | "add a `subpackage/module_name.py` module" | `08-package-files.md`, `09-code-style.md`, `10-test-layout.md`, `11-test-writing.md`, `scripts/check_test_layout.py` |
| `pywf-oss-write-test` | An existing module needs tests, more coverage, or fixed tests. | "cover `module_name.py` to 100%" | `09-code-style.md`, `10-test-layout.md`, `11-test-writing.md`, `12-coverage.md`, `scripts/check_test_layout.py` |
| `pywf-oss-write-doc` | A docs page, guide, tutorial, or notebook must be written or fixed. | "write a quick-start page" | `13-sphinx.md`, `14-docfly.md`, `15-furo.md`, `16-sphinx-design.md`, `17-nbsphinx.md`, `assets/*`, `scripts/check_doc_xrefs.py` |
| `pywf-oss-changelog` | The next version's release notes must be written from git history, or a change such as an upgrade recorded. | "update the changelog" | `21-versioning-and-changelog.md` |
| `pywf-oss-release` | A version must be bumped, published to PyPI, and tagged on GitHub. | "release 1.2.0" | `01-secrets.md`, `03-mise.md`, `21-versioning-and-changelog.md`, `22-release.md` |
| `pywf-oss-write-pypi-skill` | After a release, an Agent Skill must document this library's public API for other projects. | "make a skill for this library" | `08-package-files.md` |
| `pywf-oss-fix-ci` | GitHub Actions, the Codecov upload, or the Read the Docs build is red or warns, or a Python version must be added or dropped. | "CI fails on Windows" | `04-python-versions.md`, `18-github-actions.md`, `19-codecov.md`, `20-readthedocs.md`, `24-python-release-cycle.md` |
| `pywf-oss-upgrade-deps` | Dependencies must be upgraded, an upgrade judged, or an unmaintained package replaced. | "is the new pytest worth it?" | `04-python-versions.md`, `05-uv-dependencies.md`, `13-sphinx.md`, `15-furo.md`, `23-dependency-upgrades.md`, `scripts/check_doc_xrefs.py` |
| `pywf-oss-add-community-skill` | A community skill must be installed, or a GitHub skill link added to the catalog. | "install the logo design skill" | `25-community-skills.md`, `assets/community-skills.toml`, `scripts/install_community_skill.py` |
| `pywf-oss-audit` | A repo must be checked against these conventions, such as an older repo before a template upgrade. Changes no source file. | "audit this repo" | all references, `scripts/check_test_layout.py`, `scripts/check_one_import_per_line.py`, `scripts/check_doc_xrefs.py` |

---

## 2. Handoffs

| Skill | Hands off to |
| :--- | :--- |
| `pywf-oss-setup-machine` | `pywf-oss-setup-repo`, for a new repo |
| `pywf-oss-setup-repo` | `pywf-oss-add-module` to start coding; `pywf-oss-release` for the first version; `pywf-oss-fix-ci` if a service stays red |
| `pywf-oss-add-module` | `pywf-oss-write-test`, once the logic is written |
| `pywf-oss-write-test` | `pywf-oss-write-doc`, if the feature is user-facing; otherwise `pywf-oss-changelog` |
| `pywf-oss-write-doc` | `pywf-oss-changelog` |
| `pywf-oss-changelog` | `pywf-oss-release` |
| `pywf-oss-release` | `pywf-oss-write-pypi-skill` (optional) |
| `pywf-oss-write-pypi-skill` | — |
| `pywf-oss-fix-ci` | `pywf-oss-upgrade-deps`, when the cause is a dependency |
| `pywf-oss-upgrade-deps` | `pywf-oss-changelog`, then `pywf-oss-release` |
| `pywf-oss-add-community-skill` | — |
| `pywf-oss-audit` | any of the above, per finding |

---

## 3. Typical flows

| Flow | Steps |
| :--- | :--- |
| New machine, then new repo | `setup-machine` (once per machine) → `setup-repo` (once per repo) → `release` for the first version |
| New feature | `add-module` → write the logic → `write-test` → `write-doc` → `changelog` → `release` |
| Bug fix | fix the code → `write-test` (add the regression test) → `changelog` → `release` |
| A service is red | `fix-ci` |
| Routine upgrades, every few months or on a security fix | `upgrade-deps` → `changelog` → `release` |
| Yearly Python cycle | `fix-ci` (Python versions) → `upgrade-deps` (caps for the old floor) → `changelog` → `release` |
| A job needs an optional community skill | `add-community-skill` (stage → review → install) |
| Bring an older repo up to the current template | `audit` → apply its findings, grouped by fixing skill → `audit` again until it is clean |

---

## 4. What each handoff guarantees

- **After `add-module`:** the module exists with docstrings, and its test file with a `run_cov_test` block. `write-test` only fills in test functions.
- **After `write-test`:** the module's own test file shows 100% (or each uncovered line has a justified pragma), and `mise run cov` passes.
- **Before `changelog`:** the change is committed, because `changelog` reads `git log <last_tag>..HEAD`.
- **`release`** checks for a changelog section for the `pyproject.toml` version, and runs the `changelog` steps first if it is missing.
