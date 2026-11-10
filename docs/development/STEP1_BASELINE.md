# Step 1 — Baseline

This is step 1 of the order of work in `docs/architecture/ARCHITECTURE_DECISIONS.md` (ADR-020). It answers two questions before any platform code is written:

1. Does self-hosted Langfuse fit on the internal server (ADR-007)?
2. How good is the existing Claude workflow, measured on real stories (ADR-018)?

Commands marked "from Langfuse docs" are copied from the official pages listed at the end.

---

## Part A — Start Langfuse on the internal server

Langfuse's Docker Compose guide recommends a machine with at least 4 cores and 16 GiB of memory. The server has 16 GB, so it is at the recommended minimum before the platform itself is added. Part B measures the real usage.

1. Clone and enter the repository (from Langfuse docs):

   ```bash
   git clone https://github.com/langfuse/langfuse.git
   cd langfuse
   ```

2. Open `docker-compose.yml` and replace every value on a line marked `# CHANGEME` with a long random password. Generate one with:

   ```bash
   openssl rand -hex 32
   ```

3. Start it in the background:

   ```bash
   docker compose up -d
   ```

4. Open `http://<server-ip>:3000`. There is no default login: click **Sign up** to create the first user, then create an organization and a project.

5. In the project settings, create an API key pair. Keep the public key (`pk-lf-...`) and secret key (`sk-lf-...`) for Part C.

6. Allow incoming traffic from the internal network to ports `3000` (web) and `9090` (storage) only.

To stop: `docker compose down`. Adding `-v` also deletes all data.
To upgrade: stop, then `docker compose up --pull always`.

---

## Part B — Measure memory

Take three readings and write them into the table below.

```bash
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}"
free -h
df -h
```

| Reading | When                               | Langfuse containers total | `free -h` "available" | Disk used |
| ------- | ---------------------------------- | ------------------------- | --------------------- | --------- |
| 1       | 10 minutes after start, idle       |                           |                       |           |
| 2       | After Part C, about 10 traced runs |                           |                       |           |
| 3       | After Part D, the full dataset run |                           |                       |           |

**Working rule:** the server passes if at least 4 GB is still "available" at reading 3. That is the room reserved for the platform's own containers (web, API, worker, PostgreSQL). The 4 GB figure is an estimate, not a measurement. If the server fails, request more memory, as agreed in ADR-007.

---

## Part C — Trace the existing Claude workflow

Do this on the machine where the Claude workflow runs today.

1. Install the Langfuse SDK and the Claude Code plugin (from Langfuse docs). Python 3.9 or later is required.

   ```bash
   pip install "langfuse>=4.0,<5"
   claude plugin marketplace add langfuse/Claude-Observability-Plugin
   claude plugin install langfuse-observability@langfuse-observability
   ```

2. When the plugin asks, enter:

   - `LANGFUSE_PUBLIC_KEY`: the public key from Part A
   - `LANGFUSE_SECRET_KEY`: the secret key from Part A
   - `LANGFUSE_BASE_URL`: `http://<server-ip>:3000`

3. Run the workflow on one Jira story, as you normally do.

4. In Langfuse, open **Traces**. You should see one trace per turn, named `Claude Code - Turn N`, grouped by session, with the model calls, tool calls, and token usage inside.

5. If nothing appears, read the hook log:

   ```bash
   tail -f ~/.claude/state/langfuse_hook.log
   ```

**Known limit:** the trace does not capture the content of skills or `CLAUDE.md`. Record the git commit of the skills by hand for every dataset run (Part D), or the baseline cannot be reproduced.

---

## Part D — Build the evaluation dataset

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

- [ ] Langfuse is running on the internal server with changed secrets.
- [ ] The three memory readings are filled in, and the server passes or more memory has been requested.
- [ ] A Claude workflow run appears in Langfuse as traces.
- [ ] The dataset has 20 to 30 items with expected outputs.
- [ ] Every item has a baseline run with its three counts and the skills commit recorded.

## Sources

- Langfuse Docker Compose deployment: https://langfuse.com/self-hosting/deployment/docker-compose
- Langfuse Claude Code integration: https://langfuse.com/integrations/other/claude-code
- Langfuse coding agent tracing: https://langfuse.com/resources/engineering/coding-agent-tracing
