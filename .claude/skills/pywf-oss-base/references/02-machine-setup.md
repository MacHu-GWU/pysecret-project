---
description: "One-time setup of a maintainer's Mac: global mise, uv, git and gh, shell activation, the secrets file, where and with which scopes to create each token, account settings, and token rotation. Read when setting up a new machine, rotating a token, or when a tool is missing or a token is missing or rejected (HTTP 401 or 403)."
---

# Machine Setup

Everything here is done **once per machine**, not per repo. Afterwards, every template repo works with `mise run inst`. Secrets follow `01-secrets.md`.

---

## 1. Global tools

| Tool | Install | Why it is global |
| :--- | :--- | :--- |
| mise | `brew install mise` | Installs each per-repo tool version once per machine, and runs the tasks |
| uv | `brew install uv` | `uvx` keeps one tool cache shared by all repos (for `hst`, `ruff`, ...). Each repo still pins its own uv version. |
| git, gh | `brew install git gh`, then `gh auth login` | `gh` reads CI runs and manages GitHub repos from the terminal |

Activate mise in the shell: add this line to `~/.zshrc`, then open a new terminal.

```bash
eval "$(mise activate zsh)"
```

Check with `mise --version`, `uv --version`, and `gh auth status`. In each repo, run `mise trust` once (mise asks the first time), then `mise run inst`.

---

## 2. The secrets file

Create `$HOME/home_secret.toml` with one key path per variable in `01-secrets.md` section 1, matching the `hst get <key_path>` commands in the repos' `mise.toml`. Then restrict it to the owner:

```bash
chmod 600 ~/home_secret.toml
```

- The user writes the values. An AI only says which key paths must exist.
- Never commit the file or copy it into a repo.

---

## 3. Tokens

| Variable | Where to create it | Scope |
| :--- | :--- | :--- |
| `GITHUB_TOKEN` | <https://github.com/settings/tokens> | Classic: `repo` and `workflow`. Or fine-grained, on all repos, with Administration, Contents, Secrets, and Actions set to read and write. |
| `CODECOV_TOKEN` | codecov.io → Settings → Access | An account **API** token, not a repo upload token |
| `READTHEDOCS_TOKEN` | <https://app.readthedocs.org/accounts/tokens/> | Account API token |
| `PYPI_TOKEN` | <https://pypi.org/manage/account/token/> | "Entire account". A brand-new project cannot use a project-scoped token for its first upload. |

**Account settings, once each:**

- In Read the Docs, connect GitHub in the account settings, so new projects build on every push.
- Sign in to codecov.io with GitHub, so repos appear there.

**Rotating a token:**

1. Create the new token.
2. Replace the value in `home_secret.toml` (the user does this).
3. Run the True/False check in `01-secrets.md`.

A new Codecov API token leaves the upload secrets already stored in each GitHub repo unchanged. Rerun `mise run setup-codecov` only for a repo whose CI upload fails.

---

## 4. Diagnosing a missing token

| What happens | Cause |
| :--- | :--- |
| The True/False check prints `False` | The key path is missing from `home_secret.toml`, or `mise.toml` points at the wrong path. |
| mise errors while loading the env | `hst` failed: usually the file or the key path is missing. |
| The token is present, but a task fails with HTTP 401 or 403 | The token has expired or lacks scopes (section 3). |
