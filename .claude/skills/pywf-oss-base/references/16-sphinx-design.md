---
description: "The widgets (grid, card, tabs, code tabs, dropdown, badge, button, icon) with a copy-ready example each, the syntax rules that break them silently, and which widget fits which page. Read when a docs page needs more than plain text, such as a landing page, install tabs, or an FAQ."
---

# sphinx-design

[sphinx-design](https://sphinx-design.readthedocs.io/) (enabled in `conf.py`) adds responsive layout and UI widgets to reStructuredText (`13-sphinx.md`), including a notebook's raw reStructuredText cells. The sample page `docs/source/03-Sample-Sphinx-Design-Gallery/index.rst` of a template repo renders every example below; check your result against it.

---

## 1. Rules that break widgets silently

- **Indent child directives 4 spaces under their parent.** One wrong indent ends the parent early and renders the rest as plain text, often with no warning.
- **Options go directly under the directive line, then one blank line, then the content.** A blank line before an option turns it into body text.
- **Colors** are semantic names: `primary`, `secondary`, `success`, `info`, `warning`, `danger`, `muted`, `light`, `dark`. Avoid `light`, `dark`, `white`, and `black` for text: they vanish in one of the two modes (`15-furo.md`).
- **Icons:** `:octicon:` or `:material-regular:` (bundled). Never the FontAwesome roles (`:fas:`, ...): the template does not load FontAwesome, so they render as nothing.
- **Links inside widgets:** `:link:` takes a label with `:link-type: ref`, a document path without extension with `:link-type: doc`, or a URL (the default). Prefer `ref`, which survives renames. A `doc` path is relative to the current page, or to `docs/source/` when it starts with `/` (`/api/<package_name>/__init__`).
- **Do not decorate for its own sake.** Use a widget only when the reader gains something: a choice (tabs), optional detail (dropdown), a map of pages (cards), or status (badges).

---

## 2. Widgets

### Grid of cards: overviews and landing pages

```rst
.. grid:: 1 2 2 3
    :gutter: 3

    .. grid-item-card:: :octicon:`rocket;1.5em;sd-text-primary` Quick Start
        :link: sample-rst-document
        :link-type: ref

        Install and run your first example in two minutes.

    .. grid-item-card:: :octicon:`book;1.5em;sd-text-info` API Reference
        :link: /api/<package_name>/__init__
        :link-type: doc

        Every public class and function.
```

- `1 2 2 3` is the column count at the xs / sm / md / lg widths; a single number applies to all.
- A card with `:link:` is clickable as a whole, so put no other links inside it.

### Card with header and footer

```rst
.. card:: ClassName
    :shadow: md

    Header text
    ^^^
    Body: what ``ClassName`` does, in one sentence.
    +++
    Footer: see :class:`~<package_name>.module_name.ClassName`.
```

`^^^` ends the optional header and `+++` starts the optional footer. The directive argument is the card title.

### Tabs: alternatives the reader chooses between

```rst
.. tab-set::

    .. tab-item:: pip
        :sync: pip

        .. code-block:: bash

            pip install <package_name>

    .. tab-item:: uv
        :sync: uv

        .. code-block:: bash

            uv add <package_name>
```

Tab items with the same `:sync:` key switch together across every tab-set on the page: use it for an OS or package-manager choice that repeats.

### Code tabs: the same thing in several languages

```rst
.. tab-set-code::

    .. code-block:: python

        func_name("Alice")

    .. code-block:: bash

        python -c 'from <package_name>.api import func_name; print(func_name("Alice"))'
```

Each tab is labeled with its code block's language. `literalinclude` works inside, too.

### Dropdown: optional detail, FAQ, long output

```rst
.. dropdown:: Why does the test file name repeat the folder path?
    :icon: question
    :color: info

    pytest needs unique test module basenames.
```

Add `:open:` to start expanded. `:icon:` takes an octicon name.

### Badges: status and labels inline

```rst
:bdg-success:`stable` :bdg-warning:`beta` :bdg-secondary-line:`optional`
:bdg-link-primary:`PyPI <https://pypi.org/project/<package_name>/>`
:bdg-ref-info:`see the sample <sample-rst-document>`
```

Roles: `:bdg-<color>:` (filled), `:bdg-<color>-line:` (outlined), `:bdg-link-<color>:` (URL), `:bdg-ref-<color>:` (label). Badges work in table cells and headings.

### Buttons: one clear call to action

```rst
.. button-ref:: sample-rst-document
    :ref-type: ref
    :color: primary
    :shadow:

    Get Started

.. button-link:: https://github.com/<owner>/<repo>
    :color: secondary
    :outline:

    :octicon:`mark-github` Source
```

At most one or two per page.

### Icons

```rst
:octicon:`check-circle;1em;sd-text-success` done
:material-regular:`warning;1.2em;sd-text-warning` careful
```

Syntax: `name;size;classes`. Names: <https://primer.style/octicons/>, <https://fonts.google.com/icons>.

---

## 3. Styling hooks

- Card options: `:shadow: none|sm|md|lg`, `:text-align: center`, `:img-top: path`, `:class-card: sd-border-primary`.
- Grid options: `:gutter: 0-5`, `:margin:`, `:padding:`, `:outline:`.
- CSS utility classes, usable in any `:class*:` option or in `.. div:: <classes>`: `sd-text-<color>`, `sd-bg-<color>`, `sd-border-<color>`, `sd-font-weight-bold`, `sd-shadow-md`, `sd-rounded-3`, `sd-p-3`, `sd-m-3`.

---

## 4. Which widget for which page

| Page need | Widget |
| :--- | :--- |
| Landing page, or "what's in this section" | `grid` of `grid-item-card` with `:link:` and an icon in each title |
| Install or usage that differs by tool or OS | `tab-set` with `:sync:` keys |
| The same example in Python and in the shell | `tab-set-code` |
| FAQ, troubleshooting, long or optional detail | `dropdown`, one per question |
| Feature or support matrix | `list-table` with badges in the cells |
| "Next step" at the end of a guide | one `button-ref` |
