---
description: "The test suite structure: the source-to-test path mapping with directory-prefixed names, files with no test, the run_cov_test block, all.py per tested folder, the layout check script, the pytest config, and how to run tests. Read when working out a test file's path, creating or moving test files, or running tests."
---

# Test Layout

Tests use pytest. Every source module has exactly one test file, which also runs on its own as a script that reports the coverage of just its module.

---

## 1. Source-to-test mapping

The `tests/` tree mirrors the `<package_name>/` tree. Directory names stay the same, and **each file name is prefixed with its full directory path**:

| Source | Test file |
| :--- | :--- |
| `<package_name>/api.py` | `tests/test_api.py` |
| `<package_name>/module_name.py` | `tests/test_module_name.py` |
| `<package_name>/subpackage/module_name.py` | `tests/subpackage/test_subpackage_module_name.py` |
| `<package_name>/a/b/module_name.py` | `tests/a/b/test_a_b_module_name.py` |
| `<package_name>/a/_private.py` | `tests/a/test_a__private.py` |
| `<package_name>/a/b/` (a subpackage) | `tests/a/b/all.py` |
| `<package_name>/` (the whole package) | `tests/all.py` |

- **Why the prefix:** pytest's default import mode needs unique test module basenames. Without it, `tests/a/test_api.py` and `tests/b/test_api.py` collide, and the whole run fails with "import file mismatch".
- **No test file for** `__init__.py` or any file excluded from coverage in `08-package-files.md` section 8.
- `tests/` subfolders have no `__init__.py`.
- An occasional exception, such as one test file for two tiny modules, is fine with a comment saying why.

### The layout check

```bash
python ${CLAUDE_SKILL_DIR}/../pywf-oss-base/scripts/check_test_layout.py --project_root .
```

It lists missing test files, orphan test files that map to no module, and `run_cov_test` blocks whose module path does not match the file. Add `--source <source_path>` to print the expected test path and module for one source file.

---

## 2. The `run_cov_test` block

Every test file ends with this block:

```python
if __name__ == "__main__":
    from <package_name>.tests import run_cov_test

    run_cov_test(
        __file__,
        "<package_name>.subpackage.module_name",
        preview=False,
    )
```

- The import sits inside the `if __name__ == "__main__":` block.
- **One argument per line, with a trailing comma,** so the user can switch `preview=False` to `preview=True` (open the HTML report in a browser) by editing one line.
- The second argument is the dotted module path of the source file this test file maps to.

---

## 3. `all.py`: one per tested folder

Every `tests/` folder that mirrors a subpackage has an `all.py`, which runs every test in the folder and measures coverage on the whole subpackage:

```python
# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from <package_name>.tests import run_cov_test

    run_cov_test(
        __file__,
        "<package_name>.subpackage",
        is_folder=True,
        preview=False,
    )
```

- `is_folder=True` makes pytest collect the folder of `__file__` instead of the single file.
- `tests/all.py` covers the whole package (`"<package_name>"`).
- `all.py` has no test functions and no `test_` prefix, so the full suite never collects it.

---

## 4. pytest configuration

`pyproject.toml` has a native `[tool.pytest]` table (pytest 9+) with `testpaths = ["tests"]`, and optional settings as comments. Keep it small: `run_cov_test` and the mise tasks pass their own options.

---

## 5. Running tests

| Goal | Command |
| :--- | :--- |
| One module, with its own coverage | `.venv/bin/python tests/subpackage/test_subpackage_module_name.py` |
| One subpackage, with its coverage | `.venv/bin/python tests/subpackage/all.py` |
| Everything, with coverage | `mise run cov` |
| Everything, fast | `mise run test` |
| An ad-hoc selection | `.venv/bin/pytest tests/subpackage -k keyword` |

While developing a module, run its own test file. Before finishing, run `mise run cov`.

---

## 6. Other test folders

Tests against real external services go in `tests_int/`, load tests in `tests_load/`. Both follow the same mapping rules.
