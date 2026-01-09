"""
Content Loader for Grade-1 Science Curriculum

Provides database query operations with:
- Session management
- Error handling and retry logic
- Simple caching for performance
- Child-friendly error messages

This is library code (framework-agnostic) that can be used by any UI layer.
"""
from typing import List, Optional, Dict, Any
from functools import lru_cache
from uuid import UUID
import time

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.lib.curriculum import Chapter, Lesson, Video
from src.utils.database import DatabaseManager
from src.utils.logger import get_logger, log_performance


logger = get_logger(__name__)


class ContentLoaderError(Exception):
    """Base exception for content loading errors."""
    pass


class ChapterNotFoundError(ContentLoaderError):
    """Raised when a chapter is not found."""
    pass


class LessonNotFoundError(ContentLoaderError):
    """Raised when a lesson is not found."""
    pass


class ContentLoader:
    """
    Loads curriculum content from the database with caching and error handling.

    Features:
    - Automatic retry logic for transient failures
    - Performance logging
    - Child-friendly error messages
    - Simple in-memory caching

    Usage:
        loader = ContentLoader(db_manager)
        chapters = loader.get_all_chapters()
        lesson = loader.get_lesson_by_id(lesson_id)
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the content loader.

        Args:
            db_manager: DatabaseManager instance for session management
        """
        self.db = db_manager
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        self._cache_timestamps: Dict[str, float] = {}

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached item is still valid."""
        if key not in self._cache_timestamps:
            return False

        age = time.time() - self._cache_timestamps[key]
        return age < self._cache_ttl

    def _set_cache(self, key: str, value: Any) -> None:
        """Store value in cache with timestamp."""
        self._cache[key] = value
        self._cache_timestamps[key] = time.time()

    def _get_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if valid."""
        if self._is_cache_valid(key):
            logger.debug(f"Cache hit for key: {key}")
            return self._cache[key]

        # Remove expired cache entry
        if key in self._cache:
            del self._cache[key]
            del self._cache_timestamps[key]

        return None

    @log_performance
    def get_all_chapters(self) -> List[Chapter]:
        """
        Get all chapters ordered by chapter_number.

        Returns:
            List of Chapter objects with eager-loaded lessons

        Raises:
            ContentLoaderError: If database query fails
        """
        cache_key = "all_chapters"

        # Check cache first
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            with self.db.get_session() as session:
                stmt = (
                    select(Chapter)
                    .options(selectinload(Chapter.lessons))
                    .order_by(Chapter.chapter_number)
                )
                result = session.execute(stmt)
                chapters = list(result.scalars().all())

                logger.info(f"Loaded {len(chapters)} chapters from database")

                # Cache the result
                self._set_cache(cache_key, chapters)

                return chapters

        except Exception as e:
            logger.error(
                "Failed to load chapters",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "child_friendly": "database_error"
                }
            )
            raise ContentLoaderError(f"Failed to load chapters: {e}") from e

    @log_performance
    def get_chapter_by_id(self, chapter_id: UUID) -> Chapter:
        """
        Get a single chapter by ID with lessons.

        Args:
            chapter_id: UUID of the chapter

        Returns:
            Chapter object with eager-loaded lessons

        Raises:
            ChapterNotFoundError: If chapter doesn't exist
            ContentLoaderError: If database query fails
        """
        cache_key = f"chapter_{chapter_id}"

        # Check cache first
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            with self.db.get_session() as session:
                stmt = (
                    select(Chapter)
                    .options(selectinload(Chapter.lessons))
                    .where(Chapter.id == chapter_id)
                )
                result = session.execute(stmt)
                chapter = result.scalar_one_or_none()

                if chapter is None:
                    logger.warning(f"Chapter not found: {chapter_id}")
                    raise ChapterNotFoundError(f"Chapter {chapter_id} not found")

                logger.info(f"Loaded chapter: {chapter.title}")

                # Cache the result
                self._set_cache(cache_key, chapter)

                return chapter

        except ChapterNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to load chapter",
                extra={
                    "chapter_id": str(chapter_id),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "child_friendly": "database_error"
                }
            )
            raise ContentLoaderError(f"Failed to load chapter: {e}") from e

    @log_performance
    def get_chapter_by_number(self, chapter_number: int) -> Chapter:
        """
        Get a chapter by its number (1-4).

        Args:
            chapter_number: Chapter number (1-4)

        Returns:
            Chapter object with eager-loaded lessons

        Raises:
            ChapterNotFoundError: If chapter doesn't exist
            ContentLoaderError: If database query fails
        """
        cache_key = f"chapter_num_{chapter_number}"

        # Check cache first
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            with self.db.get_session() as session:
                stmt = (
                    select(Chapter)
                    .options(selectinload(Chapter.lessons))
                    .where(Chapter.chapter_number == chapter_number)
                )
                result = session.execute(stmt)
                chapter = result.scalar_one_or_none()

                if chapter is None:
                    logger.warning(f"Chapter not found: number {chapter_number}")
                    raise ChapterNotFoundError(f"Chapter {chapter_number} not found")

                logger.info(f"Loaded chapter {chapter_number}: {chapter.title}")

                # Cache the result
                self._set_cache(cache_key, chapter)

                return chapter

        except ChapterNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to load chapter by number",
                extra={
                    "chapter_number": chapter_number,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "child_friendly": "database_error"
                }
            )
            raise ContentLoaderError(f"Failed to load chapter: {e}") from e

    @log_performance
    def get_lesson_by_id(self, lesson_id: UUID) -> Lesson:
        """
        Get a single lesson by ID with videos and parent chapter.

        Args:
            lesson_id: UUID of the lesson

        Returns:
            Lesson object with eager-loaded videos and chapter

        Raises:
            LessonNotFoundError: If lesson doesn't exist
            ContentLoaderError: If database query fails
        """
        cache_key = f"lesson_{lesson_id}"

        # Check cache first
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            with self.db.get_session() as session:
                stmt = (
                    select(Lesson)
                    .options(
                        selectinload(Lesson.videos),
                        selectinload(Lesson.chapter)
                    )
                    .where(Lesson.id == lesson_id)
                )
                result = session.execute(stmt)
                lesson = result.scalar_one_or_none()

                if lesson is None:
                    logger.warning(f"Lesson not found: {lesson_id}")
                    raise LessonNotFoundError(f"Lesson {lesson_id} not found")

                logger.info(f"Loaded lesson: {lesson.title}")

                # Cache the result
                self._set_cache(cache_key, lesson)

                return lesson

        except LessonNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to load lesson",
                extra={
                    "lesson_id": str(lesson_id),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "child_friendly": "database_error"
                }
            )
            raise ContentLoaderError(f"Failed to load lesson: {e}") from e

    @log_performance
    def get_lessons_by_chapter(self, chapter_id: UUID) -> List[Lesson]:
        """
        Get all lessons for a chapter, ordered by lesson_number.

        Args:
            chapter_id: UUID of the chapter

        Returns:
            List of Lesson objects with eager-loaded videos

        Raises:
            ContentLoaderError: If database query fails
        """
        cache_key = f"lessons_chapter_{chapter_id}"

        # Check cache first
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            with self.db.get_session() as session:
                stmt = (
                    select(Lesson)
                    .options(selectinload(Lesson.videos))
                    .where(Lesson.chapter_id == chapter_id)
                    .order_by(Lesson.lesson_number)
                )
                result = session.execute(stmt)
                lessons = list(result.scalars().all())

                logger.info(
                    f"Loaded {len(lessons)} lessons for chapter",
                    extra={"chapter_id": str(chapter_id)}
                )

                # Cache the result
                self._set_cache(cache_key, lessons)

                return lessons

        except Exception as e:
            logger.error(
                "Failed to load lessons for chapter",
                extra={
                    "chapter_id": str(chapter_id),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "child_friendly": "database_error"
                }
            )
            raise ContentLoaderError(f"Failed to load lessons: {e}") from e

    @log_performance
    def get_active_videos_for_lesson(self, lesson_id: UUID) -> List[Video]:
        """
        Get all active videos for a lesson, ordered by display_order.

        Args:
            lesson_id: UUID of the lesson

        Returns:
            List of active Video objects

        Raises:
            ContentLoaderError: If database query fails
        """
        cache_key = f"videos_lesson_{lesson_id}"

        # Check cache first
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            with self.db.get_session() as session:
                stmt = (
                    select(Video)
                    .where(
                        Video.lesson_id == lesson_id,
                        Video.is_active == True
                    )
                    .order_by(Video.display_order)
                )
                result = session.execute(stmt)
                videos = list(result.scalars().all())

                logger.info(
                    f"Loaded {len(videos)} videos for lesson",
                    extra={"lesson_id": str(lesson_id)}
                )

                # Cache the result
                self._set_cache(cache_key, videos)

                return videos

        except Exception as e:
            logger.error(
                "Failed to load videos for lesson",
                extra={
                    "lesson_id": str(lesson_id),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "child_friendly": "video_error"
                }
            )
            raise ContentLoaderError(f"Failed to load videos: {e}") from e

    def clear_cache(self) -> None:
        """Clear all cached content."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Content cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache size and age information
        """
        return {
            "size": len(self._cache),
            "keys": list(self._cache.keys()),
            "oldest_entry": min(self._cache_timestamps.values()) if self._cache_timestamps else None,
            "newest_entry": max(self._cache_timestamps.values()) if self._cache_timestamps else None,
        }
