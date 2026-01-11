"""
SQLAlchemy ORM models for Grade-1 Science curriculum.

Entities:
- Chapter: Main science topics (4 chapters)
- Lesson: Learning concepts within chapters (5-8 per chapter)
- Video: YouTube videos for lessons (1-2 per lesson)

Based on specs/001-curriculum-browser/data-model.md
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, CheckConstraint, Column, ForeignKey, Integer, String,
    Text, TIMESTAMP, UniqueConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Chapter(Base):
    """
    Represents one of the four main Grade-1 science topics.

    Attributes:
        id: UUID primary key
        title: Chapter name (e.g., "Living and Non-Living Things")
        chapter_number: Display order (1-4)
        description: Brief summary (optional)
        image_url: Illustration URL for chapter card
        created_at: Record creation timestamp
        updated_at: Last modification timestamp
        lessons: Related lessons (one-to-many)
    """
    __tablename__ = "chapters"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )
    chapter_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    image_url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson",
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="Lesson.lesson_number"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "chapter_number >= 1 AND chapter_number <= 4",
            name="ck_chapter_number_range"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Chapter("
            f"id={self.id}, "
            f"number={self.chapter_number}, "
            f"title='{self.title}'"
            f")>"
        )


class Lesson(Base):
    """
    Represents a single learning concept within a chapter.

    One concept per screen (Constitution I: child cognitive load management).

    Attributes:
        id: UUID primary key
        chapter_id: Foreign key to parent chapter
        title: Lesson title for card display
        lesson_number: Order within chapter (1, 2, 3...)
        heading: Simple heading displayed at top of lesson
        content: 2-4 line explanation (max 500 chars)
        image_url: Lesson illustration URL
        daily_life_examples: JSONB array of 1-2 example strings
        created_at: Record creation timestamp
        updated_at: Last modification timestamp
        chapter: Parent chapter relationship
        videos: Related videos (one-to-many)
    """
    __tablename__ = "lessons"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    chapter_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("chapters.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    lesson_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    heading: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    image_url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    daily_life_examples: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    chapter: Mapped["Chapter"] = relationship(
        "Chapter",
        back_populates="lessons"
    )
    videos: Mapped[List["Video"]] = relationship(
        "Video",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="Video.display_order"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "lesson_number >= 1",
            name="ck_lesson_number_positive"
        ),
        CheckConstraint(
            "LENGTH(content) <= 500",
            name="ck_content_length"
        ),
        UniqueConstraint(
            "chapter_id",
            "lesson_number",
            name="uq_chapter_lesson_number"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Lesson("
            f"id={self.id}, "
            f"chapter_id={self.chapter_id}, "
            f"number={self.lesson_number}, "
            f"title='{self.title}'"
            f")>"
        )


class Video(Base):
    """
    Represents an embedded YouTube video for a lesson.

    Videos are child-safe and educational (1-2 per lesson).

    Attributes:
        id: UUID primary key
        lesson_id: Foreign key to parent lesson
        title: Video title for accessibility
        youtube_video_id: YouTube video ID (11 chars, e.g., "dQw4w9WgXcQ")
        thumbnail_url: Custom thumbnail (optional)
        display_order: Order within lesson (1 or 2)
        duration_seconds: Video length (optional, for tracking)
        is_active: Soft deletion flag (False hides video)
        created_at: Record creation timestamp
        updated_at: Last modification timestamp
        lesson: Parent lesson relationship
    """
    __tablename__ = "videos"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    lesson_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lessons.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    youtube_video_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True
    )
    thumbnail_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    lesson: Mapped["Lesson"] = relationship(
        "Lesson",
        back_populates="videos"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "display_order >= 1 AND display_order <= 2",
            name="ck_video_order_range"
        ),
        UniqueConstraint(
            "lesson_id",
            "display_order",
            name="uq_lesson_video_order"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Video("
            f"id={self.id}, "
            f"lesson_id={self.lesson_id}, "
            f"youtube_id='{self.youtube_video_id}', "
            f"order={self.display_order}"
            f")>"
        )
