# Data Model: Science Curriculum Browser

**Phase**: 1 (Design & Contracts)
**Date**: 2026-01-10
**Purpose**: Define database schema, domain models, and data relationships for curriculum content storage

## Entity-Relationship Overview

```
┌─────────────┐
│   Chapter   │
│             │
│ - id (PK)   │
│ - title     │◄──┐
│ - number    │   │
│ - image_url │   │ ONE-TO-MANY
│ - created_at│   │
└─────────────┘   │
                  │
                  │
              ┌───┴─────────┐
              │   Lesson    │
              │             │
              │ - id (PK)   │
              │ - chapter_id│ (FK)
              │ - title     │◄──┐
              │ - number    │   │
              │ - heading   │   │
              │ - content   │   │ ONE-TO-MANY
              │ - image_url │   │
              │ - examples  │   │ (JSONB array)
              │ - created_at│   │
              └─────────────┘   │
                                │
                                │
                            ┌───┴─────────┐
                            │    Video    │
                            │             │
                            │ - id (PK)   │
                            │ - lesson_id │ (FK)
                            │ - title     │
                            │ - youtube_id│
                            │ - thumbnail │
                            │ - order     │ (1 or 2)
                            │ - created_at│
                            └─────────────┘
```

---

## Entity Definitions

### Entity: `Chapter`

**Purpose**: Represents one of the four main Grade-1 science topics.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| `title` | VARCHAR(100) | NOT NULL, UNIQUE | Chapter name (e.g., "Living and Non-Living Things") |
| `chapter_number` | INTEGER | NOT NULL, UNIQUE, CHECK (1-4) | Display order (1-4 for four chapters) |
| `description` | TEXT | NULLABLE | Brief summary (not displayed in MVP, future use) |
| `image_url` | TEXT | NOT NULL | Illustration URL for chapter card |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification time |

**Indexes**:
- `idx_chapters_number` ON `chapter_number` (for ordered retrieval)

**Validation Rules**:
- `chapter_number` must be between 1 and 4 (CHECK constraint)
- `title` must be non-empty (NOT NULL)
- `image_url` must be valid URL (application-level validation)

**Sample Data**:
```sql
INSERT INTO chapters (title, chapter_number, image_url) VALUES
  ('Living and Non-Living Things', 1, 'https://example.com/images/living-nonliving.png'),
  ('Plants', 2, 'https://example.com/images/plants.png'),
  ('Animals', 3, 'https://example.com/images/animals.png'),
  ('Food', 4, 'https://example.com/images/food.png');
```

---

### Entity: `Lesson`

**Purpose**: Represents a single learning concept within a chapter (one concept per screen).

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| `chapter_id` | UUID | NOT NULL, FOREIGN KEY → chapters(id) | Parent chapter reference |
| `title` | VARCHAR(200) | NOT NULL | Lesson title for card display |
| `lesson_number` | INTEGER | NOT NULL, CHECK (>= 1) | Order within chapter (1, 2, 3...) |
| `heading` | VARCHAR(200) | NOT NULL | Simple heading displayed at top of lesson |
| `content` | TEXT | NOT NULL, CHECK (LENGTH <= 500) | 2-4 line explanation (max 500 chars ≈ 80 words) |
| `image_url` | TEXT | NOT NULL | Lesson illustration URL |
| `daily_life_examples` | JSONB | NOT NULL, DEFAULT '[]' | Array of 1-2 example strings |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification time |

**Indexes**:
- `idx_lessons_chapter_id` ON `chapter_id` (for chapter → lessons query)
- `idx_lessons_number` ON `(chapter_id, lesson_number)` (for ordered retrieval within chapter)

**Validation Rules**:
- `lesson_number` must be >= 1 (CHECK constraint)
- `content` max length: 500 characters (enforces 2-4 line constraint)
- `daily_life_examples` must be JSON array with 1-2 strings (application-level validation)
- `image_url` must be valid URL (application-level validation)

**Unique Constraint**:
- `UNIQUE (chapter_id, lesson_number)` (prevents duplicate lesson numbers within a chapter)

**Sample Data**:
```sql
INSERT INTO lessons (chapter_id, title, lesson_number, heading, content, image_url, daily_life_examples) VALUES
  (
    '...',  -- chapter_id for "Living and Non-Living Things"
    'What is Living?',
    1,
    'Living Things',
    'Living things can grow, eat, and move. Plants and animals are living. They need water and food.',
    'https://example.com/images/living-things.png',
    '["Your pet dog is living because it eats and plays.", "The tree in your yard grows bigger every year."]'::jsonb
  ),
  (
    '...',  -- chapter_id for "Living and Non-Living Things"
    'What is Non-Living?',
    2,
    'Non-Living Things',
    'Non-living things do not grow or eat. Rocks, toys, and chairs are non-living. They stay the same.',
    'https://example.com/images/nonliving-things.png',
    '["Your toy car does not need food or water.", "A rock does not grow bigger."]'::jsonb
  );
```

---

### Entity: `Video`

**Purpose**: Represents an embedded YouTube video for a lesson (1-2 videos per lesson).

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| `lesson_id` | UUID | NOT NULL, FOREIGN KEY → lessons(id) | Parent lesson reference |
| `title` | VARCHAR(200) | NOT NULL | Video title for accessibility |
| `youtube_video_id` | VARCHAR(20) | NOT NULL, UNIQUE | YouTube video ID (e.g., "dQw4w9WgXcQ") |
| `thumbnail_url` | TEXT | NULLABLE | Custom thumbnail (optional, YouTube provides default) |
| `display_order` | INTEGER | NOT NULL, CHECK (1-2) | Order within lesson (1 = first video, 2 = second) |
| `duration_seconds` | INTEGER | NULLABLE | Video length (for future "time spent" tracking) |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Flag to hide video without deletion |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification time |

**Indexes**:
- `idx_videos_lesson_id` ON `lesson_id` (for lesson → videos query)
- `idx_videos_order` ON `(lesson_id, display_order)` (for ordered retrieval within lesson)

**Validation Rules**:
- `display_order` must be 1 or 2 (CHECK constraint, max 2 videos per lesson)
- `youtube_video_id` must match YouTube ID format (11 characters, alphanumeric + underscore/hyphen)
- `is_active` = FALSE allows soft-deletion (video hidden but record preserved)

**Unique Constraint**:
- `UNIQUE (lesson_id, display_order)` (prevents duplicate orders within a lesson)
- `UNIQUE (youtube_video_id)` (prevents same video from being added multiple times)

**Sample Data**:
```sql
INSERT INTO videos (lesson_id, title, youtube_video_id, display_order) VALUES
  (
    '...',  -- lesson_id for "What is Living?"
    'Living vs Non-Living Things for Kids',
    'ABC123XYZ',
    1
  ),
  (
    '...',  -- lesson_id for "What is Living?"
    'Examples of Living Things',
    'DEF456UVW',
    2
  );
```

---

## SQLAlchemy ORM Models

**File**: `src/lib/curriculum.py`

```python
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, CheckConstraint, Column, ForeignKey, Integer, String,
    Text, TIMESTAMP, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="chapter", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("chapter_number >= 1 AND chapter_number <= 4", name="ck_chapter_number_range"),
    )

    def __repr__(self) -> str:
        return f"<Chapter(id={self.id}, number={self.chapter_number}, title='{self.title}')>"


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    chapter_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False)
    heading: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    daily_life_examples: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="lessons")
    videos: Mapped[List["Video"]] = relationship("Video", back_populates="lesson", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("lesson_number >= 1", name="ck_lesson_number_positive"),
        CheckConstraint("LENGTH(content) <= 500", name="ck_content_length"),
        UniqueConstraint("chapter_id", "lesson_number", name="uq_chapter_lesson_number"),
    )

    def __repr__(self) -> str:
        return f"<Lesson(id={self.id}, chapter_id={self.chapter_id}, number={self.lesson_number}, title='{self.title}')>"


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    lesson_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    youtube_video_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="videos")

    # Constraints
    __table_args__ = (
        CheckConstraint("display_order >= 1 AND display_order <= 2", name="ck_video_order_range"),
        UniqueConstraint("lesson_id", "display_order", name="uq_lesson_video_order"),
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, lesson_id={self.lesson_id}, youtube_id='{self.youtube_video_id}', order={self.display_order})>"
```

---

## Database Migration Strategy (Constitution VI)

**Tool**: Alembic 1.13+

**Initial Migration**: `database/migrations/versions/001_initial_schema.py`

**Migration Workflow**:
1. Create migration: `alembic revision --autogenerate -m "initial schema"`
2. Review generated SQL: `alembic upgrade head --sql`
3. Test on staging: `alembic upgrade head` (with staging DB connection)
4. Apply to production: `alembic upgrade head` (with production DB connection)
5. Rollback if needed: `alembic downgrade -1`

**Future Schema Changes**:
- Add columns: Create migration with `alembic revision -m "add column X"`
- Breaking changes: Use 3-phase approach (add new → migrate data → remove old)
- Test rollback: Always verify `downgrade()` function works

---

## Query Patterns

**Common Queries** (to be implemented in `src/lib/content_loader.py`):

### Q1: Get All Chapters (Ordered)
```python
def get_all_chapters(session) -> List[Chapter]:
    return session.query(Chapter).order_by(Chapter.chapter_number).all()
```

**Expected Performance**: <50ms (4 rows, indexed by `chapter_number`)

---

### Q2: Get Lessons for Chapter (Ordered)
```python
def get_lessons_by_chapter(session, chapter_id: UUID) -> List[Lesson]:
    return session.query(Lesson)\
        .filter(Lesson.chapter_id == chapter_id)\
        .order_by(Lesson.lesson_number)\
        .all()
```

**Expected Performance**: <100ms (5-8 rows per chapter, indexed by `chapter_id` and `lesson_number`)

---

### Q3: Get Lesson with Videos
```python
def get_lesson_with_videos(session, lesson_id: UUID) -> Optional[Lesson]:
    return session.query(Lesson)\
        .options(selectinload(Lesson.videos))\
        .filter(Lesson.id == lesson_id)\
        .first()
```

**Expected Performance**: <150ms (1 lesson + 1-2 videos, eager loading with JOIN)

---

### Q4: Get Next Lesson in Chapter
```python
def get_next_lesson(session, current_lesson: Lesson) -> Optional[Lesson]:
    return session.query(Lesson)\
        .filter(Lesson.chapter_id == current_lesson.chapter_id)\
        .filter(Lesson.lesson_number > current_lesson.lesson_number)\
        .order_by(Lesson.lesson_number)\
        .first()
```

**Expected Performance**: <100ms (indexed by `chapter_id` and `lesson_number`)

---

## Data Integrity Rules

1. **Referential Integrity**:
   - Deleting a chapter deletes all its lessons (CASCADE)
   - Deleting a lesson deletes all its videos (CASCADE)

2. **Ordering Integrity**:
   - Chapter numbers must be unique and sequential (1, 2, 3, 4)
   - Lesson numbers must be unique within a chapter (1, 2, 3, ...)
   - Video orders must be unique within a lesson (1, 2)

3. **Content Validation** (Application-Level):
   - Lesson content max 500 characters (≈ 2-4 lines)
   - Daily life examples array must have 1-2 strings
   - YouTube video IDs must match format: 11 characters, alphanumeric + `_-`

4. **Soft Deletion**:
   - Videos use `is_active` flag instead of hard deletion
   - Preserves historical data for analytics
   - Allows re-activation without data loss

---

## Next Steps

- Create `contracts/database-schema.sql` with full SQL DDL
- Create `database/seeds/grade1_science.sql` with sample data
- Create `quickstart.md` with setup instructions
- Implement query functions in `src/lib/content_loader.py`
