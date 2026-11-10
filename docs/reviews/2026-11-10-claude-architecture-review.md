# QualiForge AI — Architecture Review (Claude)

**Reviewer:** Claude (Fable 5), acting as independent senior architect
**Date:** 2026-11-10
**Reviewed document:** `docs/architecture/ARCHITECTURE.md` v0.1.0
**Review prompt:** `docs/prompts/ARCHITECTURE_DISCUSSION.prompt.md`
**Status:** Review only. No architecture or source files were changed.

---

## 0. Context confirmed with the project owner

The review is based on these facts, which the owner confirmed and which are not in the architecture document.

| Topic           | Confirmed fact                                                                                                                                                                                                  |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Builder         | One SDET, about 20 hours per week, working with AI coding assistants                                                                                                                                            |
| Users           | The builder first, then an internal QA team of 5 to 10 people                                                                                                                                                   |
| Existing state  | UC-01 (Jira story to reviewed test cases) already works as a coding agent plus skills, run with Claude and Antigravity                                                                                          |
| Why a platform  | The workflow lives on one machine, runs cannot be inspected, releases cannot be compared, and the only way to improve it is to edit skills                                                                      |
| Core goal       | A shared application where the team runs workflows, sees their status, and enriches a team-owned knowledge base so that the agent improves from knowledge and not from prompt edits                             |
| Deployment      | Docker Compose on one internal server with 16 GB RAM and 100 GB disk                                                                                                                                            |
| Data policy     | Jira and Confluence content may be sent to external LLM providers                                                                                                                                               |
| Identity        | No company identity provider                                                                                                                                                                                    |
| External access | Jira and Confluence credentials are entered on a configuration page and shared by the platform                                                                                                                  |
| Test target     | Xray is on Cloud, but the first version creates Jira issues of type Test, linked to the user story, instead of calling the Xray API. Test steps go in the issue description, which the team accepts for the MVP |
| Authorship      | Jira shows the shared key's account as creator. Run details such as provider and model are added to the issue as labels                                                                                         |
| Baseline        | The Claude-based workflow                                                                                                                                                                                       |
| Server memory   | More RAM can be requested if Langfuse does not fit in 16 GB                                                                                                                                                     |
| Document upload | A real feature, used to enrich the knowledge base. Markdown (`.md`) and PDF (`.pdf`) first                                                                                                                      |
| Frontend        | Next.js is confirmed                                                                                                                                                                                            |
| Administration  | An administrator can promote other accounts to administrator                                                                                                                                                    |
| "Manage tasks"  | A view of completed, running, and pending (awaiting approval) workflow runs                                                                                                                                     |
| Out of scope    | Multi-tenant SaaS, Kubernetes, cloud scaling, more than about 10 users                                                                                                                                          |

"Scalable" is read here as "can grow without a rewrite", not "built for load now".

---

## 1. Executive assessment

The technology choices are mostly sound. The scope and the order of work are not suitable for this project.

The document describes a general workflow-execution platform: nine containers, three connectors, and a permission-aware RAG layer, all before the first workflow runs. The owner needs four things:

1. A shared way to run the workflow that already exists.
2. Visibility inside each run.
3. Comparison between releases.
4. A loop that turns reviewer corrections into team knowledge.

Langfuse already provides the second and most of the third. The fourth is the main reason for the project and is missing from the document. For one person at 20 hours per week, the proposed Phase 1 is where the project is most likely to stall.

---

## 2. Architecture concerns

Ordered by importance.

1. **No knowledge feedback loop.** Knowledge is modelled only as synchronization from Jira, Confluence, and Xray. There is no entity for team-written rules, no capture of reviewer edits or rejections, and no path from a correction to an approved knowledge item.

2. **Langfuse may not fit on the server.** Self-hosted Langfuse needs two application containers plus PostgreSQL, ClickHouse, Redis, and S3-compatible storage. The documented minimums add up to about 25 GiB of RAM. The server has 16 GB, and it must also run the platform itself. This must be tested before anything else is built.

3. **Phase 1 delivers nothing visible.** Three connectors, incremental sync, deletion propagation, hybrid retrieval, reranking, and permission filtering all come before a user sees anything.

4. **The existing workflow is ignored.** The roadmap rebuilds UC-01 from scratch and captures no baseline, so there is no way to prove the rebuild is at least as good as what runs today.

5. **Duplicate writes to Jira.** LangGraph restarts an interrupted node from its beginning when it resumes. A retry after a partial create will duplicate test issues unless the write is idempotent.

6. **No data model.** Section 16 of the document requires defined entities and relationships. The document defines none.

7. **Stored credentials are a new attack surface.** A configuration page for Jira and Confluence API keys means secrets live in the database. The document says "secure API key management" but does not say how.

8. **Shared credentials remove per-user permissions and authorship.** Every user sees whatever the configured key can see, and every created test appears in Jira as created by the key's account.

9. **Custom dashboards duplicate Langfuse.** The execution, cost, and observability dashboards and trace visualization in Phase 3 already exist there.

---

## 3. Technology evaluation

### 3.1 Frontend: Next.js, optionally as a BFF

- **Alternative:** A Python UI framework such as Streamlit.
- **Trade-off:** Next.js suits review, edit, and approval screens, but it is a second language and toolchain for a solo Python-oriented builder. A BFF adds a second backend to keep consistent with FastAPI.
- **Recommendation:** Keep Next.js. Remove the BFF option. Next.js calls FastAPI through the generated TypeScript client and holds no business logic.
- **Would change if:** Nothing expected. The owner has confirmed Next.js. Note that Next.js is a framework built on React, so the screens are written as React components.

### 3.2 Backend: FastAPI

- **Alternative:** Next.js API routes only.
- **Trade-off:** FastAPI shares code and types with the Python worker. A Next.js-only backend would split the business logic across two languages.
- **Recommendation:** Keep.
- **Would change if:** Nothing at this scale.

### 3.3 Orchestration: LangGraph

- **Alternative:** Run the existing coding agent headless behind the API.
- **Trade-off:** Running the existing agent avoids a rewrite, but it ties the platform to one agent vendor and gives no per-step structure for evaluation. LangGraph gives explicit steps, checkpoints, and interrupts, so an approval can wait for days without a held worker. The cost is a rewrite whose output quality must be re-proven.
- **Recommendation:** Keep LangGraph, but port only after a baseline exists (see section 6, step 1).
- **Would change if:** The port scores worse than the current agent on the evaluation dataset and the gap cannot be closed.

### 3.4 Database and vector search: PostgreSQL + pgvector

- **Alternative:** OpenSearch or a dedicated vector database.
- **Trade-off:** One database to run and back up. pgvector applies filters after the index scan, so heavily filtered queries can return too few rows; version 0.8.0 added iterative index scans to address this. PostgreSQL full-text search covers the keyword side of hybrid retrieval.
- **Recommendation:** Keep.
- **Would change if:** The index reaches millions of chunks, or filtered search becomes slow in measurement.

### 3.5 Queue: Redis

- **Alternative:** A jobs table in PostgreSQL, polled by one worker process.
- **Trade-off:** Redis is a proven queue, but it is one more service to run for a workload of a few concurrent runs. LangGraph checkpoints already persist run state in the database.
- **Recommendation:** Drop Redis for the application. Use a jobs table.
- **Would change if:** More than about 20 runs execute concurrently, or scheduled fan-out sync jobs appear.

### 3.6 Object storage: MinIO

- **Alternative:** A Docker volume on the server's disk.
- **Trade-off:** Document upload is a confirmed feature, so original files need a home. The S3 API keeps a later move to cloud storage simple. A separate MinIO container is not needed for that: the Langfuse stack already includes S3-compatible storage.
- **Recommendation:** Keep the S3 interface. Reuse the storage service that ships with the Langfuse stack, with a separate bucket and separate credentials.
- **Would change if:** Langfuse moves off the server (see 3.7). Then run one MinIO container for the application.

### 3.7 AI observability: Langfuse + OpenTelemetry

- **Alternative:** MLflow, LangSmith, or Langfuse Cloud instead of self-hosting.
- **Trade-off:** Langfuse covers traces, token and cost data, prompt versions, datasets, and side-by-side experiment comparison, which is most of what the owner wants to see. Its self-hosted footprint is large (see concern 2). Its Python SDK is built on OpenTelemetry, so a separate collector adds nothing at this stage.
- **Recommendation:** Keep Langfuse as the only observability tool. Do not add a separate OpenTelemetry collector. Do not introduce MLflow.
- **Would change if:** Nothing expected. If the 16 GB server cannot host it, the owner will request more memory.

### 3.8 Infrastructure monitoring: Prometheus + Grafana

- **Alternative:** Container health checks and logs.
- **Trade-off:** Two more services and dashboards to maintain, for a system one person operates for ten users.
- **Recommendation:** Defer.
- **Would change if:** Someone other than the builder must operate the system, or outages go unnoticed.

### 3.9 LLM provider abstraction

- **Alternative:** A LiteLLM proxy, or a custom normalized interface as the document proposes.
- **Trade-off:** A custom layer is code to write and maintain for every provider difference. A proxy is another container.
- **Recommendation:** Do not build one. Use the chat model interface that ships with LangGraph's ecosystem, configured with one primary provider and one fallback. Take token and cost figures from Langfuse.
- **Would change if:** Per-team budgets or central key routing become requirements.

### 3.10 Deployment: Docker Compose

- **Recommendation:** Keep. Nothing at this scale would change it.

---

## 4. Missing design decisions

These must be decided before MVP development.

1. **Knowledge item model.** Scope (project or component), author, status (proposed or approved), version, and a link to the run or uploaded document that produced it.
2. **Core schema.** Project, user, run, run step, approval, generated test case with its edits, feedback, knowledge item, source document, chunk.
3. **Traceability record.** Which Jira story, prompt versions, and knowledge versions produced which Jira test issues.
4. **Description format for test steps.** Decided: steps go in the Jira issue description, because Jira's REST API cannot write Xray's internal step data. Still to define: one fixed description template, so a later move to Xray steps can parse it.
5. **Credential storage.** Encryption at rest with a key held outside the database, admin-only access, and values never returned to the browser after saving.
6. **Label scheme.** Decided: run details go on the issue as labels. Still to define: the exact label names and which details are included (see section 5, change 10).
7. **Authentication.** Local accounts, since there is no identity provider. Decide who creates accounts and whether two roles (member, admin) are enough.
8. **Evaluation set.** Which stories form it and what counts as a pass.
9. **Backup.** The knowledge base and uploaded documents are the only data that cannot be regenerated.

---

## 5. Recommended architecture changes

1. **Add a Feedback and Curated Knowledge component.** A reviewer's edit or rejection, with a reason, becomes a proposed knowledge item. Once approved, it is injected into later runs by scope. Seed it with the content of the current skills.

2. **Split knowledge into two kinds.**
   - Curated items: small, team-written, injected by scope without vector search.
   - Indexed reference content: Confluence pages, existing tests, and uploaded documents, retrieved by search.

3. **Reduce the MVP compose file** to web, API, worker, PostgreSQL, and the Langfuse stack.

4. **Link each run to its Langfuse trace.** Build no trace, cost, or observability dashboards in the platform.

5. **Make the Jira write idempotent.** Put test creation in its own deterministic step after the approval interrupt, and store an idempotency key and the resulting Jira key per test case.

6. **LLM steps get no write tools.** Only deterministic steps, after human approval, write to external systems. This is the practical defence against prompt injection from Confluence or uploaded content.

7. **Replace permission-aware retrieval with an explicit allowlist** of indexed Jira projects and Confluence spaces, since access goes through shared credentials. State on the configuration page that every platform user can see everything the key can see.

8. **Replace webhook and incremental sync with a nightly full re-index** of the allowlist.

9. **Encrypt stored credentials** with a key supplied through the environment, restrict the configuration page to admins, and mask secrets in traces.

10. **Label every created Jira issue with its origin.** Add labels for the platform, provider, and model, for example `qualiforge`, `llm-provider-anthropic`, `llm-model-<name>`. Jira labels cannot contain spaces. Keep the label set small and fixed: put the run ID, the approving user, and a link back to the run in the description, because a label per run or per person would clutter Jira's label list. The platform's approval record remains the authoritative source for who approved.

11. **Collapse the repository** to `apps/web` and `apps/api`, with workflows, knowledge, and integrations as modules. Agents are Python modules. Their version is the git commit plus the Langfuse prompt version.

12. **Build the run list early.** A page listing completed, running, and pending-approval runs is the owner's definition of task management and needs only the run table.

---

## 6. MVP implementation plan

Each step ends with something a user can see, and each removes one technical risk.

| Step                    | Work                                                                                                                                                                            | Risk removed                                                                            |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| 1. Baseline             | Start Langfuse on the server and measure memory. Trace the existing Claude-based workflow into it. Build a dataset of 20 to 30 real stories with their accepted test cases.     | Whether Langfuse fits in 16 GB. Whether the rebuild can be measured.                    |
| 2. Walking skeleton     | Local accounts, credential configuration page, run page, run list, UC-01 ported to LangGraph, approval, idempotent Jira test creation. Knowledge is the migrated skill content. | Whether the port matches the baseline. Whether checkpoint and approval work end to end. |
| 3. Feedback loop        | Capture edits and rejections, knowledge item review and approval, re-run the dataset per release.                                                                               | Whether curated knowledge measurably improves output.                                   |
| 4. Retrieval and upload | Upload, parsing, and indexing of `.md` and text-based `.pdf` files. Index Confluence and existing tests, starting with duplicate detection.                                     | Whether retrieval adds value beyond curated knowledge.                                  |
| 5. Later                | UC-02, then UC-03 and UC-04. The last two execute generated code, which needs a sandbox and is a separate class of risk.                                                        | —                                                                                       |

Gate for step 2: the LangGraph port scores at least as well as the baseline on the dataset.

---

## 7. Open questions

Still unanswered after the owner's input.

All questions raised during the review have been answered. Three details follow from those answers and need a decision during implementation:

1. **First administrator.** Administrators can promote other accounts, but the first one has to come from somewhere. Recommended: create it from environment variables on first start.
2. **Last administrator.** The system must refuse to demote or delete the only remaining administrator. Recommended: keep at least two.
3. **Scanned PDFs.** Upload supports `.md` and `.pdf` first. PDFs that contain text can be parsed directly. Scanned PDFs are images and need OCR, which is a separate piece of work. Recommended: reject them with a clear message in the first version.

---

## 8. Final recommendation

### Must change before MVP

- Add the feedback and curated knowledge component.
- Test Langfuse on the 16 GB server first, and request more memory if it does not fit.
- Capture a baseline from the existing workflow first.
- Define the core schema and the traceability record.
- Decide credential storage, authentication, and authorship.
- Make Jira writes idempotent.
- Reorder the roadmap so the first workflow comes before the knowledge foundation.

### Should change soon

- Drop Redis from the application.
- Reuse the Langfuse stack's S3-compatible storage instead of a separate MinIO container.
- Collapse the repository structure.
- Remove the BFF option.
- Link to Langfuse instead of building dashboards.

### Keep as proposed

- Next.js, FastAPI, LangGraph, PostgreSQL with pgvector, Langfuse, Docker Compose.
- The S3 interface for documents.
- The split between deterministic and agentic steps.
- Human approval before external writes.
- Direct API calls for known records, retrieval for discovery.

### Defer until later

- Prometheus and Grafana.
- Permission-aware retrieval, webhook sync, reranking.
- Agent and workflow registries.
- A provider abstraction layer.
- Xray API integration.
- MLflow, Temporal, OpenSearch.
- UC-03 and UC-04.

---

## 9. Answers to the document's open questions

| #   | Question                                | Answer                                                                                                                    |
| --- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| 1   | Knowledge system as a separate service? | No. A module in the API application.                                                                                      |
| 2   | Redis dispatch or Temporal?             | Neither. A PostgreSQL jobs table and LangGraph checkpoints.                                                               |
| 3   | FastAPI and LangGraph boundary          | FastAPI owns runs, approvals, permissions, and external writes policy. LangGraph owns the steps inside one run.           |
| 4   | Checkpoints and recovery                | LangGraph checkpointer in PostgreSQL; resume by run ID after approval or worker restart.                                  |
| 5   | Is pgvector sufficient?                 | Yes, for one organization's selected projects and spaces.                                                                 |
| 6   | OpenSearch later?                       | Only if measured retrieval speed or quality requires it.                                                                  |
| 7   | Relationship model                      | Explicit link table between source records, keyed by source system and external ID.                                       |
| 8   | Permission inheritance and deletion     | Not needed with shared credentials and an allowlist. Nightly re-index handles deletion.                                   |
| 9   | Retrieval evaluation                    | The dataset from step 1, extended with expected source documents.                                                         |
| 10  | Agents as modules or services?          | Python modules.                                                                                                           |
| 11  | Versioning definitions                  | Git commit plus Langfuse prompt version.                                                                                  |
| 12  | Preventing unnecessary delegation       | Fixed graph with explicit edges; no agent chooses another agent.                                                          |
| 13  | Tool permissions                        | LLM steps have no write tools.                                                                                            |
| 14  | Langfuse as primary?                    | Yes, subject to the memory test.                                                                                          |
| 15  | Normalizing usage and cost              | Take both from Langfuse; store per-run totals in PostgreSQL.                                                              |
| 16  | MLflow?                                 | No.                                                                                                                       |
| 17  | Prompts, datasets, comparisons          | Langfuse prompt management, datasets, and experiments.                                                                    |
| 18  | Trace correlation                       | Pass the run ID as the trace's session or metadata from API to worker.                                                    |
| 19  | Auth and multi-tenancy                  | Local accounts, two roles, single organization.                                                                           |
| 20  | Deployment target                       | One internal server.                                                                                                      |
| 21  | Concurrency and volume targets          | 10 users, a few concurrent runs, approval waits of days.                                                                  |
| 22  | Backup and retention                    | Nightly dump of the application database and document bucket. Trace retention to be set after the disk usage is measured. |

---

## 10. Verification notes

Not checked against official documentation, and to be treated as assumptions:

- LangGraph PostgreSQL checkpointer setup details.
- Confluence permission API behaviour.
- Langfuse cost calculation per provider.
- Whether the Langfuse stack runs acceptably below its listed minimums. The 25 GiB figure is the sum of those minimums.

## Sources

- Langfuse self-hosting: https://langfuse.com/self-hosting
- Langfuse scaling and minimum resources: https://langfuse.com/self-hosting/configuration/scaling
- Langfuse ClickHouse requirement: https://langfuse.com/self-hosting/deployment/infrastructure/clickhouse
- Langfuse OTel-based Python SDK: https://langfuse.com/changelog/2025-05-23-otel-based-python-sdk
- Langfuse Claude Agent SDK integration: https://langfuse.com/integrations/frameworks/claude-agent-sdk
- Langfuse coding agent tracing: https://langfuse.com/resources/engineering/coding-agent-tracing
- Langfuse experiments via UI: https://langfuse.com/docs/evaluation/experiments/experiments-via-ui
- Langfuse prompt version control: https://langfuse.com/docs/prompt-management/features/prompt-version-control
- LangGraph interrupts: https://docs.langchain.com/oss/python/langgraph/interrupts
- LangGraph checkpointers: https://docs.langchain.com/oss/python/langgraph/checkpointers
- Xray API clarifications: https://docs.getxray.app/space/XRAYCLOUD/44577823/Clarifications+on+APIs+usage
- Xray Server/DC REST API: https://docs.getxray.app/display/XRAY/REST+API
- pgvector README: https://github.com/pgvector/pgvector/blob/master/README.md
