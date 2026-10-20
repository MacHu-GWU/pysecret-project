---
description: "The format and lint tasks and their paths, the [tool.ruff] configuration, the small lint rule set, and # fmt: off / # fmt: on for hand-written layout. Read before finishing any change to Python code, or when ruff reports something."
---

# ruff

---

## 1. Tasks

```bash
mise run format   # uvx ruff format <package_name> tests .mise/tasks .claude/skills/pywf-oss-base
mise run lint     # uvx ruff check --select F401,F821,F841 on the same paths, plus the one-import-per-statement check
```

Run `format`, then `lint`, before you finish any change to Python code.

The tasks cover only this repo's own code. Other folders in `.claude/skills/`, such as installed community skills, are third-party: never format or lint them, so they stay identical to their pinned commit.

The one-import-per-statement check is the base script `check_one_import_per_line.py`, because ruff cannot enforce this rule without also re-sorting imports. To split violations automatically:

```bash
python ${CLAUDE_SKILL_DIR}/../pywf-oss-base/scripts/check_one_import_per_line.py --paths <package_name> tests --fix
```

---

## 2. Configuration

`[tool.ruff]` in `pyproject.toml`:

- **Excluded paths:**
  - `<package_name>/vendor`, which holds copied third-party code;
  - `.claude/skills/*/assets`, which holds templates with placeholders.
- **`__init__.py` and `api.py` may have unused imports:** they are the re-exports.
- **The lint set is deliberately small:** unused imports (F401), undefined names (F821), unused variables (F841). Layout is the formatter's job; line length is not linted.

---

## 3. Keeping hand-written layout

Wrap a block in `# fmt: off` / `# fmt: on` when its layout carries meaning the formatter would destroy: field definitions in declarative models (dataclass, pydantic, ORM), lookup tables, matrices, and column-aligned test cases. Keep the fence as small as possible, at the indentation of the code it fences.
