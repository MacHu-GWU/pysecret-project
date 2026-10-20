---
description: "Why furo is pinned exactly, its conf.py settings, and the light and dark mode check after a theme change. Read when changing the look of the docs, the theme settings, or the furo version."
---

# furo

The docs use the [furo](https://github.com/pradyunsg/furo) theme on top of Sphinx (`13-sphinx.md`).

---

## 1. Version

furo is **pinned exactly** (`furo==<version>`): any release can change the look, so an upgrade is a deliberate step, followed by the visual check in section 3.

---

## 2. Settings in `conf.py`

| Setting | Value |
| :--- | :--- |
| `html_theme` | `"furo"` |
| `html_theme_options` | furo options, such as `sidebar_hide_name` |
| `html_logo` / `html_favicon` | `_static/<package_name>-logo.png` / `_static/<package_name>-favicon.ico` |
| `html_css_files` / `html_js_files` | `_static/css/custom-style.css`, `_static/js/sorttable.js` |
| `pygments_style` / `pygments_dark_style` | Code highlighting in light mode and in dark mode |

- **Custom CSS** goes in `_static/css/custom-style.css`.
- **Sortable tables:** `sorttable.js` makes any table with `:class: sortable` sortable by its header.

---

## 3. Visual check

With the theme toggle in the page header, check both light and dark mode: headings and sidebar, code blocks, tables, admonitions, the logo, and any coloured text or widgets. Colours that read well in one mode can disappear in the other.
