"""
Lesson Viewer Component

Displays full lesson content with:
- Heading (simple, child-friendly)
- Content text (2-4 lines, max 500 chars)
- Lesson image/illustration
- Daily life examples (1-2 examples)
- Videos (if available)
- Navigation buttons (Next Lesson, Back)

Per Constitution I: Child-friendly UI
Per spec.md: One concept per screen, simple vocabulary
"""

import streamlit as st
from typing import Optional, List
from src.lib.curriculum import Lesson, Video
from src.utils.logger import get_logger, get_child_friendly_message


logger = get_logger(__name__)


def validate_lesson_content(lesson: Lesson) -> tuple[bool, Optional[str]]:
    """
    Validate lesson content meets specification requirements.

    Requirements (from spec.md and tasks.md):
    - Content length <=500 characters
    - daily_life_examples has 1-2 items

    Args:
        lesson: Lesson object to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if validation passes
        - error_message: None if valid, error message string if invalid
    """
    # Content length validation
    if len(lesson.content) > 500:
        error_msg = f"Lesson content exceeds 500 characters: {len(lesson.content)}"
        logger.warning(
            error_msg,
            extra={
                "lesson_id": str(lesson.id),
                "lesson_title": lesson.title,
                "content_length": len(lesson.content)
            }
        )
        return False, error_msg

    # Examples count validation
    examples_count = len(lesson.daily_life_examples)
    if examples_count < 1 or examples_count > 2:
        error_msg = f"Lesson should have 1-2 examples, got {examples_count}"
        logger.warning(
            error_msg,
            extra={
                "lesson_id": str(lesson.id),
                "lesson_title": lesson.title,
                "examples_count": examples_count
            }
        )
        return False, error_msg

    return True, None


def render_lesson_heading(lesson: Lesson) -> None:
    """
    Render lesson heading with lesson number and title.

    Args:
        lesson: Lesson object
    """
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="
                background: linear-gradient(135deg, #87CEEB 0%, #4682B4 100%);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <div style="color: white; font-size: 20px; margin-bottom: 0.5rem;">
                    Lesson {lesson.lesson_number}
                </div>
                <h1 style="color: white; font-size: 36px; margin: 0;">
                    {lesson.heading}
                </h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_lesson_image(lesson: Lesson) -> None:
    """
    Render lesson illustration image.

    Args:
        lesson: Lesson object with image_url
    """
    try:
        st.image(
            lesson.image_url,
            use_container_width=True,
            caption=lesson.heading
        )
    except Exception as e:
        # Graceful degradation (Constitution VIII)
        logger.warning(
            f"Failed to load lesson image: {e}",
            extra={
                "lesson_id": str(lesson.id),
                "lesson_title": lesson.title,
                "image_url": lesson.image_url,
                "error": str(e)
            }
        )
        st.info("🖼️ " + get_child_friendly_message("image_error"))


def render_lesson_content(lesson: Lesson) -> None:
    """
    Render main lesson content text.

    Args:
        lesson: Lesson object with content
    """
    st.markdown(
        f"""
        <div style="
            background-color: #FFF8DC;
            border-left: 5px solid #FFD700;
            border-radius: 8px;
            padding: 2rem;
            margin: 2rem 0;
        ">
            <p style="
                font-size: 20px;
                line-height: 1.6;
                color: #333;
                margin: 0;
            ">
                {lesson.content}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_daily_life_examples(examples: List[str]) -> None:
    """
    Render daily life examples section.

    Args:
        examples: List of 1-2 example strings
    """
    st.markdown(
        """
        <h2 style="color: #90EE90; font-size: 28px; margin-top: 2rem;">
            🌟 See It in Your Life!
        </h2>
        """,
        unsafe_allow_html=True
    )

    for idx, example in enumerate(examples, start=1):
        st.markdown(
            f"""
            <div style="
                background-color: #F0FFF0;
                border-left: 5px solid #90EE90;
                border-radius: 8px;
                padding: 1.5rem;
                margin: 1rem 0;
            ">
                <div style="
                    display: flex;
                    align-items: start;
                    gap: 1rem;
                ">
                    <div style="
                        background: #90EE90;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 20px;
                        font-weight: bold;
                        color: white;
                        flex-shrink: 0;
                    ">
                        {idx}
                    </div>
                    <p style="
                        font-size: 18px;
                        line-height: 1.5;
                        color: #333;
                        margin: 0;
                        padding-top: 0.5rem;
                    ">
                        {example}
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_videos_section(videos: List[Video]) -> None:
    """
    Render videos section below lesson content.

    Shows 1-2 YouTube videos with child-safety parameters.
    Displays fallback message if no videos available.

    Args:
        videos: List of Video objects (can be empty)
    """
    if not videos:
        # Fallback message (per spec FR-016)
        st.info("📺 " + get_child_friendly_message("video_error"))
        return

    st.markdown(
        """
        <h2 style="color: #FF6347; font-size: 28px; margin-top: 2rem;">
            🎬 Watch and Learn!
        </h2>
        """,
        unsafe_allow_html=True
    )

    for video in videos:
        # Import youtube_embedder here to avoid circular imports
        try:
            from src.lib.youtube_embedder import generate_safe_youtube_embed_url

            # Generate safe YouTube URL
            safe_url = generate_safe_youtube_embed_url(video.youtube_video_id)

            # Display video title
            st.markdown(
                f"""
                <h3 style="font-size: 20px; color: #333; margin-top: 1rem;">
                    {video.title}
                </h3>
                """,
                unsafe_allow_html=True
            )

            # Embed video
            st.components.v1.iframe(
                src=safe_url,
                width=640,
                height=360,
                scrolling=False
            )

        except ImportError:
            # youtube_embedder not yet implemented (will be in Phase 5)
            st.info(f"📺 Video: {video.title} (YouTube ID: {video.youtube_video_id})")
            logger.debug("youtube_embedder not available yet")
        except Exception as e:
            logger.error(
                f"Failed to render video: {e}",
                extra={
                    "video_id": str(video.id),
                    "video_title": video.title,
                    "youtube_video_id": video.youtube_video_id,
                    "error": str(e)
                }
            )
            st.warning(f"📺 {get_child_friendly_message('video_error')}")


def render_lesson_viewer(
    lesson: Lesson,
    videos: Optional[List[Video]] = None,
    show_validation: bool = True
) -> bool:
    """
    Render complete lesson viewer with all components.

    Args:
        lesson: Lesson object to display
        videos: Optional list of Video objects (if None, section skipped)
        show_validation: Whether to show validation errors (default: True)

    Returns:
        bool: True if lesson rendered successfully, False if validation failed
    """
    # Validate lesson content
    if show_validation:
        is_valid, error_msg = validate_lesson_content(lesson)
        if not is_valid:
            st.error(f"⚠️ Content validation error: {error_msg}")
            logger.error(
                "Lesson content validation failed",
                extra={
                    "lesson_id": str(lesson.id),
                    "lesson_title": lesson.title,
                    "error": error_msg
                }
            )
            return False

    # Render lesson components
    render_lesson_heading(lesson)
    render_lesson_image(lesson)
    render_lesson_content(lesson)
    render_daily_life_examples(lesson.daily_life_examples)

    # Render videos if provided
    if videos is not None:
        render_videos_section(videos)

    return True


def render_navigation_buttons(
    has_next_lesson: bool,
    on_next_click: Optional[callable] = None,
    on_back_click: Optional[callable] = None
) -> None:
    """
    Render navigation buttons (Next Lesson, Back).

    Args:
        has_next_lesson: Whether there is a next lesson available
        on_next_click: Callback for "Next Lesson" button
        on_back_click: Callback for "Back to Lessons" button
    """
    st.markdown("<br>", unsafe_allow_html=True)

    cols = st.columns([1, 1])

    with cols[0]:
        if st.button(
            "⬅️ Back to Lessons",
            key="back_to_lessons",
            use_container_width=True,
            type="secondary"
        ):
            if on_back_click:
                on_back_click()

    with cols[1]:
        if has_next_lesson:
            if st.button(
                "Next Lesson ➡️",
                key="next_lesson",
                use_container_width=True,
                type="primary"
            ):
                if on_next_click:
                    on_next_click()
        else:
            st.info("🎉 Great job! You've completed this chapter!")
