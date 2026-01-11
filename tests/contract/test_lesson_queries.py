"""
Contract tests for lesson database queries.

Tests the ContentLoader lesson query methods:
- get_lessons_by_chapter(): Get all lessons for a chapter
- get_lesson_with_details(): Get single lesson with full details
- get_next_lesson(): Get next lesson in sequence

Per Constitution III: TDD for database operations
These tests must FAIL before implementation, then PASS after.
"""

import pytest
import time
from uuid import UUID
from src.lib.content_loader import ContentLoader
from src.lib.curriculum import Chapter, Lesson


@pytest.mark.contract
@pytest.mark.db
class TestLessonQueries:
    """Contract tests for lesson query operations."""

    # =========================================================================
    # Tests for get_lessons_by_chapter()
    # =========================================================================

    def test_get_lessons_by_chapter_returns_lessons_for_chapter(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that get_lessons_by_chapter() returns lessons for specified chapter.

        Acceptance Criteria:
        - Returns list of Lesson objects
        - All lessons belong to the specified chapter
        - Lessons are ordered by lesson_number
        """
        # Get chapter 1 (Living and Non-Living Things) which has 3 lessons
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)

        # Get lessons for chapter 1
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        assert isinstance(lessons, list), "Should return a list"
        assert len(lessons) == 3, f"Chapter 1 should have 3 lessons, got {len(lessons)}"

        # Verify all lessons belong to chapter 1
        for lesson in lessons:
            assert isinstance(lesson, Lesson), f"Each item should be a Lesson, got {type(lesson)}"
            assert lesson.chapter_id == chapter1.id, \
                f"Lesson should belong to chapter {chapter1.id}, got {lesson.chapter_id}"

    def test_get_lessons_by_chapter_ordered_by_lesson_number(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that lessons are ordered by lesson_number (1, 2, 3, ...).

        Acceptance Criteria:
        - Lessons returned in order by lesson_number
        - Lesson numbers are sequential starting from 1
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)

        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        # Extract lesson numbers
        lesson_numbers = [lesson.lesson_number for lesson in lessons]

        assert lesson_numbers == [1, 2, 3], \
            f"Lessons should be ordered 1, 2, 3, got {lesson_numbers}"

    def test_get_lessons_by_chapter_correct_titles(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that lessons have correct titles in correct order.

        Acceptance Criteria:
        - Lesson 1: "What is Living?"
        - Lesson 2: "What is Non-Living?"
        - Lesson 3: "How Are They Different?"
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)

        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        expected_titles = [
            "What is Living?",
            "What is Non-Living?",
            "How Are They Different?"
        ]

        actual_titles = [lesson.title for lesson in lessons]

        assert actual_titles == expected_titles, \
            f"Lesson titles mismatch.\nExpected: {expected_titles}\nActual: {actual_titles}"

    def test_get_lessons_by_chapter_performance_under_100ms(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that get_lessons_by_chapter() completes in <100ms.

        Acceptance Criteria:
        - Query completes in under 100 milliseconds
        - Performance target per tasks.md
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)

        # Clear cache
        content_loader.clear_cache()

        # Measure query time
        start_time = time.perf_counter()
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)
        end_time = time.perf_counter()

        query_time_ms = (end_time - start_time) * 1000

        assert len(lessons) == 3, "Should return 3 lessons"
        assert query_time_ms < 100, \
            f"Query should complete in <100ms, took {query_time_ms:.2f}ms"

    def test_get_lessons_by_chapter_eager_loads_videos(
        self, content_loader: ContentLoader, seed_lessons, seed_videos
    ):
        """
        Test that lessons have videos relationship eager-loaded.

        Acceptance Criteria:
        - Lessons have videos attribute
        - Videos are accessible without additional query
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)

        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        # First lesson should have 2 videos (seeded)
        lesson1 = lessons[0]
        assert hasattr(lesson1, "videos"), "Lesson should have videos relationship"
        assert isinstance(lesson1.videos, list), "Videos should be a list"
        assert len(lesson1.videos) == 2, \
            f"Lesson 1 should have 2 videos, got {len(lesson1.videos)}"

    def test_get_lessons_by_chapter_handles_empty_chapter(
        self, content_loader: ContentLoader
    ):
        """
        Test that get_lessons_by_chapter() handles chapter with no lessons.

        Acceptance Criteria:
        - Returns empty list when chapter has no lessons
        - No error raised
        """
        # Get chapter 2 (Plants) which has lessons
        chapters = content_loader.get_all_chapters()
        chapter2 = next(ch for ch in chapters if ch.chapter_number == 2)

        # This chapter has no lessons seeded in our test data
        lessons = content_loader.get_lessons_by_chapter(chapter2.id)

        assert isinstance(lessons, list), "Should return a list"
        assert len(lessons) == 0, f"Chapter should have no lessons, got {len(lessons)}"

    # =========================================================================
    # Tests for get_lesson_with_details() (alias for get_lesson_by_id)
    # =========================================================================

    def test_get_lesson_with_details_returns_lesson(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that get_lesson_with_details() returns lesson with all fields.

        Acceptance Criteria:
        - Returns Lesson object
        - Has all required fields (title, heading, content, image_url, daily_life_examples)
        - Has relationships (chapter, videos)
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)
        lesson1_id = lessons[0].id

        # Get lesson with details (using get_lesson_by_id as alias)
        lesson = content_loader.get_lesson_by_id(lesson1_id)

        assert isinstance(lesson, Lesson), f"Should return Lesson, got {type(lesson)}"

        # Verify required fields
        assert lesson.title, "Lesson should have title"
        assert lesson.heading, "Lesson should have heading"
        assert lesson.content, "Lesson should have content"
        assert lesson.image_url, "Lesson should have image_url"
        assert isinstance(lesson.daily_life_examples, list), "Should have daily_life_examples list"
        assert len(lesson.daily_life_examples) >= 1, "Should have at least 1 example"

        # Verify relationships
        assert hasattr(lesson, "chapter"), "Should have chapter relationship"
        assert hasattr(lesson, "videos"), "Should have videos relationship"

    def test_get_lesson_with_details_performance_under_150ms(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that get_lesson_with_details() completes in <150ms.

        Acceptance Criteria:
        - Query completes in under 150 milliseconds
        - Performance target per tasks.md
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)
        lesson1_id = lessons[0].id

        # Clear cache
        content_loader.clear_cache()

        # Measure query time
        start_time = time.perf_counter()
        lesson = content_loader.get_lesson_by_id(lesson1_id)
        end_time = time.perf_counter()

        query_time_ms = (end_time - start_time) * 1000

        assert lesson.id == lesson1_id, "Should return correct lesson"
        assert query_time_ms < 150, \
            f"Query should complete in <150ms, took {query_time_ms:.2f}ms"

    def test_get_lesson_with_details_content_validation(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that lesson content meets validation requirements.

        Acceptance Criteria:
        - Content length <= 500 characters
        - daily_life_examples has 1-2 items
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        for lesson_ref in lessons:
            lesson = content_loader.get_lesson_by_id(lesson_ref.id)

            # Content length validation
            assert len(lesson.content) <= 500, \
                f"Lesson '{lesson.title}' content exceeds 500 chars: {len(lesson.content)}"

            # Examples validation
            assert len(lesson.daily_life_examples) in [1, 2], \
                f"Lesson '{lesson.title}' should have 1-2 examples, got {len(lesson.daily_life_examples)}"

    # =========================================================================
    # Tests for get_next_lesson()
    # =========================================================================

    def test_get_next_lesson_returns_next_in_sequence(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that get_next_lesson() returns the next lesson in sequence.

        Acceptance Criteria:
        - Given lesson 1, returns lesson 2
        - Given lesson 2, returns lesson 3
        - Next lesson is in same chapter
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        # Test lesson 1 -> lesson 2
        lesson1 = lessons[0]
        next_lesson = content_loader.get_next_lesson(lesson1.chapter_id, lesson1.lesson_number)

        assert next_lesson is not None, "Should return next lesson"
        assert next_lesson.lesson_number == 2, \
            f"Next lesson after 1 should be 2, got {next_lesson.lesson_number}"
        assert next_lesson.chapter_id == chapter1.id, "Should be in same chapter"

        # Test lesson 2 -> lesson 3
        lesson2 = lessons[1]
        next_lesson = content_loader.get_next_lesson(lesson2.chapter_id, lesson2.lesson_number)

        assert next_lesson is not None, "Should return next lesson"
        assert next_lesson.lesson_number == 3, \
            f"Next lesson after 2 should be 3, got {next_lesson.lesson_number}"

    def test_get_next_lesson_returns_none_for_last_lesson(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that get_next_lesson() returns None for the last lesson in chapter.

        Acceptance Criteria:
        - Given lesson 3 (last in chapter 1), returns None
        - No error raised
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        # Last lesson (lesson 3)
        last_lesson = lessons[-1]
        assert last_lesson.lesson_number == 3, "Should be lesson 3"

        next_lesson = content_loader.get_next_lesson(last_lesson.chapter_id, last_lesson.lesson_number)

        assert next_lesson is None, "Should return None for last lesson"

    def test_get_next_lesson_performance_under_100ms(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that get_next_lesson() completes in <100ms.

        Acceptance Criteria:
        - Query completes in under 100 milliseconds
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)
        lesson1 = lessons[0]

        # Clear cache
        content_loader.clear_cache()

        # Measure query time
        start_time = time.perf_counter()
        next_lesson = content_loader.get_next_lesson(lesson1.chapter_id, lesson1.lesson_number)
        end_time = time.perf_counter()

        query_time_ms = (end_time - start_time) * 1000

        assert next_lesson is not None, "Should return next lesson"
        assert query_time_ms < 100, \
            f"Query should complete in <100ms, took {query_time_ms:.2f}ms"
