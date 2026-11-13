# AGENTS.md

Instructions for AI coding agents working in this repository.

## Repository

QualiForge AI is in the design phase. The repository holds Markdown documents only, under `docs/`:

- `docs/architecture/ARCHITECTURE_DECISIONS.md` wins where it and `ARCHITECTURE.md` disagree.
- `docs/reviews/` holds dated architecture reviews, named `YYYY-MM-DD-<reviewer>-<topic>.md`.

## Markdown rules

Every document is read on GitHub. Write for GitHub's renderer, not for the raw file.

### Line breaks

A single newline inside a paragraph is not a line break on GitHub: the lines are joined into one. For metadata headers and other consecutive short lines, end every line but the last with a backslash:

```markdown
**Last updated:** 2026-11-13\
**Decided by:** Project owner\
**Inputs:**
```

Use `\`, not two trailing spaces: editors and formatters strip trailing spaces silently. Otherwise, separate paragraphs with a blank line or use a list.

### Mermaid diagrams

GitHub's Mermaid renderer fails on input that some local previewers accept.

- Quote any node label containing characters other than letters, digits, spaces, `_ - ? , ' !`: write `WEB["Next.js Web Application"]` and `PG[("PostgreSQL + pgvector")]`, not `WEB[Next.js Web Application]`.
- Never use `end` as a node id, in any case (`END`, `End`). It is a keyword. Use `DONE`.
- Keep subgraph ids short and put the title in quotes: `subgraph UI["Presentation Layer"]`.

## Formatting

After creating or editing any file, run both formatters from the repo root:

```bash
npx prettier . --write
uvx ruff format .
```

Prettier formats Markdown, JSON, YAML and similar files; Ruff formats Python. Do not hand-format around them or change their output.

### Before finishing

After formatting, if any `.md` file changed, run:

```bash
python3 .agents/skills/verify-markdown/check_markdown.py
```

It must print `OK`. Fix every reported line.

## Skills

- `.agents/skills/write-markdown/SKILL.md`: writing or editing a document.
- `.agents/skills/verify-markdown/SKILL.md`: checking documents before commit or review.
