#!/usr/bin/env python3
"""Flag Markdown that renders wrong on GitHub. Usage: check_markdown.py [FILE_OR_DIR ...] (default: repo root).

Checks:
  soft-break   Consecutive "Label: value" lines with no hard break; GitHub joins them into one line.
  mermaid-end  A flowchart node id spelled `end` (any case) breaks GitHub's Mermaid parser.
  mermaid-label  An unquoted flowchart node label with characters other than letters, digits, space or _-?,'!.
Exit code 1 when anything is found.
"""

import re
import sys
from pathlib import Path

LABEL = re.compile(r"^(\*\*[^*]+:\*\*|\*\*[^*]+\*\*:|[A-Z][\w ]{0,30}:\s)")
NOT_PARAGRAPH = re.compile(r"^\s*([-*+]\s|\d+[.)]\s|#|>|\||<|```|~~~|---|===)")
NODE = re.compile(
    r"(?<![\w\"])([A-Za-z_][\w-]*)(\[\(|\(\[|\[\[|\(\(|\{\{|\[|\(|\{)(.*?)(\)\]|\]\)|\]\]|\)\)|\}\}|\]|\)|\})"
)
SAFE_LABEL = re.compile(r"""^(""|[\w ?,'!-]*)$""")


def check_mermaid(lines, start, path):
    out = []
    kind = next(
        (l.split()[0] for l in lines if l.strip() and not l.strip().startswith("%%")),
        "",
    )
    if kind not in ("flowchart", "graph"):
        return out
    for i, raw in enumerate(lines, start):
        line = raw.strip()
        if not line or line.startswith("%%") or line.lower() == "end":
            continue
        line = re.sub(r'"[^"]*"', '""', line)  # quoted text is safe
        line = re.sub(r"\|[^|]*\|", "", line)  # edge labels
        for m in NODE.finditer(line):
            if m.group(1).lower() == "end":
                out.append(
                    f"{path}:{i}: mermaid-end: node id '{m.group(1)}' is reserved; rename it (e.g. DONE)"
                )
            if not SAFE_LABEL.match(m.group(3)):
                out.append(
                    f'{path}:{i}: mermaid-label: quote the label: {m.group(1)}{m.group(2)}"{m.group(3)}"{m.group(4)}'
                )
        bare = NODE.sub(lambda m: m.group(1), line)
        if line.startswith("subgraph"):
            continue
        for tok in re.findall(r"(?<![\w-])end(?![\w-])", bare, re.I):
            if not any(m.group(1) == tok for m in NODE.finditer(line)):
                out.append(
                    f"{path}:{i}: mermaid-end: node id '{tok}' is reserved; rename it (e.g. DONE)"
                )
    return out


def check_file(path):
    out = []
    lines = path.read_text(encoding="utf-8").splitlines()
    fence, block_start, prev = None, 0, ""
    for n, line in enumerate(lines, 1):
        stripped = line.strip()
        if fence:
            if stripped.startswith(fence):
                if lines[block_start - 1].strip().startswith(fence + "mermaid"):
                    out += check_mermaid(
                        lines[block_start : n - 1], block_start + 1, path
                    )
                fence, prev = None, ""
            continue
        if stripped.startswith(("```", "~~~")):
            fence, block_start, prev = stripped[:3], n, ""
            continue
        if (
            prev
            and stripped
            and not NOT_PARAGRAPH.match(line)
            and not NOT_PARAGRAPH.match(prev)
            and not prev.endswith(("  ", "\\"))
            and (LABEL.match(prev) or LABEL.match(stripped))
            and not line.startswith(" ")
        ):
            out.append(
                f"{path}:{n - 1}: soft-break: end the line with '\\' or the next line joins it on GitHub"
            )
        prev = line if stripped else ""
    return out


def main(args):
    files = []
    for a in args or ["."]:
        p = Path(a)
        files += (
            sorted(
                f
                for f in p.rglob("*.md")
                if not any(
                    part.startswith(".") and part not in (".", "..") for part in f.parts
                )
            )
            if p.is_dir()
            else [p]
        )
    problems = [msg for f in files for msg in check_file(f)]
    print("\n".join(problems) or f"OK: {len(files)} file(s), no problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
