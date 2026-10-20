---
description: "The uv-based build in .readthedocs.yml, the setup-readthedocs and update-github-metadata tasks, the slug and URLs, and diagnosing a failed hosted build. Read when setting up docs hosting, or when the hosted build fails or differs from the local one."
---

# Read the Docs

---

## 1. Build

- `.readthedocs.yml` installs uv, runs `uv sync --extra doc` into the Read the Docs virtualenv, and builds Sphinx from `docs/source/conf.py` (`13-sphinx.md`), with the dev Python that it reads from `mise.toml` `[tools] python` (`04-python-versions.md`).
- It builds on every push to `main`, without secrets, so notebooks ship with committed outputs (`17-nbsphinx.md`).

---

## 2. Project setup

- **Slug:** the project name with `_` replaced by `-`. The docs URL is `https://<slug>.readthedocs.io/`.
- `mise run setup-readthedocs` creates the Read the Docs project from the GitHub repo (idempotent).
- `mise run update-github-metadata` sets the GitHub repo description (from `pyproject.toml`) and homepage (the docs URL).
- Each runs only after the user's yes (`03-mise.md`).

---

## 3. Diagnosing a failed build

- **Build list and logs:** `https://app.readthedocs.org/projects/<slug>/builds/`.
- **Status from the terminal**, without printing the token:

  ```bash
  mise exec -- sh -c 'curl -s -H "Authorization: Token $READTHEDOCS_TOKEN" "https://readthedocs.org/api/v3/projects/<slug>/builds/?limit=1"' | python3 -m json.tool
  ```

- **Reproduce locally** with `mise run build-doc`.
- **Fails only on Read the Docs:** a package missing from the `doc` extra is present locally through another extra (`05-uv-dependencies.md`), or the build Python differs from the local one.
- **A notebook needs credentials:** see the execution rules in `17-nbsphinx.md`.
