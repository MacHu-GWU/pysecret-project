---
description: "One numbered folder per docs page, the autotoctree directive that builds the table of contents, and the API reference generated into docs/source/api/. Read when adding, moving, or ordering a docs page, or when the API reference is missing something."
---

# docfly

[docfly](https://github.com/MacHu-GWU/docfly-project) does two jobs for the Sphinx project (`13-sphinx.md`): it builds the page tree, and it generates the API reference.

---

## 1. Page tree

```text
docs/source/
├── conf.py                 # Sphinx config; also runs docfly's API generator
├── index.rst               # home: includes README.rst and AUTHORS.rst, then .. autotoctree::
├── release-history.rst     # .. include:: ../../release-history.rst
├── 01-Getting-Started/
│   └── index.rst           # or index.ipynb
├── 02-Some-Topic/
│   ├── index.rst
│   └── images/             # assets live next to the page that uses them
├── api/                    # GENERATED, committed, never edited by hand
└── _static/                # css, js, logo, favicon, .custom-style.rst
```

- **One folder per page;** the page is the folder's `index.rst` or `index.ipynb`.
- **Folder names are `NN-Title-In-Kebab-Case`:** the two-digit prefix sets the order; the rest is ASCII without spaces.
- **`.. autotoctree::`** (from `docfly.directives`) builds the table of contents from the child folders, titled by each child's `index` file. No `.. toctree::` list is kept by hand: to add a page, create the folder and its `index` file.
- **Order pages by how often readers need them.** Template conventions are not docs pages; they live in the skills.

---

## 2. API reference

- `conf.py` runs `docfly.ApiDocGenerator(...).fly()` on every build, writing one `.rst` file per module into `docs/source/api/`.
- It skips the files excluded in `08-package-files.md` section 8. To hide another module, add it to `ignore_patterns` in `conf.py`.
- Each page uses `.. automodule:: ... :members:`, which **skips names with no docstring or `#:` comment**. A name missing from the API page means a missing docstring: fix the docstring, never the generated `.rst`.
- `autodoc_member_order = "bysource"` keeps members in source order.
