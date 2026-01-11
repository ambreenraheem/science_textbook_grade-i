"""
Chapter Card Component

Displays an individual chapter card with:
- Chapter image
- Chapter title
- Chapter description (optional)
- Click handler for navigation

Per Constitution I: Child-friendly UI with large fonts, bright colors, and clear touch targets.
"""

import streamlit as st
from typing import Optional, Callable
from src.lib.curriculum import Chapter


def render_chapter_card(
    chapter: Chapter,
    on_click: Optional[Callable[[Chapter], None]] = None,
    key_suffix: str = ""
) -> None:
    """
    Render a single chapter card with image, title, and click handler.

    Per Constitution I: Child-friendly design with:
    - Large fonts (28-36pt headings)
    - Bright, engaging colors
    - Clear touch targets (>=48px)
    - Simple, uncluttered layout

    Args:
        chapter: Chapter object to display
        on_click: Optional callback function called when card is clicked
        key_suffix: Suffix for Streamlit widget keys to ensure uniqueness

    Example:
        ```python
        from src.components.chapter_card import render_chapter_card

        def handle_chapter_click(chapter):
            st.session_state.selected_chapter_id = chapter.id
            st.switch_page("pages/2_Lessons.py")

        render_chapter_card(chapter, on_click=handle_chapter_click)
        ```
    """
    # Create a container for the card
    with st.container():
        # Display chapter image
        try:
            st.image(
                chapter.image_url,
                use_container_width=True,
                caption=None  # No caption to keep it clean for children
            )
        except Exception as e:
            # Graceful degradation: show placeholder if image fails
            st.info("📚 Picture loading...")
            st.write(f"_(Image: {chapter.title})_")

        # Display chapter title with large, child-friendly font
        st.markdown(
            f"<h2 style='text-align: center; color: #333; font-size: 28px; margin-top: 10px;'>"
            f"{chapter.title}"
            f"</h2>",
            unsafe_allow_html=True
        )

        # Display chapter description if available
        if chapter.description:
            st.markdown(
                f"<p style='text-align: center; color: #666; font-size: 16px; margin-bottom: 10px;'>"
                f"{chapter.description}"
                f"</p>",
                unsafe_allow_html=True
            )

        # Large, child-friendly button
        button_key = f"chapter_btn_{chapter.chapter_number}_{key_suffix}"
        if st.button(
            f"Explore {chapter.title}",
            key=button_key,
            use_container_width=True,
            type="primary"
        ):
            if on_click:
                on_click(chapter)

        # Add spacing between cards
        st.markdown("<br>", unsafe_allow_html=True)


def render_chapter_cards_grid(
    chapters: list[Chapter],
    on_click: Optional[Callable[[Chapter], None]] = None,
    columns: int = 2
) -> None:
    """
    Render multiple chapter cards in a grid layout.

    Args:
        chapters: List of Chapter objects to display
        on_click: Optional callback function called when a card is clicked
        columns: Number of columns in the grid (default: 2)

    Example:
        ```python
        from src.components.chapter_card import render_chapter_cards_grid

        def handle_chapter_click(chapter):
            st.session_state.selected_chapter_id = chapter.id
            st.switch_page("pages/2_Lessons.py")

        render_chapter_cards_grid(chapters, on_click=handle_chapter_click, columns=2)
        ```
    """
    # Create columns for grid layout
    cols = st.columns(columns)

    # Distribute chapters across columns
    for idx, chapter in enumerate(chapters):
        col_idx = idx % columns
        with cols[col_idx]:
            render_chapter_card(
                chapter,
                on_click=on_click,
                key_suffix=f"grid_{idx}"
            )


def get_chapter_display_name(chapter: Chapter) -> str:
    """
    Get a child-friendly display name for a chapter.

    Args:
        chapter: Chapter object

    Returns:
        Display name string (e.g., "Chapter 1: Living and Non-Living Things")
    """
    return f"Chapter {chapter.chapter_number}: {chapter.title}"
