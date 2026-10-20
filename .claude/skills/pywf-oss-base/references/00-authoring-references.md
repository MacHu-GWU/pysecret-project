---
description: "How the pywf-oss skills themselves are written: the base and invoker split, reference numbering and backward-only citations, file shape, placeholders, script conventions, and the checks after any change. Read before adding, renaming, or editing any pywf-oss skill, reference, script, or asset."
---

# Authoring the pywf-oss Skills

---

## 1. The family

- **`pywf-oss-base`** holds knowledge only (`references/`, `scripts/`, `assets/`) and is bound to no action. Loaded on its own, it answers convention questions and picks the invoker for a job.
- **Each invoker `pywf-oss-<action>`** does one job. Its body says "Read ../pywf-oss-base/SKILL.md, then:" and lists the base files it needs. Everything after that is its own: the steps, what it asks the user, where it stops for the user's yes, and what it reports.
- **A shared fact lives in exactly one reference.** Invokers cite it and never restate it. If one invoker needs the fact to be different, change the reference.
- **Every skill is model-invocable.** None sets `disable-model-invocation`. A skill that changes an external service asks for the user's yes before each such step instead.

---

## 2. Reference files

- **Name:** `NN-slug.md`, two digits and a kebab-case slug.
- **Order** follows the project lifecycle: authoring (00), secrets and the machine, the toolchain, layout and code, tests, docs, CI and hosting, release, maintenance, and last the skill workflow.
- **Cite backward only.** A reference cites only lower-numbered references. When it needs a fact from later in the lifecycle, move that fact down into the earlier file, or state it without a citation. SKILL.md files may cite any reference.
- **One concern per file.** Split a file when two of its parts can change independently: different tools in one area (Sphinx, its theme, each extension), or structure versus style (where tests live, how they are written). A topic a job needs only sometimes gets its own file, so an invoker can load it on demand.
- **Shape:** YAML frontmatter with only `description`, one H1, then numbered H2 sections separated by `---`.
- **`description`** is one double-quoted string with no double quotes inside, in two parts: what the file holds, then a trigger sentence starting with "Read when" or "Read before". `scripts/update_skill_index.py` copies only the trigger into the base SKILL.md index, which every invoker reads, so keep the trigger short, and specific enough that no two references claim the same question.
- **Citations** look like `` `NN-slug.md` ``, optionally followed by "section N". Prefer the whole file; section numbers move.

---

## 3. Generic content

- Write in English.
- **Use placeholders, never a real project's names,** so the skills work when copied into any repo.

  | Placeholder | Meaning |
  | :--- | :--- |
  | `<package_name>` | The import package directory: snake_case, equal to `[project].name` in `pyproject.toml` |
  | `<owner>`, `<repo>` | GitHub owner and repository name. Repositories are named `<package_name>-project`. |
  | `module_name`, `subpackage`, `ClassName`, `method_name`, `func_name`, `CONSTANT_NAME`, `attr_name` | Code names in examples |
  | `third_party_lib`, `sibling_lib` | An ordinary third-party distribution, and a close-relative distribution |
  | `<slug>` | The Read the Docs project slug: the project name with `_` replaced by `-` |
  | `<version>`, `<last_tag>` | A version number, and the latest git tag |
  | `<cli_name>` | The command name registered in `[project.scripts]` |
  | `<dist_name>` | Any PyPI distribution name, in dependency work |
  | `<key_path>` | A dotted key path in `$HOME/home_secret.toml` |
  | `<run_id>` | A GitHub Actions run id |
  | `<path>`, `<source_path>`, `<test_path>`, `<notebook_path>`, `<script_name>` | File system paths and script names in commands |

  **Two spellings, on purpose:** a value substituted into a command, path, or config is snake_case in angle brackets (`<package_name>`). A name in example code is a bare identifier (`ClassName`), so the example stays valid Python.

- Name the tools of the template stack freely (mise, uv, ruff, pytest, pytest-cov, Sphinx, furo, docfly, nbsphinx, sphinx-design, sphinx-jinja, home-secret-toml, GitHub Actions, Codecov, Read the Docs): they are the conventions. Name any other library only when a rule is about it, as in "one field per line in pydantic models".
- For a working demonstration, point to the sample pages in `docs/source/` of a template repo. Do not copy a project's code into a reference.
- **Approval wording:** "the user's yes", and "one yes covers one step".

---

## 4. Scripts and assets

- Every script under `scripts/` is a stdlib-only command line tool:
  - `_main()` holds the logic, and `main(argv)` only parses arguments;
  - `--arg_name` flags only, no positional arguments;
  - exit code 0 for success, 1 for a failure found, 2 for a usage error.
- **File header:** `#!/usr/bin/env python3` on line 1, `# -*- coding: utf-8 -*-` on line 2.
- **Calling a script:** from a skill, as in the base SKILL.md; from a mise task, by its repo path, `python3 .claude/skills/pywf-oss-base/scripts/<script_name>.py`.
- `assets/` holds templates with placeholders. They are not valid Python, so ruff excludes them.

---

## 5. After any change to the family

1. Run `python ${CLAUDE_SKILL_DIR}/scripts/update_skill_index.py` to regenerate the references index in SKILL.md (`--check` only verifies it).
2. Keep three places in agreement:
   - each invoker's "Read" list;
   - the "Reads from this base" column of the "Which skill to use" table in the skill-family workflow reference;
   - the handoff table in the same reference.

   For a new or renamed skill, also update the skills table in `CLAUDE.md`.
3. Run `python ${CLAUDE_SKILL_DIR}/scripts/check_skill_family.py --skills_dir .claude/skills`, with `--forbid <forbidden_name>` for each project name that must not appear (such as the seed repo's demo package). It checks that every frontmatter is well formed, every `../pywf-oss-base/...` path resolves, every cited reference exists, no reference cites a later one, and no forbidden name appears.
4. Run `mise run lint`.
