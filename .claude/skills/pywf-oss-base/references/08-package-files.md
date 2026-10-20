---
description: "The special files in the package: api.py as the only public API, private _ names, paths.py, vendor/, the test helper and doc data folders, the single source of the version, a python-fire cli.py, and what is excluded from coverage and the API docs. Read when adding a public name, a path, a CLI, or anything that is not an ordinary module."
---

# Special Files in the Package

```text
<package_name>/
├── __init__.py      # minimal
├── api.py           # THE public API
├── paths.py         # every project path, absolute
├── cli.py           # optional: python-fire CLI
├── module_name.py   # ordinary modules
├── _module_name.py  # private modules
├── subpackage/      # may have its own api.py
├── vendor/          # copied third-party code
├── tests/           # test helpers (not tests)
└── docs/            # data for the docs
```

---

## 1. `api.py`: the public API

- Users import only through `api.py`, in one of two forms:

  ```python
  from <package_name>.api import ClassName
  import <package_name>.api as <package_name>  # then <package_name>.ClassName
  ```

- `api.py` holds only re-exports, one name per line, as relative imports:

  ```python
  # -*- coding: utf-8 -*-

  from .module_name import ClassName
  from .module_name import func_name
  from .module_name import CONSTANT_NAME
  from .subpackage import api as subpackage
  ```

- A subpackage that forms a coherent unit gets its own `subpackage/api.py`, exposed by the top-level `api.py` as a module (last line above).
- **Anything not in `api.py` is internal,** and may change in any release.
- `tests/test_api.py` touches every exported name with a line such as `_ = api.ClassName`, so a broken re-export fails CI.

---

## 2. Private modules and names

A module, function, or attribute whose name starts with `_` is private. Other modules of the package may use it; `api.py` never exports it.

---

## 3. `paths.py`: absolute paths only

- `PathEnum` lists every directory and file the code or tests need, built from `Path(__file__)`, so nothing depends on the working directory.
- Use `from .paths import path_enum`, then `path_enum.dir_project_root`, `path_enum.dir_htmlcov`, and so on.
- For a new path, add an attribute (`dir_*` for a directory, `path_*` for a file). Never build paths inline.

---

## 4. `vendor/`: copied third-party code

Small single-file utilities, copied in to avoid a dependency. Never restyle a vendored file; update it only by copying a newer upstream version.

---

## 5. `<package_name>/tests/` and `<package_name>/docs/`

- `<package_name>/tests/` holds test **helpers**, such as `run_cov_test` and shared fixtures, for test files to import. The tests themselves live in the top-level `tests/`.
- `<package_name>/docs/` holds `doc_data`, a dict that docs pages can render.
- Both are excluded from the wheel (`[tool.setuptools.packages.find] exclude` in `pyproject.toml`).

---

## 6. Version

`pyproject.toml` `[project].version` is the only place the version is written: no `_version.py`, no hard-coded `__version__`. Code that needs it at runtime calls `importlib.metadata.version("<package_name>")`.

---

## 7. `cli.py` (only if the package has a command line interface)

- **Use [python-fire](https://github.com/google/python-fire):** a class whose public methods are the subcommands, and a `main()` that calls `fire.Fire(ClassName)`.
- Register the command in `[project.scripts]` (`<cli_name> = "<package_name>.cli:main"`), and add `fire` to `dependencies`.
- Keep `cli.py` thin: it parses arguments and calls functions in ordinary modules, so the logic stays testable.

---

## 8. Excluded from coverage and from the API docs

`paths.py`, `cli.py`, `vendor/`, `tests/`, and `docs/`. The test, coverage, and docs references rely on this list. It is repeated in `.coveragerc` `[run] omit` and in `ignore_patterns` of `docs/source/conf.py`; keep the three in sync.
