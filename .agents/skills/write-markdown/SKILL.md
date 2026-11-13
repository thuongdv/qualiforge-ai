---
name: write-markdown
description: Write or edit a Markdown document in this repo (architecture docs, ADRs, reviews, plans) so it renders correctly on GitHub. Use when creating or changing any .md file under docs/ or the repo root.
---

# Write Markdown

1. Read the "Markdown rules" section of `AGENTS.md` at the repo root. Those rules are the source of truth.
2. Match the house layout of the folder you write in:
   - Title as `# <Project> — <Topic>`.
   - A metadata header right under the title: one `**Label:** value` per line, every line but the last ending in `\`.
   - `---` between top-level sections.
   - Reviews go in `docs/reviews/YYYY-MM-DD-<reviewer>-<topic>.md`.
3. Diagrams: use Mermaid `flowchart`, `sequenceDiagram`, `stateDiagram-v2` or `erDiagram`. In flowcharts, quote any label with punctuation and never name a node `end`.
4. Refer to other docs by repo-relative path in backticks, e.g. `docs/architecture/ARCHITECTURE.md`.
5. When done, run `npx prettier . --write` (and `uvx ruff format .` if any Python changed), then run the `verify-markdown` skill and fix everything it reports.
