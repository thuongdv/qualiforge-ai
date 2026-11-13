# Step 1 — Baseline

This is step 1 of the order of work in `docs/architecture/ARCHITECTURE_DECISIONS.md` (ADR-020). It answers two questions before any platform code is written:

1. Can the existing Claude workflow be seen run by run in Langfuse (ADR-007)?
2. How good is that workflow, measured on real stories (ADR-018)?

Commands marked "from Langfuse docs" are copied from the official pages listed at the end.

---

## Part A — Langfuse Cloud

The project uses Langfuse Cloud for now (ADR-007). Self-hosting is decided later, so there is nothing to install and no memory to measure in this step.

1. The connection details are in `.env` at the repository root, which git ignores:

   ```text
   LANGFUSE_PUBLIC_KEY
   LANGFUSE_SECRET_KEY
   LANGFUSE_BASE_URL
   ```

2. Check that they work. This prints `HTTP 200` when the keys are valid:

   ```bash
   set -a && . ./.env && set +a
   curl -s -o /dev/null -w 'HTTP %{http_code}\n' \
     -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" \
     "$LANGFUSE_BASE_URL/api/public/projects"
   ```

3. Never commit `.env` or paste the secret key into a document or chat.

---

## Part B — Trace the existing Claude workflow

Do this on the machine where the Claude workflow runs today.

1. Install the Langfuse SDK and the Claude Code plugin (from Langfuse docs). Python 3.9 or later is required.

   ```bash
   pip install "langfuse>=4.0,<5"
   claude plugin marketplace add langfuse/Claude-Observability-Plugin
   claude plugin install langfuse-observability@langfuse-observability
   ```

2. When the plugin asks, enter:

   - `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`: the three values from `.env` (Part A)

3. Run the workflow on one Jira story, as you normally do.

4. In Langfuse, open **Traces**. You should see one trace per turn, named `Claude Code - Turn N`, grouped by session, with the model calls, tool calls, and token usage inside.

5. If nothing appears, read the hook log:

   ```bash
   tail -f ~/.claude/state/langfuse_hook.log
   ```

**Skill content:** the plugin option "Capture skill instructions" is turned on, so the text of each invoked skill is stored in the trace. `CLAUDE.md` is not captured. Still record the git commit of the skills for every dataset run (Part C), so a baseline run can be reproduced.

**Sessions opened before the plugin was configured are not traced.** Close and reopen Claude Code after changing the plugin's options.

**Scope:** the plugin is enabled for the whole user account, so every Claude Code session on this machine is traced, not only the test workflow.

---

## Part C — Build the evaluation dataset

The dataset is what makes one release comparable with the next.

1. Pick 20 to 30 Jira stories that the QA team has already written and reviewed tests for. Include:

   - several features or components, not one area
   - a few stories the team considers hard or ambiguous
   - a few small, simple stories

2. For each story, record one dataset item in Langfuse (**Datasets → New dataset**, for example `uc01-baseline`):

   | Field           | Content                                                                                                     |
   | --------------- | ----------------------------------------------------------------------------------------------------------- |
   | Input           | The story key and a snapshot of the story text and acceptance criteria as they were when tests were written |
   | Expected output | The test cases the team finally accepted                                                                    |
   | Metadata        | Component, difficulty (simple, normal, hard), date                                                          |

   A snapshot is needed because the story in Jira may change later.

3. Run the Claude workflow once on each story with tracing on. Note the session for each run.

4. For each run, compare the generated tests with the expected output and record:

   - how many accepted tests the workflow also produced
   - how many accepted tests it missed
   - how many generated tests the team would reject, and why

   These three counts per story are the baseline. The reasons for rejection are the first input for the curated knowledge base (ADR-011).

The pass criteria for later releases are not defined yet. They are listed under "Still to design" in `ARCHITECTURE_DECISIONS.md` and are easier to set once these counts exist.

---

## Done when

- [ ] The check in Part A prints `HTTP 200`.
- [ ] A Claude workflow run appears in Langfuse as traces.
- [ ] The dataset has 20 to 30 items with expected outputs.
- [ ] Every item has a baseline run with its three counts and the skills commit recorded.

## Sources

- Langfuse Claude Code integration: https://langfuse.com/integrations/other/claude-code
- Langfuse coding agent tracing: https://langfuse.com/resources/engineering/coding-agent-tracing
