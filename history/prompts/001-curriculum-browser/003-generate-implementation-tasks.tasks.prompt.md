---
id: 003
title: Generate Implementation Tasks for Curriculum Browser
stage: tasks
date: 2026-01-10
surface: agent
model: claude-sonnet-4-5
feature: 001-curriculum-browser
branch: 001-curriculum-browser
user: Ambreen Abdul Raheem
command: /sp.tasks
labels: ["tasks", "implementation", "tdd", "user-stories", "database-design"]
links:
  spec: specs/001-curriculum-browser/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-curriculum-browser/tasks.md
tests:
  - Task format validation (all 58 tasks follow checkbox + ID + label + description format)
  - Constitution compliance (all 9 principles mapped to tasks)
  - User story independence (each story has complete task set)
---

## Prompt

generate the tasks now

Context: User requested task generation after implementation planning complete (spec, research, plan, data-model, contracts all created for feature 001-curriculum-browser).

## Response snapshot

Generated comprehensive task list with 58 dependency-ordered tasks organized by 3 user stories:

**Task Organization by User Story**:

**Phase 1: Setup** (6 tasks, T001-T006)
- Project structure, requirements.txt, .env.example, .gitignore, README, pytest config
- All parallelizable ([P] markers)

**Phase 2: Foundational** (11 tasks, T007-T017) - BLOCKS ALL USER STORIES
- Database connection pool (T007)
- Utilities: logger (T008), config (T009)
- Alembic initialization (T010)
- SQLAlchemy ORM models (T011): Chapter, Lesson, Video per data-model.md
- Initial migration (T012) + seed data (T013)
- Static assets: placeholder images (T014), child-friendly CSS (T015)
- Base content loader (T016) + Streamlit app entry (T017)

**Phase 3: User Story 1 - Browse Chapters** (6 tasks, T018-T023) - P1 MVP
- TDD: Contract test for get_all_chapters() (T018), integration test for navigation (T019)
- Implementation: query function (T020), ChapterCard component (T021), Chapters page (T022), logging (T023)
- **MVP Checkpoint**: 23 total tasks (40% of project) delivers chapter browsing

**Phase 4: User Story 2 - View Lesson Content** (13 tasks, T024-T036) - P2
- TDD: 4 contract tests (T024-T026), 1 integration test (T027) for lesson queries
- Implementation: 3 query functions (T028-T030), LessonCard (T031), LessonViewer (T032), 2 pages (T033-T034), validation (T035), logging (T036)
- **Parallel Opportunity**: T028-T031 can run simultaneously (different files)

**Phase 5: User Story 3 - Watch Educational Videos** (9 tasks, T037-T045) - P3
- TDD: 3 tests (T037 contract, T038 unit, T039 integration)
- Implementation: query function (T040), YouTube embedder (T041), VideoPlayer component (T042), update LessonViewer (T043), logging (T044), real video testing (T045)
- **Dependency**: Requires T032 (LessonViewer) from US2

**Phase 6: Polish & Cross-Cutting** (13 tasks, T046-T058)
- Streamlit theme (T046), lazy loading (T047), loading spinners (T048)
- Graceful degradation: placeholders (T049), retry logic (T050)
- Performance monitoring (T051), unit tests (T052)
- Validation: quickstart (T053), performance testing (T056), accessibility (T057)
- Documentation: README (T054), architecture docs (T055), code cleanup (T058)

**Key Metrics**:
- Total: 58 tasks
- Tests: 9 tasks (16%) - TDD for all DB operations per Constitution III
- Parallelizable: 24 tasks marked [P] (41%)
- MVP: 23 tasks (Setup + Foundational + US1)
- Database queries: 9 query functions with <150ms performance targets

**Constitution Compliance Mapping**:
- I. Child-Safety: T015 (CSS), T041 (YouTube safety), T042 (fallback messages)
- II. Discovery-First: All tasks reference plan.md, data-model.md
- III. TDD Critical Paths: T018-T019, T024-T027, T037-T039 (DB tests before implementation)
- IV. Library-Driven: T016, T020, T028-T030, T040-T041 (src/lib/ framework-agnostic)
- V. Observability: T008, T023, T036, T044, T051 (structured logging)
- VI. Migrations: T010, T012, T013 (Alembic with rollback)
- VII. AI Filtering: N/A (no chatbot)
- VIII. Graceful Degradation: T049, T050 (placeholders, retries)
- IX. Performance: T047, T051, T056 (lazy load, monitoring, testing)

**Implementation Strategies Documented**:
1. **MVP First**: Setup + Foundational + US1 = 23 tasks (chapter browsing demo-ready)
2. **Incremental Delivery**: Each user story adds independently testable value
3. **Parallel Teams**: 2-3 developers can work on US1, US2, US3 simultaneously after Foundational phase

**Dependencies & Execution Order**:
- Setup → Foundational (blocks everything)
- Foundational → US1, US2 (parallel)
- Foundational + US2 (T032) → US3 (extends LessonViewer)
- All stories → Polish

## Outcome

- ✅ Impact: Created implementation-ready task list with 58 dependency-ordered tasks. Each user story independently testable with clear checkpoints. TDD enforced for database operations (9 tests). 41% of tasks parallelizable. MVP defined at 23 tasks (40% of project).
- 🧪 Tests: 9 test tasks covering database contracts, integration, and unit tests per Constitution III (TDD mandatory for DB operations)
- 📁 Files: Created tasks.md with complete task breakdown, dependencies, parallel opportunities, implementation strategies
- 🔁 Next prompts:
  - Begin implementation: Start with Phase 1 (Setup) tasks T001-T006
  - After Foundational phase: Create feature branch, commit initial structure
  - After US1 MVP: Test independently, deploy to staging, gather feedback
  - Optional: Run `/sp.adr` to document Streamlit choice before implementation
- 🧠 Reflection: Task organization by user story enables true incremental delivery—each story is a complete vertical slice (tests + queries + UI + logging). Foundational phase (11 tasks) front-loads database and ORM setup, preventing rework. US3 dependency on US2's LessonViewer component (T043 depends on T032) is acceptable—still maintains story independence for testing. Parallel opportunities (24 tasks) enable 2-3 developer team to work efficiently without conflicts.

## Evaluation notes (flywheel)

- Failure modes observed: None (task generation completed successfully with all format validations)
- Graders run and results (PASS/FAIL):
  - Task format validation - PASS (all 58 tasks follow `- [ ] [ID] [P?] [Story?] Description with path` format)
  - Constitution compliance - PASS (all 9 principles mapped to specific tasks)
  - User story independence - PASS (each story has tests + implementation + validation)
- Prompt variant (if applicable): User-story-first organization (vs. layer-first like "all models, then all services")
- Next experiment (smallest change to try): Track actual task completion times during implementation to validate 23-task MVP estimate and refine future task breakdown granularity (some tasks like T032 LessonViewer may need splitting)
