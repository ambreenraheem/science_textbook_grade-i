---
id: 002
title: Create Curriculum Browser Implementation Plan
stage: plan
date: 2026-01-10
surface: agent
model: claude-sonnet-4-5
feature: 001-curriculum-browser
branch: 001-curriculum-browser
user: Ambreen Abdul Raheem
command: /sp.plan
labels: ["plan", "architecture", "database-design", "streamlit", "grade-1"]
links:
  spec: specs/001-curriculum-browser/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-curriculum-browser/plan.md
  - specs/001-curriculum-browser/research.md
  - specs/001-curriculum-browser/data-model.md
  - specs/001-curriculum-browser/contracts/database-schema.sql
  - specs/001-curriculum-browser/quickstart.md
  - CLAUDE.md (agent context updated)
tests:
  - Constitution Check validation (all 9 principles evaluated)
  - Database schema constraints (CHECK, UNIQUE, FK)
  - Performance targets defined (queries <150ms)
---

## Prompt

run the plan now

Context: User requested implementation planning for Science Curriculum Browser feature after spec creation (feature 001).

## Response snapshot

Created comprehensive implementation plan with complete Phase 0 (Research) and Phase 1 (Design & Contracts) artifacts:

**Phase 0: Research** (research.md)
- **R1**: Selected Streamlit over FastAPI for rapid child-friendly UI development
- **R2**: YouTube embed API with privacy-enhanced mode (`youtube-nocookie.com`) and safety parameters (rel=0, disablekb=1)
- **R3**: SQLAlchemy 2.0 ORM with Neon PostgreSQL, connection pooling (5-10 connections)
- **R4**: Child-centered UX design: large touch targets (48x48px), Grade-1 fonts (18-24pt), high contrast (4.5:1), one concept per screen
- **R5**: Multi-layer caching strategy: database query cache (5min TTL), lazy image loading, YouTube iframe optimization

**Phase 1: Design & Contracts** (data-model.md, database-schema.sql, quickstart.md)

**Data Model**:
- 3 entities: Chapter (4 fixed rows), Lesson (5-8 per chapter), Video (1-2 per lesson)
- SQLAlchemy ORM models with type hints, relationships, constraints
- Query patterns with performance targets: <50ms chapters, <100ms lessons, <150ms lesson+videos

**Database Schema** (PostgreSQL):
- UUID primary keys with uuid_generate_v4()
- Indexed foreign keys (chapter_id, lesson_id)
- CHECK constraints: chapter_number (1-4), lesson_number (>=1), video display_order (1-2), content length (<=500 chars)
- JSONB for daily_life_examples array
- Soft deletion via is_active flag on videos
- Auto-updating updated_at timestamps via triggers
- Sample data: 4 chapters, 5 lessons, 3 placeholder videos

**Project Structure**:
- Library-driven: `src/lib/` (framework-agnostic) + `src/components/` (Streamlit UI)
- Multi-page Streamlit app: `src/pages/1_Chapters.py`, `2_Lessons.py`, `3_Lesson_View.py`
- Database migrations: `database/migrations/` (Alembic)
- Test structure: `tests/contract/`, `tests/integration/`, `tests/unit/`

**Constitution Check**: ✅ ALL 8 APPLICABLE PRINCIPLES PASSED
- I. Child-Safety First: Grade-1 vocab, embedded YouTube with safety params
- II. Discovery-First: Spec → Plan → Tasks workflow followed
- III. TDD for Critical Paths: Contract tests for DB operations
- IV. Library-Driven Architecture: `src/lib/` separates business logic
- V. Observability: Dual-layer errors, structured logging planned
- VI. Database Migrations: Alembic with rollback support
- VIII. Graceful Degradation: Fallback messages for missing content
- IX. Performance Budgets: <2s page load, <500ms queries
- VII. AI Filtering: N/A (no chatbot in this feature)

**Quickstart Guide**:
- 10-step setup: Python venv, Neon DB, schema creation, environment config, Streamlit run
- Troubleshooting section: connection errors, missing data, slow performance
- Performance validation queries included

**Agent Context Update**:
- Registered Python 3.11+ and Neon PostgreSQL in CLAUDE.md
- Technology stack now available for future task generation

## Outcome

- ✅ Impact: Completed discovery and design phases for curriculum browser. Implementation-ready with database schema, ORM models, query patterns, performance targets, and developer setup guide. Zero unknowns remaining.
- 🧪 Tests: Constitution Check (8/9 principles applicable, all passed), database constraint validation, query performance targets defined
- 📁 Files: Created plan.md, research.md, data-model.md, database-schema.sql, quickstart.md (5 design artifacts)
- 🔁 Next prompts:
  - Run `/sp.tasks` to generate dependency-ordered task list for implementation
  - After tasks, proceed with TDD: write contract tests first, then implement
  - Consider `/sp.adr` to document framework choice (Streamlit) and database design
- 🧠 Reflection: Research phase resolved 5 critical decisions (framework, video embedding, DB patterns, UX design, performance strategy) through comparative analysis. Data model enforces constitution requirements via database constraints (content length <=500 chars for readability, video order 1-2 max per lesson). Streamlit selection trades customization flexibility for rapid development velocity—appropriate for MVP, revisit for parent dashboard if richer UI needed.

## Evaluation notes (flywheel)

- Failure modes observed: None (plan workflow completed successfully)
- Graders run and results (PASS/FAIL): Constitution Check - PASS (8/8 applicable principles), Database constraints - PASS (CHECK, UNIQUE, FK all defined)
- Prompt variant (if applicable): Full research phase with comparative decision tables (5 research areas vs. assumptions-only approach)
- Next experiment (smallest change to try): Validate SQLAlchemy models against actual Neon database (run `alembic upgrade head` to test schema creation, measure actual query performance vs. targets)
