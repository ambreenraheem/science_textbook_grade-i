# Implementation Plan: Science Curriculum Browser

**Branch**: `001-curriculum-browser` | **Date**: 2026-01-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-curriculum-browser/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create an interactive science curriculum browser for Grade-1 students (ages 6-7) that displays four science chapters (Living and Non-Living Things, Plants, Animals, Food) with lesson-based content. Each lesson presents one concept per screen with simple explanations (2-4 lines), colorful illustrations, daily life examples, and 1-2 embedded child-safe YouTube videos. The application must use Grade-1 appropriate vocabulary (Lexile 190L-530L), load pages within 2 seconds, and provide graceful fallbacks when content is unavailable.

**Technical Approach**: Python-based web application using Streamlit for rapid UI development, Neon (PostgreSQL) database for curriculum content storage, and embedded YouTube player with restricted mode. Library-driven architecture separates business logic (content retrieval, filtering) from presentation layer.

## Technical Context

**Language/Version**: Python 3.11+ (required for modern type hints and performance improvements)
**Primary Dependencies**:
- Streamlit 1.30+ (child-friendly UI framework with built-in components)
- psycopg2-binary 2.9+ or SQLAlchemy 2.0+ (Neon database connectivity)
- python-dotenv (environment variable management)
- Pillow (image processing for placeholders)

**Storage**: Neon database (PostgreSQL 15+, managed service with connection pooling)
**Testing**: pytest 7.0+ with pytest-asyncio for async operations
**Target Platform**: Web browser (Chrome, Firefox, Safari, Edge) on tablets/desktops (9+ inch screens)
**Project Type**: Web application (single Python app with Streamlit frontend + backend logic)
**Performance Goals**:
- Page load: <2 seconds (constitution requirement)
- Database queries: <500ms p95 latency (constitution requirement)
- Image loading: <1 second for lesson illustrations
- Support 30-100 concurrent users (classroom scale)

**Constraints**:
- Grade-1 vocabulary only (Lexile 190L-530L)
- No external navigation (YouTube must embed, not redirect)
- No PII collection (COPPA compliance)
- Content must gracefully degrade when DB/YouTube unavailable
- Bright but soft colors (child-friendly UX)

**Scale/Scope**:
- 4 chapters, estimated 20-30 lessons total (5-8 lessons per chapter)
- 40-60 YouTube videos (1-2 per lesson)
- Expected usage: 100-500 students across multiple classrooms
- Content updates: monthly additions of new lessons

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Applicable Principles

✅ **I. Child-Safety First (NON-NEGOTIABLE)**
- **Requirement**: Grade-1 vocabulary (Lexile 190L-530L), no external links, no PII collection
- **Compliance**: Spec FR-008 mandates vocabulary constraint; FR-014/FR-015 require embedded YouTube with disabled suggestions; no authentication in this feature (separate feature)
- **Status**: PASS - All child-safety requirements in spec

✅ **II. Discovery-First Development**
- **Requirement**: Complete spec → plan → tasks workflow before implementation
- **Compliance**: Currently in planning phase after spec completion
- **Status**: PASS - Following prescribed workflow

✅ **III. Test-Driven Development for Critical Paths**
- **Requirement**: TDD mandatory for database operations; optional for UI
- **Compliance**: Database queries (chapter/lesson retrieval) require TDD; Streamlit UI components optional
- **Status**: PASS - Will create contract tests for DB operations

✅ **IV. Python-First, Library-Driven Architecture**
- **Requirement**: Business logic in `src/lib/`, framework-agnostic
- **Compliance**: Plan includes `src/lib/curriculum.py`, `src/lib/content_loader.py` separate from Streamlit app
- **Status**: PASS - Library structure defined in Project Structure section

✅ **V. Observability & Child-Friendly Logging**
- **Requirement**: Dual-layer error messages (child-friendly + technical logs)
- **Compliance**: Spec FR-016 requires friendly fallback messages; will implement structured logging for debugging
- **Status**: PASS - Error handling specified in spec

⚠️ **VI. Database Schema Versioning & Migration Safety**
- **Requirement**: Versioned migrations with rollback plans
- **Compliance**: Will use Alembic for schema migrations (initial schema creation in Phase 1)
- **Status**: PASS - Migration strategy to be documented in data-model.md

N/A **VII. AI Content Filtering Pipeline**
- **Requirement**: OpenAI responses must be filtered
- **Compliance**: Not applicable - no AI chatbot in this feature (separate feature)
- **Status**: N/A

✅ **VIII. Offline Resilience & Graceful Degradation**
- **Requirement**: Graceful handling when external services fail
- **Compliance**: Spec edge cases define fallback messages for missing content, failed images, unavailable videos
- **Status**: PASS - Fallback behavior specified

✅ **IX. Performance Budgets for Child Engagement**
- **Requirement**: <2s page load, <500ms DB queries
- **Compliance**: Spec SC-002 mandates 2-second page load; Technical Context defines query performance goals
- **Status**: PASS - Performance budgets documented

### Gate Evaluation

**Result**: ✅ ALL GATES PASSED

**Summary**: All applicable constitution principles are satisfied by the feature specification and technical approach. No complexity violations detected. Ready to proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-curriculum-browser/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── database-schema.sql
├── checklists/
│   └── requirements.md  # Spec quality checklist (already created)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (Python + Streamlit)
src/
├── lib/                          # Framework-agnostic business logic (Constitution IV)
│   ├── __init__.py
│   ├── curriculum.py             # Chapter/Lesson domain models
│   ├── content_loader.py         # Database query logic
│   └── youtube_embedder.py       # YouTube embed URL generation with safety params
├── components/                   # Streamlit UI components
│   ├── __init__.py
│   ├── chapter_card.py           # Chapter selection cards
│   ├── lesson_card.py            # Lesson list cards
│   └── lesson_viewer.py          # Lesson content display
├── pages/                        # Streamlit page files
│   ├── 1_Chapters.py             # Chapter selection (home)
│   ├── 2_Lessons.py              # Lesson list for selected chapter
│   └── 3_Lesson_View.py          # Individual lesson viewer
├── utils/                        # Shared utilities
│   ├── __init__.py
│   ├── database.py               # Neon DB connection pooling
│   ├── logger.py                 # Structured logging (Constitution V)
│   └── config.py                 # Environment variable loading
└── app.py                        # Main Streamlit entry point

tests/
├── contract/                     # Database contract tests (TDD for DB operations)
│   ├── test_chapter_queries.py
│   └── test_lesson_queries.py
├── integration/                  # End-to-end user journey tests
│   ├── test_chapter_navigation.py
│   └── test_lesson_viewing.py
└── unit/                         # Library unit tests
    ├── test_curriculum_models.py
    └── test_youtube_embedder.py

database/
├── migrations/                   # Alembic migration files (Constitution VI)
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py
└── seeds/                        # Sample curriculum data for development
    └── grade1_science.sql

static/                           # Static assets
├── images/
│   ├── placeholders/             # Fallback images when content fails
│   └── icons/
└── styles/
    └── child_friendly.css        # Custom Streamlit styling (bright, soft colors)

.env.example                      # Environment variable template
requirements.txt                  # Python dependencies
README.md                         # Project setup instructions
```

**Structure Decision**:

Selected **Web Application (Python + Streamlit)** structure because:

1. **Streamlit Simplicity**: Feature requires rapid development of child-friendly UI with minimal boilerplate. Streamlit provides built-in components (cards, buttons, layouts) that map directly to spec requirements (chapter cards, lesson navigation).

2. **Library-Driven Compliance**: Business logic isolated in `src/lib/` (Constitution IV) enables:
   - Independent testing without Streamlit runtime
   - Future migration to FastAPI/mobile app if needed
   - CLI tools for content management (e.g., `python -m src.lib.curriculum list-chapters`)

3. **Single Codebase**: No separate frontend/backend needed for this feature. Streamlit handles both presentation and server-side logic in Python, reducing complexity while maintaining testability through library separation.

4. **Database-First**: `database/migrations/` directory supports Alembic for schema versioning (Constitution VI). Seeds provide sample data for development/testing without production DB dependency.

**File Organization Rationale**:
- `src/lib/`: Pure Python, no Streamlit imports (testable, reusable)
- `src/components/`: Streamlit-specific UI components (can import from lib/)
- `src/pages/`: Streamlit multi-page app structure (URL routing: /Chapters, /Lessons, /Lesson_View)
- `tests/contract/`: TDD for database queries (Constitution III)
- `database/migrations/`: Schema evolution without data loss (Constitution VI)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No complexity violations detected. All constitution principles satisfied by current design.
