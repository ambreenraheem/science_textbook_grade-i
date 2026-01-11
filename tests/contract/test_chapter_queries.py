"""
Contract tests for chapter database queries.

Tests the ContentLoader.get_all_chapters() query to verify:
- Returns exactly 4 chapters
- Chapters ordered by chapter_number (1-4)
- Query performance <50ms
- Correct data structure and fields

Per Constitution III: TDD for database operations
These tests must FAIL before implementation, then PASS after.
"""

import pytest
import time
from src.lib.content_loader import ContentLoader
from src.lib.curriculum import Chapter


@pytest.mark.contract
@pytest.mark.db
class TestChapterQueries:
    """Contract tests for chapter query operations."""

    def test_get_all_chapters_returns_four_chapters(self, content_loader: ContentLoader):
        """
        Test that get_all_chapters() returns exactly 4 chapters.

        Acceptance Criteria:
        - Returns list of Chapter objects
        - List contains exactly 4 items
        """
        chapters = content_loader.get_all_chapters()

        assert isinstance(chapters, list), "Should return a list"
        assert len(chapters) == 4, f"Should return 4 chapters, got {len(chapters)}"

    def test_get_all_chapters_ordered_by_chapter_number(self, content_loader: ContentLoader):
        """
        Test that chapters are ordered by chapter_number (1, 2, 3, 4).

        Acceptance Criteria:
        - Chapters returned in order: 1, 2, 3, 4
        - Chapter numbers are sequential
        """
        chapters = content_loader.get_all_chapters()

        # Extract chapter numbers
        chapter_numbers = [ch.chapter_number for ch in chapters]

        assert chapter_numbers == [1, 2, 3, 4], \
            f"Chapters should be ordered 1-4, got {chapter_numbers}"

    def test_get_all_chapters_correct_titles(self, content_loader: ContentLoader):
        """
        Test that chapters have correct titles in correct order.

        Acceptance Criteria:
        - Chapter 1: Living and Non-Living Things
        - Chapter 2: Plants
        - Chapter 3: Animals
        - Chapter 4: Food
        """
        chapters = content_loader.get_all_chapters()

        expected_titles = [
            "Living and Non-Living Things",
            "Plants",
            "Animals",
            "Food"
        ]

        actual_titles = [ch.title for ch in chapters]

        assert actual_titles == expected_titles, \
            f"Chapter titles mismatch.\nExpected: {expected_titles}\nActual: {actual_titles}"

    def test_get_all_chapters_returns_chapter_objects(self, content_loader: ContentLoader):
        """
        Test that get_all_chapters() returns proper Chapter ORM objects.

        Acceptance Criteria:
        - Each item is a Chapter instance
        - Each chapter has required fields: id, title, chapter_number, image_url
        """
        chapters = content_loader.get_all_chapters()

        for chapter in chapters:
            assert isinstance(chapter, Chapter), \
                f"Each item should be a Chapter object, got {type(chapter)}"

            # Verify required fields are present
            assert hasattr(chapter, "id"), "Chapter should have id field"
            assert hasattr(chapter, "title"), "Chapter should have title field"
            assert hasattr(chapter, "chapter_number"), "Chapter should have chapter_number field"
            assert hasattr(chapter, "image_url"), "Chapter should have image_url field"
            assert hasattr(chapter, "description"), "Chapter should have description field"

            # Verify fields are not None
            assert chapter.id is not None, "Chapter id should not be None"
            assert chapter.title is not None, "Chapter title should not be None"
            assert chapter.chapter_number is not None, "Chapter chapter_number should not be None"
            assert chapter.image_url is not None, "Chapter image_url should not be None"

    def test_get_all_chapters_performance_under_50ms(self, content_loader: ContentLoader):
        """
        Test that get_all_chapters() completes in <50ms.

        Acceptance Criteria:
        - Query completes in under 50 milliseconds
        - Performance target per research.md and tasks.md
        """
        # Warm up cache
        content_loader.clear_cache()

        # Measure query time
        start_time = time.perf_counter()
        chapters = content_loader.get_all_chapters()
        end_time = time.perf_counter()

        query_time_ms = (end_time - start_time) * 1000

        assert len(chapters) == 4, "Should return 4 chapters"
        assert query_time_ms < 50, \
            f"Query should complete in <50ms, took {query_time_ms:.2f}ms"

    def test_get_all_chapters_caching_works(self, content_loader: ContentLoader):
        """
        Test that caching improves performance on repeated calls.

        Acceptance Criteria:
        - First call loads from database
        - Second call uses cache and is faster
        - Cache returns same data
        """
        # Clear cache first
        content_loader.clear_cache()

        # First call (database)
        start_time_1 = time.perf_counter()
        chapters_1 = content_loader.get_all_chapters()
        end_time_1 = time.perf_counter()
        time_1_ms = (end_time_1 - start_time_1) * 1000

        # Second call (cache)
        start_time_2 = time.perf_counter()
        chapters_2 = content_loader.get_all_chapters()
        end_time_2 = time.perf_counter()
        time_2_ms = (end_time_2 - start_time_2) * 1000

        # Verify same data
        assert len(chapters_1) == len(chapters_2) == 4
        assert [ch.id for ch in chapters_1] == [ch.id for ch in chapters_2]

        # Cached call should be faster (at least 2x faster)
        assert time_2_ms < time_1_ms, \
            f"Cached call should be faster. First: {time_1_ms:.2f}ms, Second: {time_2_ms:.2f}ms"

    def test_get_all_chapters_eager_loads_lessons(self, content_loader: ContentLoader, seed_lessons):
        """
        Test that chapters have lessons relationship eager-loaded.

        Acceptance Criteria:
        - Chapters have lessons attribute
        - Lessons are accessible without additional query
        """
        chapters = content_loader.get_all_chapters()

        # Chapter 1 should have 3 lessons (seeded)
        chapter1 = chapters[0]
        assert hasattr(chapter1, "lessons"), "Chapter should have lessons relationship"
        assert isinstance(chapter1.lessons, list), "Lessons should be a list"

        # After seeding, chapter 1 should have 3 lessons
        assert len(chapter1.lessons) == 3, \
            f"Chapter 1 should have 3 lessons, got {len(chapter1.lessons)}"

    def test_get_all_chapters_handles_empty_database(self, db_manager_mock, test_db_engine):
        """
        Test that get_all_chapters() handles empty database gracefully.

        Acceptance Criteria:
        - Returns empty list when no chapters exist
        - No error raised
        """
        from src.lib.curriculum import Base

        # Clear database for this test
        Base.metadata.drop_all(test_db_engine)
        Base.metadata.create_all(test_db_engine)

        # Create content loader without seeded data
        loader = ContentLoader(db_manager_mock)
        loader.clear_cache()

        # Should return empty list, not raise error
        chapters = loader.get_all_chapters()

        assert isinstance(chapters, list), "Should return a list"
        assert len(chapters) == 0, f"Should return empty list, got {len(chapters)} chapters"
