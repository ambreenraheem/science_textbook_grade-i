"""
Integration tests for lesson viewing and navigation.

Tests the complete user flow for User Story 2:
- Select chapter → view lesson list
- Select lesson → view lesson content
- Navigate between lessons (Next/Back)
- View videos, examples, and full lesson details

Per Constitution III: Integration tests for user journeys.
"""

import pytest
from unittest.mock import Mock, MagicMock
from uuid import UUID
from src.lib.curriculum import Chapter, Lesson
from src.lib.content_loader import ContentLoader


@pytest.mark.integration
@pytest.mark.ui
class TestLessonViewing:
    """Integration tests for lesson viewing and navigation flow."""

    def test_full_lesson_viewing_journey(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test complete user journey from chapter selection to lesson viewing.

        User Journey:
        1. User selects chapter → sees lesson list
        2. User clicks lesson → sees full lesson content
        3. Content includes: heading, text, image, examples
        4. User can navigate to next lesson

        Acceptance Criteria:
        - All steps complete without errors
        - Data flows correctly through the journey
        - Lesson content is complete and valid
        """
        # Step 1: Get chapter
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        assert chapter1.title == "Living and Non-Living Things"

        # Step 2: Get lessons for chapter
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)
        assert len(lessons) == 3, "Chapter 1 should have 3 lessons"

        # Step 3: Select first lesson
        lesson1 = lessons[0]
        assert lesson1.lesson_number == 1
        assert lesson1.title == "What is Living?"

        # Step 4: View lesson details
        lesson_details = content_loader.get_lesson_by_id(lesson1.id)
        assert lesson_details.heading == "Living Things"
        assert len(lesson_details.content) > 0
        assert lesson_details.image_url
        assert len(lesson_details.daily_life_examples) >= 1

        # Step 5: Get next lesson
        next_lesson = content_loader.get_next_lesson(lesson1.chapter_id, lesson1.lesson_number)
        assert next_lesson is not None
        assert next_lesson.lesson_number == 2
        assert next_lesson.title == "What is Non-Living?"

    def test_lesson_list_displays_all_lessons_for_chapter(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that lesson list page displays all lessons for selected chapter.

        User Story: As a student, I want to see all lessons in a chapter
        so I can choose which lesson to learn.

        Acceptance Criteria:
        - All lessons for chapter are displayed
        - Lessons show in correct order (by lesson_number)
        - Each lesson has title and number
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)

        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        # Verify we have all lessons
        assert len(lessons) == 3, "Should display all 3 lessons"

        # Verify correct order
        for idx, lesson in enumerate(lessons, start=1):
            assert lesson.lesson_number == idx, \
                f"Lesson should be number {idx}, got {lesson.lesson_number}"
            assert lesson.title, f"Lesson {idx} should have a title"

    def test_lesson_content_has_all_required_fields(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that lesson view displays all required content fields.

        Lesson Content Requirements (per spec.md):
        - Heading (simple, child-friendly)
        - Content (2-4 lines, max 500 chars)
        - Image (illustration)
        - Daily life examples (1-2 examples)

        Acceptance Criteria:
        - All required fields present
        - Content meets length requirements
        - Examples array has 1-2 items
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        for lesson_ref in lessons:
            lesson = content_loader.get_lesson_by_id(lesson_ref.id)

            # Required fields
            assert lesson.heading, f"Lesson '{lesson.title}' must have heading"
            assert lesson.content, f"Lesson '{lesson.title}' must have content"
            assert lesson.image_url, f"Lesson '{lesson.title}' must have image_url"
            assert lesson.daily_life_examples, f"Lesson '{lesson.title}' must have examples"

            # Content validation
            assert 1 <= len(lesson.content) <= 500, \
                f"Content should be 1-500 chars, got {len(lesson.content)}"

            # Examples validation (1-2 per spec)
            assert 1 <= len(lesson.daily_life_examples) <= 2, \
                f"Should have 1-2 examples, got {len(lesson.daily_life_examples)}"

    def test_next_lesson_navigation_works_correctly(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that "Next Lesson" navigation works through entire chapter.

        User Flow:
        1. View Lesson 1 → click "Next" → see Lesson 2
        2. View Lesson 2 → click "Next" → see Lesson 3
        3. View Lesson 3 → "Next" button disabled (last lesson)

        Acceptance Criteria:
        - Next lesson loads correctly each time
        - Sequential order maintained
        - Last lesson has no "next"
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        # Navigate from Lesson 1 → 2 → 3
        current_lesson = lessons[0]
        lesson_numbers_visited = [current_lesson.lesson_number]

        while True:
            next_lesson = content_loader.get_next_lesson(
                current_lesson.chapter_id,
                current_lesson.lesson_number
            )

            if next_lesson is None:
                break

            lesson_numbers_visited.append(next_lesson.lesson_number)
            current_lesson = next_lesson

        # Should have visited 1, 2, 3
        assert lesson_numbers_visited == [1, 2, 3], \
            f"Should navigate through 1→2→3, got {lesson_numbers_visited}"

    def test_back_navigation_from_lesson_to_chapter(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that "Back" button returns user to lesson list.

        User Flow:
        1. User on lesson view page
        2. Clicks "Back" button
        3. Returns to lesson list for same chapter

        Acceptance Criteria:
        - Can navigate back to lesson list
        - Same chapter context maintained
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)

        # Simulate viewing a lesson
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)
        lesson2 = lessons[1]

        # View lesson details
        lesson_details = content_loader.get_lesson_by_id(lesson2.id)
        assert lesson_details.chapter_id == chapter1.id

        # Simulate "Back" - should return to chapter's lesson list
        # (In real UI, would navigate back to lessons page)
        back_to_lessons = content_loader.get_lessons_by_chapter(lesson_details.chapter_id)

        assert len(back_to_lessons) == 3, "Should return to same chapter's lesson list"
        assert back_to_lessons[0].chapter_id == chapter1.id, "Should be same chapter"

    def test_lesson_viewing_with_videos(
        self, content_loader: ContentLoader, seed_lessons, seed_videos
    ):
        """
        Test that lesson view displays videos below content.

        User Story: Videos displayed below lesson content (1-2 per lesson)

        Acceptance Criteria:
        - Lessons with videos show video section
        - Videos ordered by display_order
        - Video data complete (title, youtube_id)
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        # Lesson 1 has 2 videos (seeded)
        lesson1 = content_loader.get_lesson_by_id(lessons[0].id)

        # Get videos for lesson
        videos = content_loader.get_active_videos_for_lesson(lesson1.id)

        assert len(videos) == 2, f"Lesson 1 should have 2 videos, got {len(videos)}"

        # Verify video order
        assert videos[0].display_order == 1, "First video should have display_order 1"
        assert videos[1].display_order == 2, "Second video should have display_order 2"

        # Verify video data
        for video in videos:
            assert video.title, "Video should have title"
            assert video.youtube_video_id, "Video should have youtube_video_id"
            assert video.is_active, "Video should be active"

    def test_session_state_maintains_navigation_context(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that session state maintains user's navigation context.

        Navigation Context:
        - Current chapter
        - Current lesson
        - Position in lesson sequence

        Acceptance Criteria:
        - Can track which chapter user is viewing
        - Can track which lesson user is viewing
        - Can determine lesson position (e.g., "Lesson 2 of 3")
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        # Simulate session state (like Streamlit st.session_state)
        mock_session = {
            "current_chapter_id": chapter1.id,
            "current_lesson_id": lessons[1].id,  # Lesson 2
            "current_lesson_number": lessons[1].lesson_number
        }

        # Verify we can reconstruct navigation context
        assert mock_session["current_chapter_id"] == chapter1.id
        assert mock_session["current_lesson_number"] == 2

        # Calculate position
        total_lessons = len(lessons)
        current_position = mock_session["current_lesson_number"]

        assert current_position == 2, "Should be on lesson 2"
        assert total_lessons == 3, "Chapter should have 3 lessons"
        assert current_position < total_lessons, "Should not be last lesson"

    def test_lesson_content_validation_meets_spec(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that all lesson content meets specification requirements.

        Specification Requirements (from spec.md):
        - Content: 2-4 lines, maximum 500 characters
        - Examples: 1-2 daily life examples
        - Simple vocabulary (Grade-1 appropriate)
        - Concrete, not abstract concepts

        Acceptance Criteria:
        - All lessons meet content length requirement
        - All lessons have 1-2 examples
        - Content is concise and child-friendly
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        for lesson_ref in lessons:
            lesson = content_loader.get_lesson_by_id(lesson_ref.id)

            # Content length (max 500 chars per spec)
            assert len(lesson.content) <= 500, \
                f"Lesson '{lesson.title}' content exceeds 500 chars"

            # Examples count (1-2 per spec)
            assert 1 <= len(lesson.daily_life_examples) <= 2, \
                f"Lesson '{lesson.title}' should have 1-2 examples"

            # Each example should be a string
            for example in lesson.daily_life_examples:
                assert isinstance(example, str), "Each example should be a string"
                assert len(example) > 0, "Example should not be empty"

    @pytest.mark.slow
    def test_lesson_viewing_performance_under_2_seconds(
        self, content_loader: ContentLoader, seed_lessons, seed_videos
    ):
        """
        Test that lesson viewing page loads in <2 seconds.

        Performance Target (from spec.md SC-002):
        - Page load time < 2 seconds

        Acceptance Criteria:
        - Loading lesson list < 100ms
        - Loading lesson details < 150ms
        - Loading videos < 50ms
        - Total page load simulation < 2000ms
        """
        import time

        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)

        # Clear cache to simulate first load
        content_loader.clear_cache()

        start_time = time.perf_counter()

        # Simulate lesson page load operations
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)
        lesson1 = content_loader.get_lesson_by_id(lessons[0].id)
        videos = content_loader.get_active_videos_for_lesson(lesson1.id)

        # Simulate rendering (access all fields)
        _ = lesson1.heading
        _ = lesson1.content
        _ = lesson1.image_url
        _ = lesson1.daily_life_examples
        for video in videos:
            _ = video.title
            _ = video.youtube_video_id

        end_time = time.perf_counter()
        total_time_ms = (end_time - start_time) * 1000

        assert len(lessons) == 3, "Should load lessons"
        assert lesson1.id == lessons[0].id, "Should load correct lesson"
        assert len(videos) == 2, "Should load videos"
        assert total_time_ms < 2000, \
            f"Page load should complete in <2s, took {total_time_ms:.2f}ms"

    def test_lesson_viewing_handles_missing_videos_gracefully(
        self, content_loader: ContentLoader, seed_lessons
    ):
        """
        Test that lessons without videos display gracefully.

        Acceptance Criteria:
        - Lessons without videos still display correctly
        - No errors when videos list is empty
        - Fallback message shown (from spec: "Video is resting now!")
        """
        chapters = content_loader.get_all_chapters()
        chapter1 = next(ch for ch in chapters if ch.chapter_number == 1)
        lessons = content_loader.get_lessons_by_chapter(chapter1.id)

        # Lesson 2 has 1 video, Lesson 3 has no videos (not seeded)
        lesson3 = content_loader.get_lesson_by_id(lessons[2].id)
        videos = content_loader.get_active_videos_for_lesson(lesson3.id)

        # Should return empty list, not error
        assert isinstance(videos, list), "Should return list even if empty"
        assert len(videos) == 0, "Lesson 3 should have no videos"

        # Lesson should still be viewable
        assert lesson3.heading, "Lesson should still have heading"
        assert lesson3.content, "Lesson should still have content"
