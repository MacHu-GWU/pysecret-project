---
description: "Sphinx without theme or extensions: conf.py, reStructuredText heading and label rules, the exact cross-reference forms and why a target silently fails to resolve, the small built-in extensions, and building and checking the docs, including the AI visual check. Read when writing reStructuredText or a docstring cross-reference, or checking a local docs build."
---

# Sphinx

The docs are a Sphinx project in `docs/source/`, configured by `conf.py`, with reStructuredText pages. The theme and each larger extension have their own reference.

---

## 1. reStructuredText conventions

Heading underlines are exactly **78 characters**, at three levels:

```rst
Page Title
==============================================================================

Section
------------------------------------------------------------------------------

Subsection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

- **Labels** go right above a title that other pages link to. They are kebab-case and unique across the project:

  ```rst
  .. _getting-started:

  Getting Started
  ==============================================================================
  ```

- **Code:** inline ``` ``code`` ```; blocks with `.. code-block:: python`.
- **External links:** `` `text <https://...>`_ ``.
- **Admonitions** (`.. note::`, `.. warning::`): sparingly.

---

## 2. Cross-references

These roles work the same in `.rst` pages, docstrings, and anywhere else reStructuredText is parsed. The sample page `docs/source/01-Sample-RestructuredText-Document/index.rst` of a template repo uses every form below.

### 2.1 Python objects

Always write the **full dotted path from the defining module**, not from the `api.py` re-export, then pick the display form that reads best:

| Target | Full path, displayed as written | Preferred display form | Renders as |
| :--- | :--- | :--- | :--- |
| Module | ``:mod:`<package_name>.module_name` `` | (same) | `<package_name>.module_name` |
| Class | ``:class:`<package_name>.module_name.ClassName` `` | ``:class:`~<package_name>.module_name.ClassName` `` | `ClassName` |
| Method | ``:meth:`<package_name>.module_name.ClassName.method_name` `` | ``:meth:`ClassName.method_name <<package_name>.module_name.ClassName.method_name>` `` | `ClassName.method_name()` |
| Function | ``:func:`<package_name>.module_name.func_name` `` | ``:func:`~<package_name>.module_name.func_name` `` | `func_name()` |
| Function, with its module | | ``:func:`module_name.func_name <<package_name>.module_name.func_name>` `` | `module_name.func_name()` |
| Module-level constant | ``:attr:`<package_name>.module_name.CONSTANT_NAME` `` | ``:attr:`~<package_name>.module_name.CONSTANT_NAME` `` | `CONSTANT_NAME` |
| Class attribute, field, or property | ``:attr:`<package_name>.module_name.ClassName.attr_name` `` | ``:attr:`ClassName.attr_name <<package_name>.module_name.ClassName.attr_name>` `` | `ClassName.attr_name` |

- `~` keeps only the last name. Use it when the context makes the module obvious.
- `title <target>` displays any text. For a method, show `ClassName.method_name`: a bare `method_name` loses its class.
- **Match the role to the object type:** `:meth:` for methods, `:func:` for functions, `:attr:` for constants, attributes, and fields. Sphinx may resolve a mismatched role, but renders it wrong (such as a trailing `()`).

### 2.2 Why a target silently fails

A Python target resolves only if autodoc documented the object: a function, class, or method needs a docstring, and a constant or field a `#:` comment (`09-code-style.md`). An unresolved target renders as plain code instead of a link, and **Sphinx gives no warning**. After a build, run:

```bash
python ${CLAUDE_SKILL_DIR}/../pywf-oss-base/scripts/check_doc_xrefs.py
```

It lists every cross-reference that did not become a link. Add `--include_api` to also scan the generated API pages.

### 2.3 Pages, sections, and the standard library

| Target | Syntax |
| :--- | :--- |
| A labeled section or page | ``:ref:`getting-started` ``, or ``:ref:`custom text <getting-started>` `` |
| Another doc file, relative to the current page | ``:doc:`../03-Some-Topic/index` `` |
| Another doc file, from `docs/source/` | ``:doc:`/03-Some-Topic/index` `` |
| Python standard library (through intersphinx) | ``:class:`pathlib.Path` ``, ``:func:`json.dumps` `` |

---

## 3. Small extensions

Enabled in `conf.py`, with no reference of their own:

| Extension | What it does |
| :--- | :--- |
| `sphinx.ext.intersphinx` | Resolves standard library cross-references |
| `sphinx.ext.viewcode` | Adds "[source]" links next to API entries |
| `sphinx-copybutton` | Adds a copy button to code blocks |
| `sphinx-jinja` | Renders data from code through `.. jinja:: doc_data`, defined in `<package_name>/docs/__init__.py` |

`rst_prolog` includes `_static/.custom-style.rst`, which defines the custom roles (colors, strike, and so on) available on every page.

---

## 4. Build and check

```bash
mise run build-doc   # clean build into docs/build/html
mise run view-doc    # open it in the browser
```

A docs change is done when:

- `build-doc` finishes with no new warnings;
- the cross-reference check reports 0 unresolved;
- the page appears in the sidebar with the right title and order.

**Visual check by an AI:** in the Claude desktop app, open the built site with the browser pane's `preview_start` and the `docs-html` configuration in `.claude/launch.json`, which serves `docs/build/html` over HTTP. Never open the files as `file://`: the pane then shows a snapshot without CSS, so layout and theme cannot be judged. Humans keep using `mise run view-doc`; their browser loads CSS from `file://` fine.
