---
description: "How package source code is written: file header, one imported name per statement, the five-group import order, Python 3.11+ type hints, naming, docstrings and #: comments, one field per line in declarative models, and plain explicit code. Read before writing or reviewing source code in the package."
---

# Code Style

These rules apply to source code under `<package_name>/`. Special files are in `08-package-files.md`; test files use a different import order.

---

## 1. File header

Every `.py` file starts with:

```python
# -*- coding: utf-8 -*-
```

An executable script puts its shebang on line 1 and this on line 2. Then come the module docstring, if any, and `from __future__ import annotations` (section 4).

---

## 2. One imported name per statement

This applies everywhere: source, tests, `.mise/tasks`, and scripts.

```python
# yes
from .module_name import ClassName
from .module_name import func_name

# no
from .module_name import ClassName, func_name
from .module_name import (
    ClassName,
    func_name,
)
```

- **Why:** diffs, `git blame`, and commenting a name in or out each touch exactly one line, and `api.py` reads as a list of public names.
- One long import that the formatter wraps into `from x import (\n    name,\n)` is still one name, and is fine.
- `mise run lint` checks this rule (see `06-ruff.md`).

---

## 3. Import order

Five groups, in this order, with one blank line between groups:

1. **Special first:** `import typing as T`. This is the only way typing is imported.
2. **Standard library.**
3. **Third party.**
4. **Close relatives:** distributions from the same ecosystem, such as the author's other libraries this one builds on, or sibling distributions of one large project.
5. **This package, relative imports only, farthest first:** `from ...x import`, then `from ..y import`, then `from .z import`. Distant modules are closer to third-party code; the nearest are "my own" code and come last.

```python
# -*- coding: utf-8 -*-

"""
One-line summary of the module.
"""

from __future__ import annotations

import typing as T
import json
from pathlib import Path

import third_party_lib

from sibling_lib.api import sibling_func

from ...subpackage.module_name import CONSTANT_NAME
from ..module_name import ClassName
from .module_name import func_name

if T.TYPE_CHECKING:  # pragma: no cover
    from third_party_lib import TypeOnlyClass
```

- Inside `<package_name>/`, never write `from <package_name>.x import y`. Relative imports tie the code to its position in the tree, not to the package name.
- Imports needed only for type hints go under `if T.TYPE_CHECKING:  # pragma: no cover`, after all other imports.

---

## 4. Type hints (Python 3.11+)

- Use builtin generics and `|`: `list[str]`, `dict[str, int]`, `tuple[int, ...]`, `type[X]`, `X | None`, `A | B`.
- Never `T.Optional`, `T.Union`, `T.List`, `T.Dict`, `T.Tuple`, `T.Set`, or `T.Type`.
- Use `T.` for names that exist only in `typing`: `T.Any`, `T.Callable`, `T.Iterable`, `T.Iterator`, `T.Literal`, `T.TypeVar`, `T.Self`, `T.TYPE_CHECKING`, `T.overload`.
- Every module with type annotations starts with `from __future__ import annotations`, so forward references need no quotes. Pure re-export modules (`__init__.py`, `api.py`) do not need it.
- Annotate every public function and method, including the return type.

---

## 5. Naming

- Private names start with `_` (see `08-package-files.md`).
- Constants are `UPPER_CASE` at module level.

---

## 6. Docstrings and comments

- **Every public module, class, function, and method has a docstring** of at least one line. The API docs list only names that have one.
- **Constants and fields are documented with a `#:` comment:** above a constant, trailing on the same line for a field (section 7).
- **Docstrings use reStructuredText fields:** `:param name:`, `:returns:`, `:raises ExcType:`.
- **Keep docstrings thin:** say what the signature cannot (behavior, side effects, raised errors, non-obvious constraints).
- Add a `>>>` example only when it shows something non-obvious, and keep it runnable.
- Comments explain why, not what.
- Version history belongs in the changelog, not in code. When a public behavior changes, use `.. versionadded:: x.y.z` or `.. versionchanged:: x.y.z` in the docstring.

---

## 7. One field per line in declarative models

In a dataclass, pydantic model, ORM model, attrs class, or any similar declarative schema, **each field definition stays on one line**, however long. The fields read as a table, and a field the formatter wraps over five lines breaks it. So fence the fields with `# fmt: off` / `# fmt: on` at the indentation of the class body, and keep the methods outside, where the formatter still handles them:

```python
@dataclasses.dataclass
class ClassName:
    # fmt: off
    attr_name: str = dataclasses.field(default="")  #: What this field means, in one line.
    other_attr: int | None = dataclasses.field(default=None)  #: Another field, documented the same way.
    # fmt: on

    def method_name(self) -> str:
        return f"{self.attr_name}"
```

- Fence the fields even when they fit today, so a long field added later does not reflow the block.
- Only field definitions go inside the fence: no methods, no validators.
- Document each field with a **trailing** `#:` comment, so it stays on one line and still appears in the API docs.
- Other hand-aligned blocks (lookup tables, matrices, column-aligned test cases) are fenced the same way.

---

## 8. Plain, explicit code

- Use named temporaries and explicit `if` / `else`, not clever one-liners.
- Re-raise with a bare `raise`. Convert an exception with `raise NewError(...) from e`.
