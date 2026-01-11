"""
Chapters Page - Grade-1 Science Learning App

User Story 1 (MVP): Browse Science Chapters

Displays four chapter cards (Living/Non-Living, Plants, Animals, Food) on the home screen.
User can click any card to navigate to that chapter's lesson list.

Per Constitution I: Child-friendly UI with large fonts, bright colors, clear touch targets.
"""

import streamlit as st
from typing import Optional
from uuid import UUID

from src.lib.content_loader import ContentLoader, ContentLoaderError
from src.lib.curriculum import Chapter
from src.components.chapter_card import render_chapter_cards_grid
from src.utils.logger import get_logger, log_user_action, get_child_friendly_message


# Configure page
st.set_page_config(
    page_title="Science Chapters - Grade-1",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Initialize logger
logger = get_logger(__name__)


def initialize_session_state() -> None:
    """
    Initialize session state for chapter browsing.

    Session state variables:
    - selected_chapter_id: UUID of currently selected chapter
    - selected_chapter_number: Number of currently selected chapter
    - selected_chapter_title: Title of currently selected chapter
    """
    if "selected_chapter_id" not in st.session_state:
        st.session_state.selected_chapter_id = None

    if "selected_chapter_number" not in st.session_state:
        st.session_state.selected_chapter_number = None

    if "selected_chapter_title" not in st.session_state:
        st.session_state.selected_chapter_title = None

    # Content loader (from main app initialization)
    if "content_loader" not in st.session_state:
        # If not initialized, this is an error - should be set by app.py
        logger.error("ContentLoader not found in session state")
        st.error(get_child_friendly_message("database_error"))
        st.stop()


def handle_chapter_click(chapter: Chapter) -> None:
    """
    Handle chapter card click event.

    Stores chapter information in session state and logs the action.

    Args:
        chapter: Chapter object that was clicked

    Side Effects:
        - Updates st.session_state with selected chapter info
        - Logs user action for observability (Constitution V)
        - Triggers navigation to lessons page (future: would use st.switch_page)
    """
    # Store chapter info in session state
    st.session_state.selected_chapter_id = str(chapter.id)
    st.session_state.selected_chapter_number = chapter.chapter_number
    st.session_state.selected_chapter_title = chapter.title

    # Log user action (Constitution V: Observability)
    log_user_action(
        logger,
        action="chapter_clicked",
        chapter_id=str(chapter.id),
        chapter_number=chapter.chapter_number,
        chapter_title=chapter.title
    )

    logger.info(
        f"Chapter selected: {chapter.title}",
        extra={
            "chapter_id": str(chapter.id),
            "chapter_number": chapter.chapter_number,
            "chapter_title": chapter.title
        }
    )

    # Show success message to child
    st.success(f"🎉 Great choice! You selected: **{chapter.title}**")

    # Future: Navigate to lessons page
    # st.switch_page("pages/2_Lessons.py")


def render_header() -> None:
    """Render page header with title and description."""
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <h1 style="color: #87CEEB; font-size: 3rem; margin-bottom: 0.5rem;">
                📚 Choose Your Science Adventure!
            </h1>
            <p style="font-size: 1.5rem; color: #666; margin-top: 0;">
                Click on a chapter to start learning
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_chapters_page() -> None:
    """
    Main rendering function for the chapters page.

    Implements User Story 1: Browse Science Chapters
    - Loads all chapters from database
    - Displays chapter cards in 2-column grid
    - Handles chapter selection and navigation
    - Includes error handling with child-friendly messages
    """
    # Initialize session state
    initialize_session_state()

    # Render header
    render_header()

    # Get content loader from session state
    content_loader: ContentLoader = st.session_state.content_loader

    try:
        # Load all chapters
        logger.debug("Loading chapters from database")
        chapters = content_loader.get_all_chapters()

        # Log successful load
        log_user_action(
            logger,
            action="chapters_displayed",
            chapter_count=len(chapters)
        )

        logger.info(
            f"Chapters page rendered successfully",
            extra={"chapter_count": len(chapters)}
        )

        # Handle empty state
        if not chapters:
            st.warning(
                "📚 No chapters available yet!\n\n"
                "Our science lessons are being prepared. Check back soon!"
            )
            logger.warning("No chapters found in database")
            return

        # Verify we have exactly 4 chapters (per spec)
        if len(chapters) != 4:
            logger.warning(
                f"Expected 4 chapters, found {len(chapters)}",
                extra={"chapter_count": len(chapters)}
            )

        # Render chapters in 2-column grid
        render_chapter_cards_grid(
            chapters=chapters,
            on_click=handle_chapter_click,
            columns=2
        )

        # Show selected chapter info if available
        if st.session_state.selected_chapter_id:
            st.markdown("---")
            st.markdown(
                f"""
                <div style="text-align: center; padding: 1rem; background-color: #FFD700;
                     border-radius: 12px; margin: 1rem 0;">
                    <h3 style="margin: 0; color: #333;">
                        📖 You selected: {st.session_state.selected_chapter_title}
                    </h3>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; color: #666;">
                        Get ready to explore Chapter {st.session_state.selected_chapter_number}!
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    except ContentLoaderError as e:
        # Database/content loading error
        logger.error(
            "Failed to load chapters",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "child_friendly": "database_error"
            }
        )

        st.error(get_child_friendly_message("database_error"))

        # Provide retry button
        if st.button("🔄 Try Again", use_container_width=True):
            content_loader.clear_cache()
            st.rerun()

    except Exception as e:
        # Unexpected error
        logger.error(
            "Unexpected error in chapters page",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "child_friendly": "general_error"
            }
        )

        st.error(get_child_friendly_message("general_error"))

        # Provide home button
        if st.button("🏠 Go Home", use_container_width=True):
            # Clear error state
            for key in ["selected_chapter_id", "selected_chapter_number", "selected_chapter_title"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


def main() -> None:
    """Page entry point."""
    # Log page visit
    log_user_action(
        logger,
        action="page_visit",
        page="chapters"
    )

    # Render page
    render_chapters_page()


# Run the page
if __name__ == "__main__" or True:  # Always run in Streamlit pages
    main()
