---
name: verify-markdown
description: Check Markdown files for problems that break GitHub rendering (lines joined into one paragraph, Mermaid diagrams that fail to render) and fix them. Use after editing any .md file, before committing docs, or when a document looks wrong on GitHub.
---

# Verify Markdown

1. Run the checker on the changed files, or on the whole repo with no arguments:

   ```bash
   python3 .agents/skills/verify-markdown/check_markdown.py [FILE_OR_DIR ...]
   ```

2. Fix each reported line:

   | Code            | Problem                                             | Fix                                           |
   | --------------- | --------------------------------------------------- | --------------------------------------------- |
   | `soft-break`    | Consecutive `Label: value` lines join into one line | End the line with `\`                         |
   | `mermaid-end`   | Flowchart node id `end` (any case) is a keyword     | Rename it, e.g. `DONE`, in every edge too     |
   | `mermaid-label` | Unquoted label with punctuation fails to parse      | Wrap the label in `"..."` inside the brackets |

3. Rerun until it prints `OK`.

4. Read what the script cannot check. Look over each changed file for:
   - Other single-newline paragraphs that should be separate lines (a list or blank line fixes them).
   - Tables whose rows have a different number of cells from the header.
   - Mermaid edge labels `-->|...|` and non-flowchart diagrams with brackets or quotes inside text.

5. If a Mermaid diagram changed and Node is available, render it to be sure (slow on first run, downloads Chromium):

   ```bash
   npx -y @mermaid-js/mermaid-cli -i FILE.md -o /tmp/mmd-out.md
   ```

   GitHub may use a different Mermaid version, so a render failure is certain but a pass is not proof.
