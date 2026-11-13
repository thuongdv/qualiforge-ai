# QualiForge AI — Architecture Decisions

**Last updated:** 2026-11-13\
**Decided by:** Project owner\
**Inputs:**

- `docs/architecture/ARCHITECTURE.md` v0.1.0 (the proposal)
- `docs/reviews/2026-11-10-claude-architecture-review.md` (adopted as the plan)
- `docs/reviews/2026-11-10-gemini-architecture-review.md` (selected points adopted)

Where this file and `ARCHITECTURE.md` disagree, this file wins. `ARCHITECTURE.md` has not yet been updated to match.

---

## Project context

These facts shape every decision below.

| Topic          | Fact                                                                                                                                  |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Builder        | One SDET, about 20 hours per week, working with AI coding assistants                                                                  |
| Users          | An internal QA team of 5 to 10 people                                                                                                 |
| Starting point | UC-01 (Jira story to reviewed test cases) already works as a Claude coding agent plus skills                                          |
| Goal           | A shared application where the team runs workflows, sees inside each run, compares releases, and enriches a team-owned knowledge base |
| Deployment     | Docker Compose on one internal server with 16 GB RAM and 100 GB disk                                                                  |
| Data policy    | Jira and Confluence content may be sent to external LLM providers and to Langfuse Cloud                                               |
| Not a goal     | Multi-tenant SaaS, cloud scaling, more than about 10 users                                                                            |

---

## Decisions

Each decision lists where it came from: the Claude review, the Gemini review, both, or the owner directly.

### ADR-001 — Frontend

- **Decision:** Next.js with TypeScript. Next.js holds no business logic and is not used as a backend-for-frontend. It calls FastAPI through a TypeScript client generated from the OpenAPI specification.
- **Why:** A second backend would have to be kept consistent with FastAPI. The generated client makes the build fail when frontend and API disagree.
- **Revisit when:** Not expected.
- **Source:** Both reviews.

### ADR-002 — Backend

- **Decision:** FastAPI. All Python code lives in one package with two entry points, the API and the worker.
- **Why:** One person cannot maintain many internal packages, and the API and worker share the same models.
- **Revisit when:** Not expected at this scale.
- **Source:** Both reviews.

### ADR-003 — Workflow orchestration

- **Decision:** LangGraph, with its checkpointer stored in PostgreSQL. Workflows are fixed graphs with explicit edges; no agent chooses another agent. The reviewer-to-designer loop is capped at 2 revisions, after which the run goes to human approval with the reviewer's warnings attached.
- **Why:** Checkpoints and interrupts let an approval wait for days without a worker being held. The cap prevents two agents from looping and consuming tokens.
- **Revisit when:** The LangGraph port scores worse than the existing workflow on the evaluation dataset and the gap cannot be closed (see ADR-018).
- **Source:** Both reviews. Loop cap from Gemini.

### ADR-004 — Database

- **Decision:** PostgreSQL with pgvector, plus PostgreSQL full-text search. LangGraph's checkpoint tables are kept separate from the business tables, and the user interface reads only business tables.
- **Why:** One database to run and back up. Checkpoint data is internal to LangGraph and changes when a graph changes.
- **Revisit when:** The index reaches millions of chunks, or filtered search is measured to be slow.
- **Source:** Both reviews. Table separation from Gemini.

### ADR-005 — Job queue and progress updates

- **Decision:** No Redis in the application. Runs are dispatched through a jobs table in PostgreSQL, polled by one worker process. The user interface polls run status every few seconds.
- **Why:** The load is a few concurrent runs for 10 users. Each run step is already written to PostgreSQL, so polling needs nothing extra.
- **Revisit when:** More than about 20 runs execute at the same time, or polling delay becomes a complaint.
- **Source:** Claude. Gemini recommended Redis with ARQ and Pub/Sub; not adopted.

### ADR-006 — Knowledge and retrieval

- **Decision:**
  - Knowledge has two kinds: curated items (ADR-011) and indexed reference content.
  - A record whose ID is known is fetched through the source system's API. Retrieval is used only to discover related content.
  - Indexed sources are an explicit allowlist of Jira projects and Confluence spaces.
  - The allowlist is re-indexed in full every night. A content hash skips re-embedding of unchanged documents.
  - Retrieval is built in step 4 of the roadmap, and only where the evaluation shows a gap that curated knowledge does not fill.
- **Why:** Access goes through shared credentials, so per-user permission filtering has nothing to filter. Atlassian Cloud cannot deliver webhooks to a server on the internal network.
- **Revisit when:** Teams with different access rights share the platform, or nightly freshness is not enough.
- **Source:** Claude. Content hash from Gemini.

### ADR-007 — AI observability

- **Decision:** Langfuse is the only observability tool. The project starts on Langfuse Cloud (US region); self-hosting is decided later. It provides traces, token and cost figures, prompt versions, datasets, and comparison between releases. Each run links to its Langfuse trace. Step records (name, status, inputs, outputs, tokens) are also stored in PostgreSQL, so the run list and run view work when Langfuse is unavailable. No separate OpenTelemetry collector is deployed.
- **Why:** Langfuse already covers run visibility and release comparison, two of the three problems the platform exists to solve. Building cost tables and comparison screens by hand would duplicate it.
- **Condition:** Traces contain story text and generated tests, so they leave the internal network. The owner accepted this on 2026-11-13. Moving to self-hosting later means changing the base URL and keys; traces and datasets already in the cloud project do not move automatically. Self-hosted Langfuse recommends at least 16 GiB of memory for itself, which is the whole internal server, so self-hosting needs more memory or a second machine.
- **Revisit when:** Not expected.
- **Source:** Claude. Step records in PostgreSQL from both reviews. Gemini recommended making Langfuse optional; not adopted.

### ADR-008 — Infrastructure monitoring

- **Decision:** Prometheus and Grafana are deferred. Container health checks and logs are used.
- **Why:** Two more services to maintain for a system one person operates.
- **Revisit when:** Someone other than the builder must operate the system, or outages go unnoticed.
- **Source:** Both reviews.

### ADR-009 — Document storage and upload

- **Decision:** Uploaded documents are stored through an S3-compatible interface. The application runs its own S3-compatible storage container, added in step 4 of the roadmap when upload is built. Upload supports Markdown (`.md`) and text-based PDF (`.pdf`) first. Scanned PDFs are rejected with a clear message.
- **Why:** Upload is a confirmed feature for enriching the knowledge base. Reusing the existing storage service adds no container. Scanned PDFs need OCR, which is separate work.
- **Revisit when:** Langfuse is self-hosted on the same server (its bundled storage could then be shared), or users need scanned documents or other file types.
- **Source:** Claude and owner. Gemini recommended deferring storage; not adopted.

### ADR-010 — Deployment

- **Decision:** Docker Compose on one internal server. The first compose file contains web, API, worker, and PostgreSQL. Langfuse is not in it while the project uses Langfuse Cloud (ADR-007).
- **Why:** It matches the confirmed environment and scale.
- **Revisit when:** Not expected.
- **Source:** Both reviews and owner.

### ADR-011 — Curated knowledge and the feedback loop

- **Decision:** The platform has a curated knowledge component. A reviewer's edit, rejection, or regeneration feedback, with its reason, becomes a proposed knowledge item. An approved item is injected into later runs by scope (project or component), without vector search. Each item records its author, status (proposed or approved), version, and the run or document it came from. The component is seeded with the content of the existing skills.
- **Why:** This is the main reason for the platform. Today the only way to improve the agent is to edit skills. The team needs corrections to accumulate as shared knowledge.
- **Revisit when:** Curated items grow too numerous to inject by scope; then they move into retrieval.
- **Source:** Claude and owner. Not present in `ARCHITECTURE.md` or the Gemini review.

### ADR-012 — Where generated tests are written

- **Decision:** The MVP creates Jira issues of type Test, linked to the user story. The Xray API is not used. Test steps go in the issue description, written in Atlassian Document Format, following one fixed template with bold section headings such as **Preconditions** and **Steps**. Each issue gets labels for the platform, provider, and model, for example `qualiforge`, `llm-provider-anthropic`, `llm-model-<name>`. The run ID, the approving user, and a link to the run go in the description.
- **Why:** It removes a second API and a second authentication scheme from the MVP. The team accepts steps in the description for now. A fixed template lets a later move to Xray steps parse them.
- **Revisit when:** The team needs Xray test steps, or needs generated tests added to Xray Test Sets.
- **Source:** Owner. Atlassian Document Format requirement from Gemini. Gemini recommended the Xray API and Test Sets; not adopted for the MVP.

### ADR-013 — Human approval

- **Decision:** Approval is per test case, not per batch. The reviewer can edit a test inline, select which tests to create, and choose one of three actions: approve, regenerate with feedback, or reject. The original and the edited version of each test are both stored. Time spent waiting for approval is excluded from run duration.
- **Why:** A batch-level yes or no forces reviewers to reject good work over one bad test. The stored edits feed the knowledge loop (ADR-011).
- **Revisit when:** Not expected.
- **Source:** Gemini, adopted.

### ADR-014 — Writes to external systems

- **Decision:** LLM steps have no write tools. Writes to Jira happen only in a deterministic step that runs after human approval. Each test case carries an idempotency key and stores the Jira key it produced, and a retry creates only the tests not yet created.
- **Why:** This is the practical defence against prompt injection from retrieved or uploaded content. LangGraph restarts an interrupted step from its beginning, so a write without idempotency would duplicate tests.
- **Revisit when:** Never.
- **Source:** Both reviews.

### ADR-015 — Authentication and roles

- **Decision:** Local accounts from the first version, with two roles, member and administrator. An administrator can promote other accounts. The first administrator is created from environment variables on first start. The system refuses to demote or delete the last administrator. The API obtains the current user through one function, so the login method can be replaced in one place.
- **Why:** There is no company identity provider. Without login, anyone on the internal network could replace stored credentials or trigger Jira writes, and approvals and knowledge items would have no author.
- **Revisit when:** The company provides an identity provider.
- **Source:** Claude and owner. Single-function seam from Gemini. Gemini recommended no authentication in the MVP; not adopted.

### ADR-016 — Integration credentials

- **Decision:** Jira and Confluence credentials are entered on a configuration page, open to administrators only. They are encrypted at rest with a key supplied through the environment, are never returned to the browser after saving, and are masked in traces. Each integration has a "test connection" action. The page states that every platform user can see everything the configured credentials can see.
- **Why:** Credentials in a database are a target. Shared credentials mean access rights in Jira and Confluence do not apply per platform user.
- **Revisit when:** Per-user access to source systems becomes a requirement.
- **Source:** Both reviews and owner. Test connection from Gemini.

### ADR-017 — LLM providers

- **Decision:** No custom provider abstraction and no proxy. The platform uses the chat model interface from LangGraph's ecosystem, with one primary provider and one fallback. Token and cost figures come from Langfuse.
- **Why:** A custom layer is code to maintain for every provider difference, and nothing in the MVP needs it.
- **Revisit when:** Per-team budgets or central key routing are required.
- **Source:** Claude. Gemini recommended a `ModelGateway` with a pricing table; not adopted.

### ADR-018 — Baseline and evaluation

- **Decision:** The existing Claude-based workflow is the baseline. Before the port, it is traced into Langfuse and a dataset of 20 to 30 real stories with their accepted test cases is built. The LangGraph port must score at least as well as the baseline on that dataset. The dataset is re-run for each release.
- **Why:** Without a baseline, there is no way to show that the rebuild is as good as what runs today, or that a release is better than the last.
- **Revisit when:** Not expected. The dataset grows over time.
- **Source:** Claude and owner.

### ADR-019 — Versioning of agents and workflows

- **Decision:** Agents are Python modules. Their version is the git commit plus the Langfuse prompt version. Both are recorded on each run. There are no agent or workflow registries in the MVP.
- **Why:** Registries are platform features with no user yet.
- **Revisit when:** Non-developers need to change agents or workflows.
- **Source:** Claude.

### ADR-020 — Order of work

- **Decision:**
  1. **Baseline.** The Claude workflow traced into Langfuse Cloud; the evaluation dataset built.
  2. **Walking skeleton.** Accounts, configuration page, run page, run list (completed, running, pending approval), UC-01 on LangGraph, approval, idempotent Jira test creation. Knowledge is the migrated skill content.
  3. **Feedback loop.** Capture of edits and rejections, review and approval of knowledge items, dataset re-run per release.
  4. **Retrieval and upload.** Upload and indexing of `.md` and text-based `.pdf` files; indexing of Confluence and existing tests, starting with duplicate detection.
  5. **Later.** UC-02, then UC-03 and UC-04.
- **Why:** Each step ends with something a user can see and removes one technical risk. The original roadmap built the knowledge layer before any workflow.
- **Revisit when:** Step 1 or the step 2 gate fails.
- **Source:** Claude. Both reviews agree the workflow comes before the knowledge layer.

---

## Deferred

Not part of the MVP. Each has a condition in the decision that would bring it back.

| Item                                                                         | Related decision |
| ---------------------------------------------------------------------------- | ---------------- |
| Prometheus and Grafana                                                       | ADR-008          |
| Redis                                                                        | ADR-005          |
| Xray API and Xray Test Sets                                                  | ADR-012          |
| Permission-aware retrieval, webhook sync, reranking                          | ADR-006          |
| Agent and workflow registries                                                | ADR-019          |
| LLM provider abstraction layer or proxy                                      | ADR-017          |
| Company single sign-on                                                       | ADR-015          |
| OCR for scanned PDFs                                                         | ADR-009          |
| UC-03 and UC-04, which run generated code and need an isolated sandbox first | ADR-020          |
| MLflow, Temporal, OpenSearch, Kubernetes                                     | —                |

---

## To validate before or during implementation

These are assumptions, not decisions.

1. The Langfuse Cloud plan in use covers the expected trace volume, retention, and number of team members (ADR-007).
2. The Jira project does not require custom fields on Test issues that the platform does not yet supply (ADR-012).
3. The LangGraph PostgreSQL checkpointer behaves as described for multi-day approval waits (ADR-003).
4. Company policy allows trace content on Langfuse Cloud in the US region for as long as the project stays there (ADR-007).
5. Langfuse reports cost correctly for the chosen provider and model (ADR-017).

## Still to design

- The database schema. The table diagram in section 4.3 of the Gemini review is the starting point, with knowledge item, feedback, and user tables added.
- The description template for Test issues (ADR-012).
- The pass criteria for the evaluation dataset (ADR-018).
- Backup of the application database and the document bucket.
