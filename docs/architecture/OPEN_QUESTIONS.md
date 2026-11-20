# QualiForge AI — Open Questions

**Last updated:** 2026-11-20\
**Applies to:** `docs/architecture/ARCHITECTURE.md` v0.2.0

This file holds what is not yet decided: assumptions to validate, designs still to write, and decisions still to take. When an item is resolved, record it as a decision in `ARCHITECTURE_DECISIONS.md`, apply it to `ARCHITECTURE.md` with a version bump, and remove it here.

---

## 1. To validate before or during implementation

These are assumptions, not decisions.

| #   | Assumption                                                                                                     | Related decision |
| --- | -------------------------------------------------------------------------------------------------------------- | ---------------- |
| V1  | The Langfuse Cloud plan in use covers the expected trace volume, retention, and number of team members.        | ADR-007          |
| V2  | The Jira project does not require custom fields on Test issues that the platform does not yet supply.          | ADR-012          |
| V3  | The LangGraph PostgreSQL checkpointer behaves as described for multi-day approval waits.                       | ADR-003          |
| V4  | Company policy allows trace content on Langfuse Cloud in the US region for as long as the project stays there. | ADR-007          |
| V5  | Langfuse reports cost correctly for the chosen provider and model.                                             | ADR-017          |

---

## 2. Still to design

| #   | Item                                                                                                                                                                                                                                                    | Related decision | Needed by   |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------- |
| D1  | The database schema. The table diagram in section 4.3 of the Gemini review is the starting point, with knowledge item, feedback, and user tables added. It includes the traceability record from story to prompt and knowledge versions to Test issues. | ADR-004, ADR-011 | Step 2      |
| D2  | The description template for Test issues.                                                                                                                                                                                                               | ADR-012          | Step 2      |
| D3  | The pass criteria for the evaluation dataset.                                                                                                                                                                                                           | ADR-018          | Step 2 gate |
| D4  | Backup of the application database and the document bucket.                                                                                                                                                                                             | ADR-010          | Step 2      |
| D5  | How the run ID is passed to Langfuse so that a run and its trace are correlated, for example as the trace's session or metadata.                                                                                                                        | ADR-007          | Step 2      |
| D6  | The local development environment.                                                                                                                                                                                                                      | ADR-010          | Step 2      |
| D7  | The relationship model between source records, for example an explicit link table keyed by source system and external ID.                                                                                                                               | ADR-006          | Step 4      |

---

## 3. Decisions still to take

| #   | Question                                                                                                 | Related decision | When                           |
| --- | -------------------------------------------------------------------------------------------------------- | ---------------- | ------------------------------ |
| Q1  | Whether and when to self-host Langfuse.                                                                  | ADR-007          | Not scheduled                  |
| Q2  | Trace retention period.                                                                                  | ADR-007          | After trace volume is measured |
| Q3  | How retrieval quality is evaluated, for example by extending the dataset with expected source documents. | ADR-006, ADR-018 | Before step 4                  |
| Q4  | CI/CD: GitHub Actions is proposed but not decided.                                                       | —                | Before step 2                  |

---

## 4. Status of the questions raised in `ARCHITECTURE.md` v0.1.0

Section 14 of version 0.1.0 listed 22 questions for review. Both reviews in `docs/reviews/` answer them. This table shows where each now stands.

| #   | Question                                                 | Status                                                         |
| --- | -------------------------------------------------------- | -------------------------------------------------------------- |
| 1   | Knowledge System as a separate service?                  | Decided: a module in the one Python package (ADR-002)          |
| 2   | Redis dispatch or Temporal?                              | Decided: PostgreSQL jobs table (ADR-005); Temporal deferred    |
| 3   | Boundary between FastAPI and LangGraph                   | Described in `ARCHITECTURE.md` section 3.3                     |
| 4   | Checkpoints and worker recovery                          | Decided (ADR-003); to validate (V3)                            |
| 5   | Is PostgreSQL + pgvector sufficient?                     | Decided: yes (ADR-004)                                         |
| 6   | OpenSearch later?                                        | Deferred until measured need (ADR-004)                         |
| 7   | Relationships among stories, pages, tests, and code      | Still to design (D7)                                           |
| 8   | Permission inheritance and document deletion             | Decided: allowlist and nightly re-index (ADR-006)              |
| 9   | Retrieval evaluation                                     | Open (Q3)                                                      |
| 10  | Agents as modules or services?                           | Decided: Python modules (ADR-019)                              |
| 11  | Versioning of agent and workflow definitions             | Decided: git commit plus prompt version (ADR-019)              |
| 12  | Preventing unnecessary agent-to-agent delegation         | Decided: fixed graphs (ADR-003)                                |
| 13  | Tool permissions and unsafe external operations          | Decided: no write tools for LLM steps (ADR-014)                |
| 14  | Langfuse as the primary LLM observability platform?      | Decided: yes, Langfuse Cloud (ADR-007)                         |
| 15  | Normalizing token usage and cost across providers        | Decided: taken from Langfuse (ADR-017)                         |
| 16  | MLflow?                                                  | Not adopted; in the Deferred list                              |
| 17  | Prompt versions, evaluation datasets, model comparisons  | Decided: Langfuse (ADR-007, ADR-018)                           |
| 18  | Trace correlation across API, worker, retrieval, and LLM | Still to design (D5)                                           |
| 19  | Authentication and multi-tenancy                         | Decided: local accounts, single organization (ADR-015)         |
| 20  | Deployment target                                        | Decided: one internal server (ADR-010)                         |
| 21  | Concurrency, workflow duration, and data volume          | Answered in the Project context of `ARCHITECTURE_DECISIONS.md` |
| 22  | Backup, disaster recovery, and retention                 | Still to design (D4) and open (Q2)                             |
