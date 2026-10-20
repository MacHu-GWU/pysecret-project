---
description: "What pytest-cov measures, the .coveragerc omit and exclude lists, the 100% per-module target, and when # pragma: no cover is allowed. Read when coverage is below 100%, when deciding whether code may be excluded, or when editing .coveragerc."
---

# Coverage

---

## 1. What is measured

- pytest-cov measures the package (`--cov=<package_name>`). A test file run directly measures only its module (`10-test-layout.md`).
- **`.coveragerc` `[run] omit`** leaves out the files listed in `08-package-files.md` section 8.
- **`.coveragerc` `[report] exclude_lines`** leaves out the usual lines: `pragma: no cover`, `if __name__ == .__main__.:`, `raise NotImplementedError`, `def __repr__`, and so on.

---

## 2. Target

Each module reaches 100% from its own test file. Every uncovered line gets a test, or a justified `# pragma: no cover`.

---

## 3. `# pragma: no cover`

**Allowed** on a line or block that cannot or should not run in unit tests:

- platform-specific branches,
- `if T.TYPE_CHECKING:`,
- defensive code for impossible states,
- code that only runs against real external services.

**Never** use it to hide logic that simply has no test yet.
