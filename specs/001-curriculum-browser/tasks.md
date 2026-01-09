---

description: "Task list for Science Curriculum Browser implementation"
---

# Tasks: Science Curriculum Browser

**Input**: Design documents from `/specs/001-curriculum-browser/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/database-schema.sql

**Tests**: Test tasks included per Constitution III (TDD mandatory for database operations). Tests are required for database queries, optional for UI components.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project structure**: `src/`, `tests/`, `database/` at repository root
- All paths shown below use this structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure per plan.md (src/lib/, src/components/, src/pages/, src/utils/, tests/contract/, tests/integration/, tests/unit/, database/migrations/, database/seeds/, static/images/, static/styles/)
- [ ] T002 [P] Create requirements.txt with dependencies (streamlit>=1.30.0, sqlalchemy>=2.0.0, psycopg2-binary>=2.9.0, python-dotenv>=1.0.0, alembic>=1.13.0, pytest>=7.0.0, pillow>=10.0.0)
- [ ] T003 [P] Create .env.example template with DATABASE_URL, APP_ENV, LOG_LEVEL, STREAMLIT_SERVER_PORT
- [ ] T004 [P] Create .gitignore with .env, venv/, __pycache__/, *.pyc, .pytest_cache/, htmlcov/
- [ ] T005 [P] Create README.md with project overview and quickstart link
- [ ] T006 [P] Configure pytest.ini for test discovery and coverage settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Implement database connection pool in src/utils/database.py with SQLAlchemy engine, session factory, connection string from env
- [ ] T008 [P] Implement structured JSON logger in src/utils/logger.py with child-friendly error wrapper (Constitution V)
- [ ] T009 [P] Implement environment config loader in src/utils/config.py using python-dotenv
- [ ] T010 Initialize Alembic migrations in database/migrations/ with env.py configured for Neon PostgreSQL
- [ ] T011 Create SQLAlchemy ORM models in src/lib/curriculum.py (Chapter, Lesson, Video classes with relationships, constraints per data-model.md)
- [ ] T012 Create initial database migration in database/migrations/versions/001_initial_schema.py based on contracts/database-schema.sql
- [ ] T013 Create seed data script in database/seeds/grade1_science.sql with 4 chapters, 5+ sample lessons, 3+ placeholder videos
- [ ] T014 [P] Create placeholder images in static/images/placeholders/ (chapter-placeholder.png, lesson-placeholder.png with appropriate dimensions)
- [ ] T015 [P] Create child-friendly CSS in static/styles/child_friendly.css with bright colors, large fonts (18-24pt body, 28-36pt headings), 48x48px touch targets
- [ ] T016 Implement base content loader in src/lib/content_loader.py with database session management and error handling
- [ ] T017 Create main Streamlit app entry point in src/app.py with multi-page configuration, session state initialization, error boundaries

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Browse Science Chapters (Priority: P1) 🎯 MVP

**Goal**: Display four chapter cards (Living/Non-Living, Plants, Animals, Food) on home screen. User can click any card to navigate to that chapter's lesson list.

**Independent Test**: Launch app, verify 4 chapter cards display with correct titles and images, click "Plants" card, verify navigation to Plants lesson list page.

### Tests for User Story 1 (TDD for database operations per Constitution III)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US1] Contract test for get_all_chapters() query in tests/contract/test_chapter_queries.py (verify returns 4 chapters ordered by chapter_number, <50ms performance target)
- [ ] T019 [P] [US1] Integration test for chapter browsing in tests/integration/test_chapter_navigation.py (simulate user clicking chapter card, verify session state updates, navigation occurs)

### Implementation for User Story 1

- [ ] T020 [US1] Implement get_all_chapters() function in src/lib/content_loader.py with SQLAlchemy query, Streamlit caching (@st.cache_data, ttl=300), error handling with child-friendly fallback
- [ ] T021 [US1] Create ChapterCard component in src/components/chapter_card.py accepting chapter object, displaying image, title, with click handler
- [ ] T022 [US1] Create Chapters page in src/pages/1_Chapters.py (home screen) displaying 4 chapter cards in st.columns([1,1,1,1]) grid, handling click navigation via session state
- [ ] T023 [US1] Add logging for chapter display and navigation events in src/pages/1_Chapters.py (Constitution V: observability)

**Checkpoint**: At this point, User Story 1 should be fully functional - app displays chapters and allows navigation

---

## Phase 4: User Story 2 - View Lesson Content (Priority: P2)

**Goal**: Display list of lessons for selected chapter. User can click lesson to view full content (heading, 2-4 line explanation, illustration, daily life examples). Navigation includes "Next Lesson" and "Back" buttons.

**Independent Test**: From Chapters page, click "Living and Non-Living Things", verify lesson list displays, click "What is Living?" lesson, verify lesson content shows heading, text, image, examples, "Next Lesson" and "Back" buttons work.

### Tests for User Story 2 (TDD for database operations per Constitution III)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T024 [P] [US2] Contract test for get_lessons_by_chapter() query in tests/contract/test_lesson_queries.py (verify returns lessons for chapter_id ordered by lesson_number, <100ms performance target)
- [ ] T025 [P] [US2] Contract test for get_lesson_with_details() query in tests/contract/test_lesson_queries.py (verify returns lesson with all fields, <150ms performance target)
- [ ] T026 [P] [US2] Contract test for get_next_lesson() query in tests/contract/test_lesson_queries.py (verify returns correct next lesson in sequence or None if last)
- [ ] T027 [P] [US2] Integration test for lesson viewing in tests/integration/test_lesson_viewing.py (simulate full user journey: select chapter → select lesson → view content → next lesson → back)

### Implementation for User Story 2

- [ ] T028 [P] [US2] Implement get_lessons_by_chapter() function in src/lib/content_loader.py with SQLAlchemy query, caching, error handling
- [ ] T029 [P] [US2] Implement get_lesson_with_details() function in src/lib/content_loader.py with eager loading of relationships, caching
- [ ] T030 [P] [US2] Implement get_next_lesson() function in src/lib/content_loader.py for sequential navigation within chapter
- [ ] T031 [US2] Create LessonCard component in src/components/lesson_card.py displaying lesson title, thumbnail, with click handler
- [ ] T032 [US2] Create LessonViewer component in src/components/lesson_viewer.py displaying heading, content, image, daily_life_examples with proper formatting (depends on T029, T030)
- [ ] T033 [US2] Create Lessons page in src/pages/2_Lessons.py displaying lesson cards for selected chapter, handling chapter_id from session state, back to chapters navigation
- [ ] T034 [US2] Create Lesson_View page in src/pages/3_Lesson_View.py rendering LessonViewer component, "Next Lesson" and "Back" buttons with navigation logic (depends on T032)
- [ ] T035 [US2] Add validation for content length (<=500 chars) and examples array (1-2 items) in lesson display logic in src/components/lesson_viewer.py
- [ ] T036 [US2] Add logging for lesson views, navigation events in src/pages/2_Lessons.py and src/pages/3_Lesson_View.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - full chapter and lesson browsing functional

---

## Phase 5: User Story 3 - Watch Educational Videos (Priority: P3)

**Goal**: Display 1-2 YouTube video thumbnails below lesson content. Videos embed within app (no external navigation) with child-safety parameters enabled. Fallback message if video unavailable.

**Independent Test**: View any lesson with videos, verify video thumbnails appear below text, click play, verify video embeds and plays in-app with restricted mode, verify related videos hidden, test with invalid video ID and verify fallback message appears.

### Tests for User Story 3 (TDD for database operations per Constitution III)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T037 [P] [US3] Contract test for get_videos_by_lesson() query in tests/contract/test_video_queries.py (verify returns videos for lesson_id ordered by display_order, only active videos, <50ms performance target)
- [ ] T038 [P] [US3] Unit test for generate_safe_youtube_embed_url() in tests/unit/test_youtube_embedder.py (verify URL format, safety parameters present: rel=0, modestbranding=1, disablekb=1, fs=0, iv_load_policy=3)
- [ ] T039 [P] [US3] Integration test for video playback in tests/integration/test_video_viewing.py (simulate video load, verify embed iframe present, verify fallback on invalid video)

### Implementation for User Story 3

- [ ] T040 [P] [US3] Implement get_videos_by_lesson() function in src/lib/content_loader.py with SQLAlchemy query filtering is_active=True, ordered by display_order, caching
- [ ] T041 [US3] Implement generate_safe_youtube_embed_url() function in src/lib/youtube_embedder.py generating youtube-nocookie.com URLs with safety parameters (rel=0&modestbranding=1&disablekb=1&fs=0&iv_load_policy=3) per research.md
- [ ] T042 [US3] Create VideoPlayer component in src/components/video_player.py using st.components.v1.iframe() for YouTube embed with error handling, fallback message: "Video is resting now! Let's read the lesson together." (spec FR-016)
- [ ] T043 [US3] Update LessonViewer component in src/components/lesson_viewer.py to display videos below content using VideoPlayer component, handling 1-2 videos per lesson (depends on T040, T041, T042)
- [ ] T044 [US3] Add video load logging and error tracking in src/components/video_player.py (Constitution V: observability)
- [ ] T045 [US3] Test video embedding with real YouTube IDs, verify safety parameters work (no related videos, no comments, restricted mode)

**Checkpoint**: All three user stories should now be independently functional - complete curriculum browsing with videos

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, performance optimization, documentation

- [ ] T046 [P] Add custom Streamlit theme configuration in .streamlit/config.toml with child-friendly colors from research.md (sky blue #87CEEB, grass green #90EE90, sunshine yellow #FFD700)
- [ ] T047 [P] Implement image lazy loading optimization in src/components/chapter_card.py and src/components/lesson_viewer.py for <1 second load time (Constitution IX)
- [ ] T048 [P] Add loading spinners and skeleton screens in src/pages/ files for better UX during data fetching
- [ ] T049 [P] Implement graceful degradation for missing images in all components - display placeholder with alt text (Constitution VIII, spec edge case)
- [ ] T050 [P] Add database connection retry logic with exponential backoff in src/utils/database.py (Constitution VIII: graceful degradation)
- [ ] T051 [P] Create performance monitoring logging for query times in src/lib/content_loader.py (target: <150ms per research.md)
- [ ] T052 [P] Add unit tests for utility functions in tests/unit/test_logger.py, tests/unit/test_config.py, tests/unit/test_database.py
- [ ] T053 Run quickstart.md validation end-to-end (setup venv, install dependencies, run migrations, seed data, launch app, verify all user stories work)
- [ ] T054 [P] Update README.md with architecture diagram, links to specs/001-curriculum-browser/spec.md and quickstart.md
- [ ] T055 [P] Create developer documentation in docs/architecture.md explaining library-driven structure (Constitution IV)
- [ ] T056 Performance testing: measure page load times with Chrome DevTools, verify <2 second target (Constitution IX, spec SC-002)
- [ ] T057 Accessibility review: test with keyboard navigation, verify touch targets >=48px, contrast ratios >=4.5:1 per research.md
- [ ] T058 Code cleanup: remove TODOs, unused imports, add docstrings to public functions in src/lib/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T006) completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (T007-T017) completion - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational (T007-T017) completion - Can integrate with US1 navigation but independently testable
- **User Story 3 (Phase 5)**: Depends on Foundational (T007-T017) completion AND User Story 2 (T024-T036) completion (extends LessonViewer)
- **Polish (Phase 6)**: Depends on all desired user stories (T018-T045) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start immediately after Foundational phase - No dependencies on other stories
- **User Story 2 (P2)**: Can start immediately after Foundational phase - Builds on US1 navigation pattern but independently testable
- **User Story 3 (P3)**: Requires User Story 2 (T032 LessonViewer component) to be complete - Extends existing lesson viewing

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD per Constitution III)
- Database query functions before UI components (content_loader.py before components/)
- Components before pages (components/ used by pages/)
- Core implementation (query + component) before logging/monitoring
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (can run in parallel)**:
- T002, T003, T004, T005, T006 (different files, no dependencies)

**Foundational Phase (can run in parallel within phase)**:
- T008, T009 (utilities: logger, config - different files)
- T014, T015 (static assets: images, CSS - different files)

**User Story 1 Tests (can run in parallel)**:
- T018, T019 (contract and integration tests - different files)

**User Story 1 Implementation**:
- T020 must complete before T021, T022 (content_loader used by components/pages)
- T021, T023 can run in parallel (different files)

**User Story 2 Tests (can run in parallel)**:
- T024, T025, T026, T027 (all test files - different files)

**User Story 2 Implementation**:
- T028, T029, T030 can run in parallel (all in content_loader.py but different functions)
- T031 can run in parallel with T028-T030 (different file)
- T032 depends on T029, T030 (uses those functions)
- T033, T034 depend on T032 (use LessonViewer component)
- T035, T036 can run in parallel (validation and logging - different concerns)

**User Story 3 Tests (can run in parallel)**:
- T037, T038, T039 (all test files - different files)

**User Story 3 Implementation**:
- T040, T041 can run in parallel (different files: content_loader.py vs youtube_embedder.py)
- T042 depends on T041 (uses youtube_embedder)
- T043 depends on T040, T041, T042 (integrates all)

**Polish Phase (many can run in parallel)**:
- T046, T047, T048, T049, T050, T051, T052, T054, T055 (different files/concerns)
- T053, T056, T057, T058 are validation tasks (run after implementation)

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together (TDD - write these first):
Task T024: "Contract test for get_lessons_by_chapter() in tests/contract/test_lesson_queries.py"
Task T025: "Contract test for get_lesson_with_details() in tests/contract/test_lesson_queries.py"
Task T026: "Contract test for get_next_lesson() in tests/contract/test_lesson_queries.py"
Task T027: "Integration test for lesson viewing in tests/integration/test_lesson_viewing.py"

# After tests fail, launch query functions in parallel:
Task T028: "Implement get_lessons_by_chapter() in src/lib/content_loader.py"
Task T029: "Implement get_lesson_with_details() in src/lib/content_loader.py"
Task T030: "Implement get_next_lesson() in src/lib/content_loader.py"
Task T031: "Create LessonCard component in src/components/lesson_card.py"

# Then implement pages sequentially (depend on components):
Task T032: "Create LessonViewer component (depends on T029, T030)"
Task T033: "Create Lessons page (uses LessonCard)"
Task T034: "Create Lesson_View page (uses LessonViewer)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T017) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T018-T023)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Launch app
   - Verify 4 chapter cards display
   - Click each card, verify navigation
   - Check performance: <2s page load
5. Deploy to staging/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational (T001-T017) → Foundation ready
2. Add User Story 1 (T018-T023) → Test independently → Deploy/Demo (MVP! Chapter browsing works)
3. Add User Story 2 (T024-T036) → Test independently → Deploy/Demo (Lesson viewing works)
4. Add User Story 3 (T037-T045) → Test independently → Deploy/Demo (Videos work)
5. Add Polish (T046-T058) → Final QA → Production release
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers after Foundational phase (T017) completes:

**Scenario: 2 Developers**
- Developer A: User Story 1 (T018-T023) + User Story 3 (T037-T045)
- Developer B: User Story 2 (T024-T036) + Polish (T046-T058)

**Scenario: 3 Developers**
- Developer A: User Story 1 (T018-T023)
- Developer B: User Story 2 (T024-T036)
- Developer C: User Story 3 (T037-T045) then Polish (T046-T058)

Note: User Story 3 depends on User Story 2 (T032 LessonViewer), so Developer C would start US3 after US2 T032 completes.

---

## Task Count Summary

- **Total Tasks**: 58
- **Setup Phase**: 6 tasks (T001-T006)
- **Foundational Phase**: 11 tasks (T007-T017) - BLOCKS all stories
- **User Story 1 (P1 MVP)**: 6 tasks (T018-T023) - 2 tests + 4 implementation
- **User Story 2 (P2)**: 13 tasks (T024-T036) - 4 tests + 9 implementation
- **User Story 3 (P3)**: 9 tasks (T037-T045) - 3 tests + 6 implementation
- **Polish Phase**: 13 tasks (T046-T058) - Cross-cutting improvements

**Parallel Opportunities**: 24 tasks marked [P] can run in parallel (41% of total)

**Test Coverage**: 9 test tasks (16% of total) - TDD for all database operations per Constitution III

**MVP Scope** (Minimum for first demo):
- Phase 1: Setup (T001-T006)
- Phase 2: Foundational (T007-T017)
- Phase 3: User Story 1 (T018-T023)
- **Total MVP Tasks**: 23 tasks (40% of total)

---

## Notes

- **[P] tasks** = different files, no dependencies - safe to parallelize
- **[US1], [US2], [US3] labels** = map task to specific user story for traceability
- **TDD Required**: Constitution III mandates tests for database operations (content_loader queries) - tests MUST fail before implementation
- **UI Tests Optional**: Integration tests included for completeness but not strictly required per Constitution III
- Each user story is independently testable - stop at any checkpoint to validate
- Commit after each task or logical group of [P] tasks
- **Performance Validation**: Run T056 after User Story 1 completes to verify <2s load time target early
- **Graceful Degradation**: Test T050 (connection retry) and T049 (missing images) against constitution requirements
- Avoid: vague tasks, same file conflicts, breaking user story independence

---

## Constitution Compliance Checklist

- ✅ **I. Child-Safety First**: Tasks include child-friendly error messages (T042, T044), Grade-1 CSS (T015), YouTube safety params (T041)
- ✅ **II. Discovery-First**: Tasks follow approved plan.md structure and data-model.md entities
- ✅ **III. TDD for Critical Paths**: Database query tests (T018-T019, T024-T027, T037-T039) written before implementation
- ✅ **IV. Library-Driven**: Business logic in src/lib/ (T016, T020, T028-T030, T040-T041), framework-agnostic
- ✅ **V. Observability**: Logging tasks (T008, T023, T036, T044, T051) with structured JSON format
- ✅ **VI. Database Migrations**: Alembic setup (T010), initial migration (T012), seed data (T013)
- ✅ **VII. AI Filtering**: N/A (no chatbot in this feature)
- ✅ **VIII. Graceful Degradation**: Retry logic (T050), placeholder images (T049), video fallback (T042)
- ✅ **IX. Performance Budgets**: Performance testing (T051, T056), lazy loading (T047), caching in queries (T020, T028-T029)
