"""
Grade-1 Science Learning Web Application

Main entry point for the Streamlit application.

Features:
- Multi-page navigation
- Session state management
- Database connection pooling
- Error boundaries with child-friendly messages
- Custom CSS for child-friendly design
"""
import streamlit as st
from pathlib import Path
from typing import Optional

from src.utils.config import load_config
from src.utils.database import DatabaseManager
from src.utils.logger import get_logger, log_user_action, get_child_friendly_message
from src.lib.content_loader import ContentLoader, ContentLoaderError


# Configure page settings (must be first Streamlit command)
st.set_page_config(
    page_title="Grade-1 Science Learning",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",  # Hide sidebar for cleaner child UI
    menu_items={
        'Get Help': None,  # Disable to keep child-focused
        'Report a bug': None,
        'About': "# Grade-1 Science Learning\nFun science for young learners!"
    }
)


# Initialize logger
logger = get_logger(__name__)


def load_custom_css() -> None:
    """Load custom CSS for child-friendly design."""
    css_path = Path(__file__).parent.parent / "static" / "styles" / "child_friendly.css"

    try:
        if css_path.exists():
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
                logger.debug("Custom CSS loaded successfully")
        else:
            logger.warning(f"CSS file not found: {css_path}")
    except Exception as e:
        logger.error(f"Failed to load custom CSS: {e}")
        # Non-critical error, continue without custom CSS


def initialize_database() -> Optional[DatabaseManager]:
    """
    Initialize database connection.

    Returns:
        DatabaseManager instance or None if initialization fails
    """
    try:
        config = load_config()

        if not config.database_url:
            logger.error("DATABASE_URL not configured")
            st.error(get_child_friendly_message("database_error"))
            st.stop()

        db_manager = DatabaseManager()
        db_manager.initialize(config.database_url)

        # Verify connection
        if db_manager.health_check():
            logger.info("Database connection initialized successfully")
            return db_manager
        else:
            logger.error("Database health check failed")
            st.error(get_child_friendly_message("database_error"))
            st.stop()

    except Exception as e:
        logger.error(
            "Failed to initialize database",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "child_friendly": "database_error"
            }
        )
        st.error(get_child_friendly_message("database_error"))
        st.stop()


def initialize_session_state() -> None:
    """Initialize Streamlit session state with default values."""
    # Database manager (singleton per session)
    if "db_manager" not in st.session_state:
        st.session_state.db_manager = initialize_database()

    # Content loader (singleton per session)
    if "content_loader" not in st.session_state:
        st.session_state.content_loader = ContentLoader(st.session_state.db_manager)

    # Navigation state
    if "current_chapter" not in st.session_state:
        st.session_state.current_chapter = None

    if "current_lesson" not in st.session_state:
        st.session_state.current_lesson = None

    # User progress tracking (future feature)
    if "visited_lessons" not in st.session_state:
        st.session_state.visited_lessons = set()

    logger.debug("Session state initialized")


def render_header() -> None:
    """Render the application header with title and navigation."""
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: var(--color-primary, #87CEEB); font-size: 2.5rem;">
                🔬 Grade-1 Science Learning
            </h1>
            <p style="font-size: 1.5rem; color: var(--color-text, #333333);">
                Let's explore the world of science together!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_error_boundary() -> None:
    """Render error boundary for the entire application."""
    try:
        # Load custom CSS
        load_custom_css()

        # Initialize session state
        initialize_session_state()

        # Render header
        render_header()

        # Load content loader from session state
        content_loader: ContentLoader = st.session_state.content_loader

        # Main content area - Chapter browsing (User Story 1)
        render_chapter_browser(content_loader)

    except ContentLoaderError as e:
        logger.error(f"Content loading error: {e}")
        st.error(get_child_friendly_message("database_error"))
        if st.button("🔄 Try Again"):
            st.rerun()

    except Exception as e:
        logger.error(
            "Unexpected application error",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "child_friendly": "default"
            }
        )
        st.error(get_child_friendly_message("default"))
        if st.button("🏠 Go Home"):
            # Clear session state and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def render_chapter_browser(content_loader: ContentLoader) -> None:
    """
    Render the chapter browsing interface (User Story 1: MVP).

    Args:
        content_loader: ContentLoader instance for database queries
    """
    st.markdown("## 📚 Choose a Chapter to Start Learning!")

    try:
        # Load all chapters
        chapters = content_loader.get_all_chapters()

        if not chapters:
            st.warning("No chapters available yet. Check back soon!")
            logger.warning("No chapters found in database")
            return

        # Display chapters in a grid (2 columns for large screens)
        cols = st.columns(2)

        for idx, chapter in enumerate(chapters):
            col = cols[idx % 2]

            with col:
                # Create chapter card
                with st.container():
                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="card-title">
                                Chapter {chapter.chapter_number}: {chapter.title}
                            </div>
                            <p style="font-size: 1.2rem; margin-bottom: 1rem;">
                                {chapter.description or "Explore this chapter!"}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Chapter button
                    if st.button(
                        f"🚀 Start Chapter {chapter.chapter_number}",
                        key=f"chapter_{chapter.id}",
                        use_container_width=True
                    ):
                        log_user_action(
                            action="chapter_selected",
                            details={
                                "chapter_id": str(chapter.id),
                                "chapter_number": chapter.chapter_number,
                                "chapter_title": chapter.title
                            }
                        )
                        st.session_state.current_chapter = chapter
                        st.info(
                            f"🎉 Great choice! You selected: **{chapter.title}**\n\n"
                            f"This chapter has {len(chapter.lessons)} exciting lessons!"
                        )

                st.markdown("<br>", unsafe_allow_html=True)

        # Show selected chapter details
        if st.session_state.current_chapter:
            selected_chapter = st.session_state.current_chapter
            st.markdown("---")
            st.markdown(
                f"""
                ### 📖 Selected: Chapter {selected_chapter.chapter_number} - {selected_chapter.title}

                {selected_chapter.description}
                """
            )

            # Display lessons in selected chapter
            if selected_chapter.lessons:
                st.markdown("#### Lessons in this chapter:")
                for lesson in sorted(selected_chapter.lessons, key=lambda l: l.lesson_number):
                    st.markdown(
                        f"""
                        <div style="padding: 0.5rem 1rem; margin: 0.5rem 0;
                             background-color: var(--color-highlight, #FFD700);
                             border-radius: 8px;">
                            <strong>Lesson {lesson.lesson_number}:</strong> {lesson.title}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("Lessons coming soon!")

    except ContentLoaderError as e:
        logger.error(f"Failed to load chapters: {e}")
        st.error(get_child_friendly_message("database_error"))
        if st.button("🔄 Retry Loading Chapters"):
            content_loader.clear_cache()
            st.rerun()

    except Exception as e:
        logger.error(
            "Unexpected error in chapter browser",
            extra={
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        st.error(get_child_friendly_message("default"))


def main() -> None:
    """Main application entry point."""
    try:
        # Log application start
        logger.info("Application started")
        log_user_action("app_start", {})

        # Render application with error boundary
        render_error_boundary()

    except Exception as e:
        # Last resort error handler
        logger.critical(
            "Critical application error",
            extra={
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        st.error(
            "😢 Oh no! Something unexpected happened.\n\n"
            "Please refresh the page to try again."
        )


if __name__ == "__main__":
    main()
