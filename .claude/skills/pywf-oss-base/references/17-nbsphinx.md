---
description: "Notebook docs pages with nbsphinx: raw reStructuredText cells with the exact cell JSON, the page skeleton, code cell style, and executing and committing outputs. Read when creating or editing a .ipynb docs page."
---

# nbsphinx Notebooks

A docs page can be `index.ipynb` instead of `index.rst`. nbsphinx renders it, and `.. autotoctree::` picks it up like any other page. Folder naming (`14-docfly.md`), labels, and cross-references (`13-sphinx.md`) work as for `.rst` pages.

Use a notebook when the page teaches by running code and real output helps the reader; use `.rst` for concepts and design notes.

---

## 1. The three cell types

| Cell | Used for | Rendered as |
| :--- | :--- | :--- |
| `code` | Runnable examples, with committed outputs | Code plus its output |
| `markdown` | Prose, lists, tables, images, and links. A link to another page uses its source path (`[text](../01-Some-Page/index.rst)` or `.ipynb`); nbsphinx turns it into the HTML link. | Markdown |
| `raw` with `raw_mimetype: text/restructuredtext` | Anything that needs Sphinx: the labeled page title, `:ref:` / `:class:` / `:func:` cross-references, directives (`.. note::`, `.. code-block::`, sphinx-design widgets from `16-sphinx-design.md`) | reStructuredText, parsed by Sphinx |

Markdown cells cannot use Sphinx roles or directives; put such a piece in a raw reST cell (<https://nbsphinx.readthedocs.io/en/0.9.8/raw-cells.html>).

---

## 2. Raw reST cell: the exact JSON

In JupyterLab or PyCharm, set the cell type to *Raw* and the *Raw NBConvert Format* to *reStructuredText*. On disk:

```json
{
  "cell_type": "raw",
  "id": "a1b2c3d4",
  "metadata": {
    "raw_mimetype": "text/restructuredtext"
  },
  "source": [
    ".. _getting-started:\n",
    "\n",
    "Getting Started\n",
    "==============================================================================\n"
  ]
}
```

- `metadata.raw_mimetype` must be exactly `text/restructuredtext`. Without it, nbsphinx drops the cell from the HTML.
- `source` is a list of lines, each ending in `\n` except possibly the last.
- `assets/raw-rst-cell.json` in the base skill is a copy-ready template of this cell, and `assets/notebook-page-template.ipynb` a minimal page in the skeleton of section 3.

---

## 3. Page skeleton

1. **Raw reST cell:** the page label and title with a 78-character `=` underline (as above), giving the page its `:ref:` target and sidebar title.
2. **Markdown cell:** one paragraph on what the page shows and who it is for.
3. **Then alternate** markdown cells (`##` section headings, explanations) and code cells, with a raw reST cell wherever a cross-reference or directive is needed.

Example raw cell in the middle of a page:

```rst
Every result is a :class:`~<package_name>.module_name.ClassName`; see :ref:`getting-started`
for how to create one.

.. note::

    One sentence the reader must not miss.
```

The sample page `docs/source/02-Sample-Jupyter-Notebook-Document/index.ipynb` of a template repo is a working example of everything on this page.

From nbsphinx 0.9.8 on, a raw-cell title shows in the sidebar and in `.. autotoctree::`. Some versions have lost that sidebar link (nbsphinx PR #834): if a page vanishes from the sidebar after an nbsphinx upgrade, move the title into a Markdown `# Title` cell, and keep the label in a raw cell above it.

---

## 4. Code cells: style

The reader learns one step at a time, so plain and explicit beats short.

- **One step and one result per cell.** Show a value as the last expression or with `print(f"{x = }")`; three values take three cells.
- Write the code a user would write: named variables, plain `for` loops, no clever comprehensions, lambdas, or demo-only helper functions.
- Show an expected error explicitly, one per cell:

  ```python
  try:
      do_bad_thing()
  except ValueError as e:
      print(f"{type(e).__name__}: {e}")
  ```

- Import from the public API (`from <package_name>.api import ClassName`), exactly as users would.
- Never put inline code inside bold in markdown (`**``x``**`); some editors render it badly.
- Never write secrets, account ids, or personal paths in a cell; read them from environment variables.

---

## 5. Editing and running

- Edit cells with the `NotebookEdit` tool or with `nbformat` in a script, never by hand-editing output JSON.
- Outputs are committed, because the hosted docs show what the file stores. Execute the notebook locally before committing:

  ```bash
  .venv/bin/jupyter nbconvert --to notebook --execute --inplace docs/source/02-Some-Topic/index.ipynb
  ```

  `ipykernel` comes with the `doc` extra, so `mise run inst` is enough.
- If a notebook needs credentials or services the hosted build lacks, set `nbsphinx_execute = "never"` in `conf.py`, so the build uses only committed outputs.
- `mise run notebook-to-markdown` converts the notebooks to Markdown, for an AI to read the docs without the JSON noise.
- Then build and check it like any page (`13-sphinx.md` section 4): raw cells render, cross-references resolve, and the page is in the sidebar.
