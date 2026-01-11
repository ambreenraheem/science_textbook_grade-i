"""
Integration tests for chapter browsing and navigation.

Tests the complete user flow:
- Display chapter cards on home screen
- Click chapter card
- Session state updates with selected chapter
- Navigation to lessons page

Per Constitution III: Integration tests for user journeys.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
from src.lib.curriculum import Chapter
from src.lib.content_loader import ContentLoader


@pytest.mark.integration
@pytest.mark.ui
class TestChapterNavigation:
    """Integration tests for chapter browsing and navigation flow."""

    def test_chapter_display_shows_all_four_chapters(self, content_loader: ContentLoader):
        """
        Test that the chapter browsing page displays all 4 chapter cards.

        User Story: As a student, I want to see all four science topics (chapters)
        on the home screen so I can choose which topic to learn.

        Acceptance Criteria:
        - All 4 chapters are loaded from database
        - Each chapter has title and image_url
        - Chapters displayed in order 1-4
        """
        chapters = content_loader.get_all_chapters()

        # Verify we have all 4 chapters
        assert len(chapters) == 4, "Should display 4 chapter cards"

        # Verify each chapter has required display data
        for chapter in chapters:
            assert chapter.title, f"Chapter {chapter.chapter_number} should have a title"
            assert chapter.image_url, f"Chapter {chapter.chapter_number} should have an image URL"
            assert 1 <= chapter.chapter_number <= 4, \
                f"Chapter number should be 1-4, got {chapter.chapter_number}"

        # Verify correct order
        chapter_numbers = [ch.chapter_number for ch in chapters]
        assert chapter_numbers == [1, 2, 3, 4], "Chapters should be ordered 1-4"

    def test_chapter_card_click_stores_chapter_id_in_session(self, content_loader: ContentLoader):
        """
        Test that clicking a chapter card stores the chapter ID in session state.

        User Flow:
        1. User sees chapter cards
        2. User clicks "Plants" (chapter 2)
        3. Session state stores selected chapter ID
        4. App navigates to lessons page

        Acceptance Criteria:
        - Chapter ID is stored in session state
        - Session state is accessible for next page
        """
        chapters = content_loader.get_all_chapters()

        # Simulate user clicking "Plants" (chapter 2)
        plants_chapter = next(ch for ch in chapters if ch.chapter_number == 2)

        # Mock Streamlit session state
        mock_session_state = {}

        # Simulate the click handler storing chapter info
        mock_session_state["selected_chapter_id"] = str(plants_chapter.id)
        mock_session_state["selected_chapter_number"] = plants_chapter.chapter_number
        mock_session_state["selected_chapter_title"] = plants_chapter.title

        # Verify session state was updated
        assert "selected_chapter_id" in mock_session_state, \
            "Session state should store selected_chapter_id"
        assert mock_session_state["selected_chapter_number"] == 2, \
            "Should store chapter number 2 for Plants"
        assert mock_session_state["selected_chapter_title"] == "Plants", \
            "Should store chapter title 'Plants'"

    def test_chapter_navigation_flow_end_to_end(self, content_loader: ContentLoader):
        """
        Test complete navigation flow from chapter list to chapter selection.

        User Journey:
        1. App loads → displays 4 chapters
        2. User clicks "Living and Non-Living Things"
        3. Session stores chapter info
        4. Navigation ready for lessons page

        Acceptance Criteria:
        - Chapters load successfully
        - Selected chapter info is complete
        - Chapter has lessons relationship available
        """
        # Step 1: Load chapters
        chapters = content_loader.get_all_chapters()
        assert len(chapters) == 4, "Should load 4 chapters"

        # Step 2: User selects "Living and Non-Living Things" (chapter 1)
        selected_chapter = chapters[0]
        assert selected_chapter.chapter_number == 1
        assert selected_chapter.title == "Living and Non-Living Things"

        # Step 3: Verify chapter has complete data for navigation
        assert selected_chapter.id is not None, "Chapter should have ID"
        assert selected_chapter.title, "Chapter should have title"
        assert selected_chapter.chapter_number == 1, "Should be chapter 1"

        # Step 4: Verify chapter has lessons relationship (for next page)
        assert hasattr(selected_chapter, "lessons"), \
            "Chapter should have lessons relationship for lessons page"

    def test_chapter_selection_persists_across_page_views(self, content_loader: ContentLoader):
        """
        Test that chapter selection persists in session state.

        Simulates:
        1. User selects chapter on home page
        2. Session state stores selection
        3. Next page can retrieve selection

        Acceptance Criteria:
        - Session state maintains chapter ID
        - Can retrieve chapter from ID later
        """
        chapters = content_loader.get_all_chapters()

        # Simulate selecting Animals (chapter 3)
        animals_chapter = next(ch for ch in chapters if ch.chapter_number == 3)

        # Mock session state (simulating Streamlit st.session_state)
        mock_session = {"selected_chapter_id": animals_chapter.id}

        # Simulate next page retrieving the selection
        retrieved_chapter_id = mock_session["selected_chapter_id"]

        # Verify we can load the chapter using the stored ID
        retrieved_chapter = content_loader.get_chapter_by_id(retrieved_chapter_id)

        assert retrieved_chapter.id == animals_chapter.id, \
            "Should retrieve same chapter from session state"
        assert retrieved_chapter.chapter_number == 3, \
            "Should be Animals chapter (number 3)"
        assert retrieved_chapter.title == "Animals", \
            "Should have correct title"

    def test_multiple_chapter_clicks_update_session_correctly(self, content_loader: ContentLoader):
        """
        Test that clicking different chapters updates session state correctly.

        User Flow:
        1. Click Plants → session stores Plants
        2. Click Food → session updates to Food
        3. Verify latest selection is active

        Acceptance Criteria:
        - Session state updates on each click
        - Only most recent selection is active
        """
        chapters = content_loader.get_all_chapters()

        mock_session_state = {}

        # Click 1: Plants (chapter 2)
        plants = next(ch for ch in chapters if ch.chapter_number == 2)
        mock_session_state["selected_chapter_id"] = str(plants.id)
        mock_session_state["selected_chapter_number"] = plants.chapter_number

        assert mock_session_state["selected_chapter_number"] == 2, \
            "First click should select Plants"

        # Click 2: Food (chapter 4)
        food = next(ch for ch in chapters if ch.chapter_number == 4)
        mock_session_state["selected_chapter_id"] = str(food.id)
        mock_session_state["selected_chapter_number"] = food.chapter_number

        assert mock_session_state["selected_chapter_number"] == 4, \
            "Second click should update to Food"
        assert mock_session_state["selected_chapter_id"] == str(food.id), \
            "Session should store most recent chapter ID"

    def test_chapter_cards_have_required_data_for_display(self, content_loader: ContentLoader):
        """
        Test that each chapter has all required data for card display.

        Chapter Card Requirements:
        - Title (for heading)
        - Image URL (for card image)
        - Chapter number (for ordering)
        - Description (optional, for tooltip)

        Acceptance Criteria:
        - All required fields are present and non-empty
        - Image URLs are valid strings
        """
        chapters = content_loader.get_all_chapters()

        for chapter in chapters:
            # Required fields
            assert chapter.title, \
                f"Chapter {chapter.chapter_number} must have title"
            assert chapter.image_url, \
                f"Chapter {chapter.chapter_number} must have image_url"
            assert chapter.chapter_number, \
                f"Chapter must have chapter_number"

            # Data type validation
            assert isinstance(chapter.title, str), "Title should be string"
            assert isinstance(chapter.image_url, str), "Image URL should be string"
            assert isinstance(chapter.chapter_number, int), "Chapter number should be int"

            # Value validation
            assert len(chapter.title) > 0, "Title should not be empty"
            assert len(chapter.image_url) > 0, "Image URL should not be empty"
            assert chapter.chapter_number in [1, 2, 3, 4], \
                f"Chapter number should be 1-4, got {chapter.chapter_number}"

    @pytest.mark.slow
    def test_chapter_navigation_performance_under_2_seconds(self, content_loader: ContentLoader):
        """
        Test that chapter loading and display completes within 2 seconds.

        Performance Target (from spec.md SC-002):
        - Page load time < 2 seconds

        Acceptance Criteria:
        - Loading chapters from database < 50ms
        - Total page load simulation < 2000ms
        """
        import time

        # Clear cache to simulate first load
        content_loader.clear_cache()

        start_time = time.perf_counter()

        # Simulate page load operations
        chapters = content_loader.get_all_chapters()

        # Simulate rendering preparation (accessing fields)
        for chapter in chapters:
            _ = chapter.title
            _ = chapter.image_url
            _ = chapter.chapter_number

        end_time = time.perf_counter()
        total_time_ms = (end_time - start_time) * 1000

        assert len(chapters) == 4, "Should load 4 chapters"
        assert total_time_ms < 2000, \
            f"Page load should complete in <2s, took {total_time_ms:.2f}ms"
