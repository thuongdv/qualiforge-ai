# QualiForge AI — Architecture Review Protocol for AI Assistants

**Moved from:** `docs/architecture/ARCHITECTURE.md` v0.1.0, section 15\
**Used with:** `docs/prompts/ARCHITECTURE_DISCUSSION.prompt.md`

`docs/architecture/ARCHITECTURE.md` is the shared architecture baseline for all AI assistants working on QualiForge AI. `docs/architecture/ARCHITECTURE_DECISIONS.md` records the decisions behind it.

## Review rules

When reviewing the architecture, assistants follow these rules:

1. Read `ARCHITECTURE.md` and `ARCHITECTURE_DECISIONS.md` completely before making recommendations.
2. Do not silently change existing architecture decisions.
3. Clearly distinguish confirmed decisions, proposals, assumptions, and open questions.
4. Challenge decisions when there are concrete technical or operational reasons. Name the ADR being challenged and address its "Revisit when" condition.
5. Compare alternatives using maintainability, scalability, complexity, security, cost, and developer experience.
6. Avoid introducing technologies without explaining the problem they solve.
7. Prefer the simplest architecture that satisfies the current requirements.
8. Consider compatibility with the existing repository and implementation constraints.
9. Identify risks, trade-offs, migration costs, and operational consequences.
10. Provide references to official documentation for important technical claims.
11. Do not modify architecture documents or implementation code during a review unless explicitly requested.
12. Treat a decision as approved only when it is recorded in `ARCHITECTURE_DECISIONS.md`, not merely because it appears in `ARCHITECTURE.md`.

## Required review output

Each AI assistant produces:

1. Overall assessment.
2. Architecture strengths.
3. Architecture weaknesses and risks.
4. Recommended changes, with rationale.
5. Alternative technologies and trade-offs.
6. Answers to the questions in `docs/architecture/OPEN_QUESTIONS.md`.
7. Proposed ADR changes.
8. A prioritized list of decisions required before implementation.

Save the review as `docs/reviews/YYYY-MM-DD-<reviewer>-<topic>.md`, and state the version of `ARCHITECTURE.md` it reviews.

## Review philosophy

The objective is not to make every AI assistant agree.

The objective is to discover incorrect assumptions, hidden complexity, missing requirements, and better technical alternatives before implementation.

All architecture changes must be explicitly discussed and recorded in `ARCHITECTURE_DECISIONS.md`, then applied to `ARCHITECTURE.md` with a version bump.
