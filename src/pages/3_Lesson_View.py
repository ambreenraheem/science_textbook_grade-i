"""
Lesson View Page - Grade-1 Science Learning App

User Story 2: View Lesson Content - Part 2 (Full Lesson Display)

Displays full lesson content with:
- Heading
- Content text (2-4 lines)
- Illustration
- Daily life examples
- Videos (1-2 per lesson)
- Navigation (Next Lesson, Back)

Per Constitution I: One concept per screen, child-friendly UI
"""

import streamlit as st
from typing import Optional
from uuid import UUID

from src.lib.content_loader import ContentLoader, ContentLoaderError
from src.lib.curriculum import Lesson
from src.components.lesson_viewer import (
    render_lesson_viewer,
    render_navigation_buttons
)
from src.utils.logger import get_logger, log_user_action, get_child_friendly_message


# Configure page
st.set_page_config(
    page_title="Lesson - Grade-1",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Initialize logger
logger = get_logger(__name__)


def initialize_session_state() -> None:
    """
    Initialize session state for lesson viewing.

    Session state variables:
    - selected_chapter_id: UUID of current chapter
    - selected_lesson_id: UUID of current lesson (from previous page)
    - selected_lesson_number: Number of current lesson
    """
    if "selected_chapter_id" not in st.session_state:
        st.session_state.selected_chapter_id = None

    if "selected_lesson_id" not in st.session_state:
        st.session_state.selected_lesson_id = None

    if "selected_lesson_number" not in st.session_state:
        st.session_state.selected_lesson_number = None

    # Content loader
    if "content_loader" not in st.session_state:
        logger.error("ContentLoader not found in session state")
        st.error(get_child_friendly_message("database_error"))
        st.stop()


def handle_next_lesson_click(current_lesson: Lesson, next_lesson: Lesson) -> None:
    """
    Handle "Next Lesson" button click.

    Args:
        current_lesson: Current lesson object
        next_lesson: Next lesson object

    Side Effects:
        - Updates session state with next lesson
        - Logs navigation action
        - Triggers page reload
    """
    # Update session state
    st.session_state.selected_lesson_id = str(next_lesson.id)
    st.session_state.selected_lesson_number = next_lesson.lesson_number

    # Log navigation
    log_user_action(
        logger,
        action="next_lesson_clicked",
        from_lesson_id=str(current_lesson.id),
        from_lesson_number=current_lesson.lesson_number,
        to_lesson_id=str(next_lesson.id),
        to_lesson_number=next_lesson.lesson_number,
        chapter_id=str(current_lesson.chapter_id)
    )

    logger.info(
        f"Navigating to next lesson: {next_lesson.title}",
        extra={
            "from_lesson": current_lesson.title,
            "to_lesson": next_lesson.title,
            "chapter_id": str(current_lesson.chapter_id)
        }
    )

    # Reload page with new lesson
    st.rerun()


def handle_back_click() -> None:
    """
    Handle "Back to Lessons" button click.

    Side Effects:
        - Clears selected lesson from session state
        - Logs navigation action
        - User returns to lesson list
    """
    # Log navigation
    log_user_action(
        logger,
        action="back_to_lessons_clicked",
        from_page="lesson_view",
        lesson_id=st.session_state.selected_lesson_id
    )

    # Clear lesson selection (keep chapter selection)
    st.session_state.selected_lesson_id = None
    st.session_state.selected_lesson_number = None

    st.info("Going back to lesson list...")
    # In real app, would use st.switch_page("pages/2_Lessons.py")


def render_lesson_view_page() -> None:
    """
    Main rendering function for the lesson view page.

    Implements User Story 2: View Lesson Content - Part 2
    - Loads full lesson with details
    - Loads videos for lesson
    - Displays lesson using LessonViewer component
    - Provides Next/Back navigation
    - Includes error handling with child-friendly messages
    """
    # Initialize session state
    initialize_session_state()

    # Check if lesson is selected
    if not st.session_state.selected_lesson_id:
        st.warning("📚 Please select a lesson first!")
        st.info("Click the button below to go back and choose a lesson.")
        if st.button("⬅️ Back to Lessons", use_container_width=True):
            handle_back_click()
        return

    # Get content loader
    content_loader: ContentLoader = st.session_state.content_loader

    try:
        # Load lesson with full details
        lesson_id = UUID(st.session_state.selected_lesson_id)
        logger.debug(f"Loading lesson details for ID: {lesson_id}")

        lesson = content_loader.get_lesson_by_id(lesson_id)

        # Load videos for lesson
        videos = content_loader.get_active_videos_for_lesson(lesson_id)

        # Check for next lesson
        next_lesson = content_loader.get_next_lesson(
            lesson.chapter_id,
            lesson.lesson_number
        )
        has_next_lesson = next_lesson is not None

        # Log lesson view
        log_user_action(
            logger,
            action="lesson_viewed",
            lesson_id=str(lesson_id),
            lesson_number=lesson.lesson_number,
            lesson_title=lesson.title,
            chapter_id=str(lesson.chapter_id),
            video_count=len(videos),
            has_next_lesson=has_next_lesson
        )

        logger.info(
            f"Lesson view page rendered: {lesson.title}",
            extra={
                "lesson_id": str(lesson_id),
                "lesson_number": lesson.lesson_number,
                "lesson_title": lesson.title,
                "chapter_id": str(lesson.chapter_id),
                "video_count": len(videos),
                "has_next_lesson": has_next_lesson
            }
        )

        # Render lesson content using LessonViewer component
        render_success = render_lesson_viewer(
            lesson=lesson,
            videos=videos,
            show_validation=True
        )

        if not render_success:
            # Validation failed - error already shown by component
            logger.error(
                "Lesson viewer validation failed",
                extra={
                    "lesson_id": str(lesson_id),
                    "lesson_title": lesson.title
                }
            )
            if st.button("⬅️ Back to Lessons", use_container_width=True):
                handle_back_click()
            return

        # Render navigation buttons
        def next_click_handler():
            if next_lesson:
                handle_next_lesson_click(lesson, next_lesson)

        def back_click_handler():
            handle_back_click()

        render_navigation_buttons(
            has_next_lesson=has_next_lesson,
            on_next_click=next_click_handler,
            on_back_click=back_click_handler
        )

        # Show progress indicator
        if st.session_state.selected_chapter_id:
            chapter_id = UUID(st.session_state.selected_chapter_id)
            chapter_lessons = content_loader.get_lessons_by_chapter(chapter_id)
            total_lessons = len(chapter_lessons)

            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 2rem; color: #666;">
                    <p style="font-size: 16px;">
                        Lesson {lesson.lesson_number} of {total_lessons}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    except ValueError as e:
        # Invalid UUID
        logger.error(
            "Invalid lesson ID format",
            extra={
                "lesson_id": st.session_state.selected_lesson_id,
                "error": str(e)
            }
        )
        st.error("😢 Something went wrong. Please go back and select a lesson again.")
        if st.button("⬅️ Back to Lessons", use_container_width=True):
            handle_back_click()

    except ContentLoaderError as e:
        # Database/content loading error
        logger.error(
            "Failed to load lesson",
            extra={
                "lesson_id": st.session_state.selected_lesson_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "child_friendly": "database_error"
            }
        )

        st.error(get_child_friendly_message("database_error"))

        # Provide retry and back buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Lessons", use_container_width=True):
                handle_back_click()
        with col2:
            if st.button("🔄 Try Again", use_container_width=True):
                content_loader.clear_cache()
                st.rerun()

    except Exception as e:
        # Unexpected error
        logger.error(
            "Unexpected error in lesson view page",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "child_friendly": "general_error"
            }
        )

        st.error(get_child_friendly_message("general_error"))

        if st.button("⬅️ Back to Lessons", use_container_width=True):
            handle_back_click()


def main() -> None:
    """Page entry point."""
    # Log page visit
    log_user_action(
        logger,
        action="page_visit",
        page="lesson_view"
    )

    # Render page
    render_lesson_view_page()


# Run the page
if __name__ == "__main__" or True:  # Always run in Streamlit pages
    main()
