---
id: 001
title: Create Grade-1 Science Learning Constitution
stage: constitution
date: 2026-01-10
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: Ambreen Abdul Raheem
command: /sp.constitution
labels: ["constitution", "child-safety", "educational-app", "python", "initial-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

create constitution according to "a complete, production-grade Claude Code skill folder structure for Grade-1 Science Learning Web Application project, written in clear technical English and aligned with Anthropic best practices.

This structure assumes:

Python-based web app

Child-safe education domain

OpenAI SDK chatbot

Neon database

Vercel / Streamlit deployment

Discovery-first, implementation-second workflow"

## Response snapshot

Created comprehensive constitution v1.0.0 for Grade-1 Science Learning Web Application with 9 core principles:

1. **Child-Safety First (NON-NEGOTIABLE)**: Age-appropriate content filtering, no PII collection, COPPA compliance, Grade-1 vocabulary (Lexile 190L-530L)

2. **Discovery-First Development**: Mandatory `/sp.specify` → `/sp.plan` → `/sp.tasks` workflow before implementation

3. **Test-Driven Development for Critical Paths (CONDITIONAL)**: TDD mandatory for database, AI interactions, auth; optional for UI/static content

4. **Python-First, Library-Driven Architecture**: Business logic in standalone libraries (`src/lib/`), framework-agnostic, independently testable

5. **Observability & Child-Friendly Logging**: Dual-layer error messages (child-friendly + technical), parent dashboard for monitoring, structured JSON logging

6. **Database Schema Versioning & Migration Safety**: Versioned migrations with rollback plans, deprecation cycles for breaking changes

7. **AI Content Filtering Pipeline (MANDATORY)**: Multi-layer filtering (OpenAI moderation + vocabulary validator + blocked topics), <200ms performance budget

8. **Offline Resilience & Graceful Degradation**: Bundled core content, fallback modes when external services unavailable, aggressive timeouts (5s)

9. **Performance Budgets for Child Engagement**: <2s page load, <5s AI response, <500ms database queries, 30+ fps animations

Additional sections created:
- **Security & Privacy Requirements**: COPPA compliance, data minimization, API key management, rate limiting, role-based access
- **Development Workflow**: Branch strategy, code review requirements, deployment pipeline (local → staging → QA → production)
- **Governance**: Amendment process, compliance verification, complexity justification requirements

Templates verified compatible:
- ✅ plan-template.md (Constitution Check section)
- ✅ spec-template.md (Requirements alignment)
- ✅ tasks-template.md (Task categorization matches principles)

## Outcome

- ✅ Impact: Established foundational governance for child-safe educational application development. All future features must align with 9 core principles emphasizing safety, testability, and age-appropriate design.
- 🧪 Tests: No tests created (constitution is governance document)
- 📁 Files: Created `.specify/memory/constitution.md` (v1.0.0, ratified 2026-01-10)
- 🔁 Next prompts:
  - Create first feature spec using `/sp.specify` (e.g., chatbot integration, content display, progress tracking)
  - Generate ADR for technology stack decisions (OpenAI vs alternatives, Streamlit vs FastAPI, Neon schema design)
  - Setup project structure per Principle IV (library-driven architecture)
- 🧠 Reflection: Constitution balances child safety (non-negotiable) with developer productivity (conditional TDD, graceful degradation). Performance budgets and offline resilience address practical constraints of educational settings (slow networks, unreliable infrastructure). Discovery-first workflow prevents premature implementation before requirements are clear.

## Evaluation notes (flywheel)

- Failure modes observed: None (initial creation)
- Graders run and results (PASS/FAIL): N/A (manual constitution review required by stakeholders)
- Prompt variant (if applicable): N/A (baseline constitution)
- Next experiment (smallest change to try): Validate constitution principles against sample feature (e.g., chatbot) to identify missing constraints or overly rigid rules
