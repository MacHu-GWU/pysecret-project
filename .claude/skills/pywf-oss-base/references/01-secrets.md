---
description: "How secrets reach a repo: $HOME/home_secret.toml read by the hst CLI through mise [env], the variables the template uses, the hard rules that keep an AI from reading or printing a secret, and how CI differs. Read before running anything that needs a token, or when adding a secret."
---

# Secrets

The maintainer runs hundreds of repos on one machine, so instead of a `.env` file per repo, every secret lives in one file, `$HOME/home_secret.toml`, read by the [home-secret-toml](https://github.com/MacHu-GWU/home_secret_toml-project) CLI (`hst`).

---

## 1. How a repo gets a secret

- `$HOME/home_secret.toml` is one flat TOML file: one full dotted key path and its value per line. The key paths are the maintainer's own; the template depends on no particular shape.
- When mise loads a repo, the `[env]` block of its `mise.toml` turns key paths into environment variables:

  ```toml
  [env]
  GITHUB_TOKEN = "{{ exec(command='uvx --from home-secret-toml hst get <key_path> || true') }}"
  ```

  The `|| true` fallback matters: a failed `exec` aborts every mise command in the repo, not only the tasks that need the secret. With it, an unreadable secret is an empty string, which scripts treat as not set, and the `hst` error printed on each mise command names the missing key.

  `mise.toml` is the only place that maps a variable to its key path. Read it there; never assume a path.

- Scripts read a plain environment variable, such as `os.environ["GITHUB_TOKEN"]`.

The template uses these variables:

| Variable | The value is |
| :--- | :--- |
| `GITHUB_TOKEN` | A GitHub token for the GitHub API: repo metadata, Actions secrets, tags and releases |
| `CODECOV_TOKEN` | The Codecov **API** token of the account, used to fetch each repo's upload token |
| `READTHEDOCS_TOKEN` | A Read the Docs API token |
| `PYPI_TOKEN` | A PyPI API token, used to upload releases |

---

## 2. Hard rules for an AI

- **Never read, open, cat, grep, copy, or summarize `$HOME/home_secret.toml`.** Not even to check whether a key exists.
- **Never print a secret value:** no `echo $PYPI_TOKEN`, `env`, `printenv`, `mise env`, or `hst get` outside `mise.toml`.
- Never write a secret into a file, a commit, a log, a notebook cell, a URL, or the chat.
- **To check which variables are loaded,** print only True or False, from a repo root:

  ```bash
  mise exec -- python3 -c "import os; print({k: bool(os.environ.get(k)) for k in ['GITHUB_TOKEN', 'CODECOV_TOKEN', 'READTHEDOCS_TOKEN', 'PYPI_TOKEN']})"
  ```

- **To add a secret,** add an `[env]` line with `hst get <key_path>` to `mise.toml`, and tell the user which key path to add to their file. The user writes the value.
- **When a task fails for a missing or rejected token,** report the variable name and stop. Do not work around it.
- **If the user pastes a secret into the chat,** do not use it, and ask them to rotate it: it is now in the transcript.

---

## 3. CI is different

GitHub Actions uses neither mise nor `home_secret.toml`. It reads repository secrets, such as `secrets.CODECOV_TOKEN`, that one-time setup tasks store on the GitHub repo.
