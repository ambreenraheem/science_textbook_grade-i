"""
Lessons Page - Grade-1 Science Learning App

User Story 2: View Lesson Content - Part 1 (Lesson List)

Displays list of lessons for selected chapter.
User can click lesson to view full content.

Per Constitution I: Child-friendly UI with large fonts, bright colors, clear touch targets.
"""

import streamlit as st
from typing import Optional
from uuid import UUID

from src.lib.content_loader import ContentLoader, ContentLoaderError
from src.lib.curriculum import Chapter, Lesson
from src.components.lesson_card import render_lesson_cards_list, get_lesson_progress_text
from src.utils.logger import get_logger, log_user_action, get_child_friendly_message


# Configure page
st.set_page_config(
    page_title="Lessons - Grade-1",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Initialize logger
logger = get_logger(__name__)


def initialize_session_state() -> None:
    """
    Initialize session state for lesson browsing.

    Session state variables:
    - selected_chapter_id: UUID of currently selected chapter (from previous page)
    - selected_lesson_id: UUID of currently selected lesson
    - selected_lesson_number: Number of currently selected lesson
    """
    # Chapter selection (should be set by Chapters page)
    if "selected_chapter_id" not in st.session_state:
        st.session_state.selected_chapter_id = None

    if "selected_lesson_id" not in st.session_state:
        st.session_state.selected_lesson_id = None

    if "selected_lesson_number" not in st.session_state:
        st.session_state.selected_lesson_number = None

    # Content loader (from main app initialization)
    if "content_loader" not in st.session_state:
        logger.error("ContentLoader not found in session state")
        st.error(get_child_friendly_message("database_error"))
        st.stop()


def handle_lesson_click(lesson: Lesson) -> None:
    """
    Handle lesson card click event.

    Stores lesson information in session state and logs the action.

    Args:
        lesson: Lesson object that was clicked

    Side Effects:
        - Updates st.session_state with selected lesson info
        - Logs user action for observability (Constitution V)
        - Navigates to lesson view page
    """
    # Store lesson info in session state
    st.session_state.selected_lesson_id = str(lesson.id)
    st.session_state.selected_lesson_number = lesson.lesson_number

    # Log user action (Constitution V: Observability)
    log_user_action(
        logger,
        action="lesson_clicked",
        lesson_id=str(lesson.id),
        lesson_number=lesson.lesson_number,
        lesson_title=lesson.title,
        chapter_id=str(lesson.chapter_id)
    )

    logger.info(
        f"Lesson selected: {lesson.title}",
        extra={
            "lesson_id": str(lesson.id),
            "lesson_number": lesson.lesson_number,
            "lesson_title": lesson.title,
            "chapter_id": str(lesson.chapter_id)
        }
    )

    # Show success message
    st.success(f"📚 Loading: **{lesson.title}**...")

    # Navigate to lesson view page
    # Note: In Streamlit multi-page apps, navigation happens via page change
    # We'll use st.switch_page when available, or rely on user clicking the lesson view link


def render_header(chapter: Chapter, lesson_count: int) -> None:
    """
    Render page header with chapter info and lesson count.

    Args:
        chapter: Current chapter object
        lesson_count: Number of lessons in chapter
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <div style="color: #666; font-size: 18px; margin-bottom: 0.5rem;">
                Chapter {chapter.chapter_number}
            </div>
            <h1 style="color: #87CEEB; font-size: 3rem; margin: 0.5rem 0;">
                📚 {chapter.title}
            </h1>
            <p style="font-size: 1.3rem; color: #666; margin-top: 0.5rem;">
                {chapter.description}
            </p>
            <div style="
                background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                border-radius: 24px;
                padding: 0.75rem 2rem;
                display: inline-block;
                margin-top: 1rem;
            ">
                <span style="color: white; font-size: 20px; font-weight: bold;">
                    {lesson_count} Lessons to Explore
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_back_to_chapters_button() -> None:
    """Render button to navigate back to chapters page."""
    if st.button("⬅️ Back to Chapters", type="secondary"):
        # Clear lesson selection
        st.session_state.selected_lesson_id = None
        st.session_state.selected_lesson_number = None

        log_user_action(
            logger,
            action="back_to_chapters_clicked",
            from_page="lessons"
        )

        st.info("Going back to chapters...")
        # In real app, would use st.switch_page("pages/1_Chapters.py")


def render_lessons_page() -> None:
    """
    Main rendering function for the lessons page.

    Implements User Story 2: View Lesson Content - Part 1
    - Loads lessons for selected chapter
    - Displays lesson cards in vertical list
    - Handles lesson selection and navigation
    - Includes error handling with child-friendly messages
    """
    # Initialize session state
    initialize_session_state()

    # Check if chapter is selected
    if not st.session_state.selected_chapter_id:
        st.warning("📚 Please select a chapter first!")
        st.info("Click 'Back to Chapters' below to choose a chapter.")
        render_back_to_chapters_button()
        return

    # Get content loader from session state
    content_loader: ContentLoader = st.session_state.content_loader

    try:
        # Load selected chapter
        chapter_id = UUID(st.session_state.selected_chapter_id)
        chapter = content_loader.get_chapter_by_id(chapter_id)

        # Load lessons for chapter
        logger.debug(f"Loading lessons for chapter: {chapter.title}")
        lessons = content_loader.get_lessons_by_chapter(chapter_id)

        # Log page view
        log_user_action(
            logger,
            action="lessons_page_displayed",
            chapter_id=str(chapter_id),
            chapter_title=chapter.title,
            lesson_count=len(lessons)
        )

        logger.info(
            f"Lessons page rendered for chapter: {chapter.title}",
            extra={
                "chapter_id": str(chapter_id),
                "chapter_title": chapter.title,
                "lesson_count": len(lessons)
            }
        )

        # Render header
        render_header(chapter, len(lessons))

        # Back button
        render_back_to_chapters_button()

        st.markdown("<br>", unsafe_allow_html=True)

        # Handle empty state
        if not lessons:
            st.info(
                "📖 No lessons available yet for this chapter!\n\n"
                "Lessons are being prepared. Check back soon!"
            )
            logger.warning(
                f"No lessons found for chapter: {chapter.title}",
                extra={"chapter_id": str(chapter_id)}
            )
            return

        # Render lesson cards
        st.markdown(
            """
            <h2 style="color: #333; font-size: 28px; margin-top: 2rem;">
                Choose a Lesson to Start Learning
            </h2>
            """,
            unsafe_allow_html=True
        )

        render_lesson_cards_list(
            lessons=lessons,
            on_click=handle_lesson_click
        )

        # Show hint if lesson selected
        if st.session_state.selected_lesson_id:
            st.markdown(
                f"""
                <div style="
                    text-align: center;
                    padding: 1.5rem;
                    background: linear-gradient(135deg, #90EE90 0%, #00CED1 100%);
                    border-radius: 12px;
                    margin-top: 2rem;
                ">
                    <p style="color: white; font-size: 20px; margin: 0;">
                        ✨ Lesson {st.session_state.selected_lesson_number} selected!
                        The lesson is loading above.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    except ValueError as e:
        # Invalid UUID
        logger.error(
            "Invalid chapter ID format",
            extra={
                "chapter_id": st.session_state.selected_chapter_id,
                "error": str(e)
            }
        )
        st.error("😢 Something went wrong. Please go back and select a chapter again.")
        render_back_to_chapters_button()

    except ContentLoaderError as e:
        # Database/content loading error
        logger.error(
            "Failed to load lessons",
            extra={
                "chapter_id": st.session_state.selected_chapter_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "child_friendly": "database_error"
            }
        )

        st.error(get_child_friendly_message("database_error"))

        # Provide retry button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Try Again", use_container_width=True):
                content_loader.clear_cache()
                st.rerun()
        with col2:
            render_back_to_chapters_button()

    except Exception as e:
        # Unexpected error
        logger.error(
            "Unexpected error in lessons page",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "child_friendly": "general_error"
            }
        )

        st.error(get_child_friendly_message("general_error"))

        # Provide home button
        render_back_to_chapters_button()


def main() -> None:
    """Page entry point."""
    # Log page visit
    log_user_action(
        logger,
        action="page_visit",
        page="lessons"
    )

    # Render page
    render_lessons_page()


# Run the page
if __name__ == "__main__" or True:  # Always run in Streamlit pages
    main()
