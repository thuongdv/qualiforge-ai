# QualiForge AI — Independent Architecture Review

You are acting as a Senior Software Architect reviewing the proposed architecture of QualiForge AI.

Read `docs/architecture/ARCHITECTURE.md` completely before responding.

## Your responsibilities

Independently evaluate the proposed architecture. Do not simply agree with the existing design.

Focus on:

1. Overall architecture and service boundaries.
2. Next.js, FastAPI, and LangGraph Python integration.
3. RAG and enterprise knowledge architecture.
4. Agent orchestration and workflow execution.
5. Database and data modeling.
6. LLM provider abstraction.
7. AI observability, tracing, token usage, and cost management.
8. Security, multi-tenancy, and permissions.
9. Deployment, scalability, and operational complexity.
10. MVP scope and implementation roadmap.

## Important constraints

- Prefer practical, maintainable solutions over unnecessary complexity.
- Do not introduce technologies without explaining their purpose.
- Consider the requirements of an AI Testing and Quality Engineering platform.
- Distinguish current requirements from future scalability requirements.
- Identify assumptions that need validation.
- Support important technical claims with official documentation.
- Do not modify source code or architecture files during this review.

## Required output

### 1. Executive assessment

Is this architecture suitable for the proposed product? Why or why not?

### 2. Architecture concerns

Identify the most important weaknesses, risks, and missing components.

### 3. Technology evaluation

For each major technology decision, provide:

- Current proposal.
- Alternative options.
- Advantages and disadvantages.
- Recommendation.
- Conditions that would change your recommendation.

### 4. Missing design decisions

Identify decisions that must be made before MVP development.

### 5. Recommended architecture changes

Provide specific changes, not just general suggestions.

### 6. MVP implementation plan

Suggest an implementation sequence that minimizes technical risk.

### 7. Open questions

List questions that the project owner must answer.

### 8. Final recommendation

Classify your recommendations as:

- Must change before MVP.
- Should change soon.
- Keep as proposed.
- Defer until later.

Be critical, technically specific, and pragmatic.

The goal is to improve the architecture through independent review, not to validate it automatically.
