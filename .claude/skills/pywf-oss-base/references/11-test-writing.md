---
description: "How a test file body is written: the template, imports with the subject under test first, naming and grouping, parametrize, docstrings, and independence from order and working directory. Read when writing or reviewing the test functions inside a test file."
---

# Writing Tests

Where test files live and how they end is in `10-test-layout.md`. This file covers what goes between the header and the `run_cov_test` block.

---

## 1. Template

```python
# -*- coding: utf-8 -*-

from <package_name>.subpackage.module_name import func_name
from <package_name>.subpackage.module_name import ClassName

import pytest

from pathlib import Path

from <package_name>.paths import path_enum


def test_func_name():
    result = func_name(...)
    assert isinstance(result, ClassName)


class TestClassName:
    def test_method_name(self):
        ...


if __name__ == "__main__":
    from <package_name>.tests import run_cov_test

    run_cov_test(
        __file__,
        "<package_name>.subpackage.module_name",
        preview=False,
    )
```

---

## 2. Import order in test files

This differs from source files:

1. **The subject under test, first:** the names from the module this file maps to, imported absolutely from that exact module. They are the file's protagonists.
2. `import pytest` and `import typing as T`, if needed.
3. Standard library.
4. Third party.
5. Other modules of this package, as absolute imports (`from <package_name>.x import y`), including helpers from `<package_name>.tests`.

Test files use absolute imports only. One imported name per statement still applies (`09-code-style.md`).

---

## 3. Writing good tests

- **Naming:** `test_func_name` or `test_func_name_case`. Group the tests of one class in `class TestClassName:`.
- **Docstrings:** one or two lines on what is verified and why it matters; none when the name says it all.
- **Parametrize** tests that differ only in data, instead of writing near-duplicate functions.
- **Independence:** never depend on run order or the working directory. Use `path_enum` or `tmp_path` for files.
- **Behavior over lines:** target behavior and edge cases. Coverage is the check, not the goal.
