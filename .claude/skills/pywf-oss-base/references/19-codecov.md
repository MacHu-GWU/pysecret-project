---
description: "codecov.yml versus .coveragerc, how the setup-codecov task stores the upload token on GitHub, the CI upload step, and fixing a failed or wrong upload. Read when connecting a repo to Codecov, or when the Codecov upload fails or its numbers look wrong."
---

# Codecov

---

## 1. Configuration

`codecov.yml` holds the report settings on the Codecov side. What gets measured is set by `.coveragerc` (`12-coverage.md`).

---

## 2. Upload token

`mise run setup-codecov` uses `CODECOV_TOKEN`, the account **API** token (`01-secrets.md`), to fetch the repo's own upload token, and stores it as the `CODECOV_TOKEN` Actions secret of the GitHub repo. The task is idempotent, and runs only after the user's yes (`03-mise.md`).

---

## 3. Upload in CI

The last workflow step (`18-github-actions.md`) uploads `coverage.xml` with `codecov/codecov-action`. The report path goes in the `files:` input; the old `file:` input is gone.

---

## 4. Diagnosing

| Symptom | Fix |
| :--- | :--- |
| "Upload coverage to Codecov" fails | The `CODECOV_TOKEN` Actions secret is missing or stale. Check with `gh secret list` (names only), then rerun `mise run setup-codecov`. |
| The upload succeeds, but the numbers look wrong | Compare `.coveragerc` `omit` with the `--cov=<package_name>` target, and check that the test step produced `coverage.xml`. |
