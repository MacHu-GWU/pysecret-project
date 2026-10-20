---
description: "Runtime dependencies and the dev, test, doc and mise extras in uv, the version constraint policy, the generated uv.lock and requirements*.txt, and running Python through .venv. Read when adding or removing a dependency, or writing a version constraint."
---

# uv and Dependencies

uv manages packages, and `.venv/` is the only environment. Never `pip install`. Run `.venv/bin/python` and `.venv/bin/pytest`.

---

## 1. Where dependencies are declared

All in `pyproject.toml`:

| Group | What goes in it |
| :--- | :--- |
| `dependencies` | Runtime dependencies of the library |
| extra `dev` | Local developer tools |
| extra `test` | `pytest`, `pytest-cov` |
| extra `doc` | Sphinx, the theme, the Sphinx extensions, and `ipykernel` (to execute the docs notebooks) |
| extra `mise` | Libraries used by the scripts in `.mise/tasks/` |

---

## 2. Constraint policy

| Kind | Form | Example |
| :--- | :--- | :--- |
| Normal dependency | `>=<tested floor>,<<next major>` | `"third_party_lib>=2.4.1,<3.0.0"` |
| Pre-1.0 package (a minor release may break) | `>=0.Y.Z,<1.0.0`, or `<0.(Y+1).0` when its minors do break | `"third_party_lib>=0.9.8,<1.0.0"` |
| Visual theme (any release changes the look) | exact pin | `"third_party_lib==2025.12.19"` |
| Needs a fix or a security patch | raise the floor to the fixed version | `"third_party_lib>=9.0.3"` |

- **The floor is a tested version,** normally the one in `uv.lock` after the last upgrade.
- **Every dependency, extras included, supports every Python in `requires-python`.** When a package's newest release drops a Python the repo still supports, cap below that release, and say why in the comment.
- Every line ends with a comment saying why the package is there: `"pytest>=9.1.1,<10.0.0", # Testing framework`.

---

## 3. Applying a change

1. Edit `pyproject.toml`.
2. `mise run inst` (`uv sync --all-extras`): updates `uv.lock` and `.venv`.
3. `mise run export`: regenerates `requirements*.txt` from `uv.lock`.

`uv.lock` and `requirements*.txt` are generated files. Never edit them by hand.
