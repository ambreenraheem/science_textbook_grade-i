"""
Lesson Card Component

Displays an individual lesson card with:
- Lesson number
- Lesson title
- Lesson thumbnail (optional)
- Click handler for navigation

Per Constitution I: Child-friendly UI with large fonts, bright colors, and clear touch targets.
"""

import streamlit as st
from typing import Optional, Callable
from src.lib.curriculum import Lesson


def render_lesson_card(
    lesson: Lesson,
    on_click: Optional[Callable[[Lesson], None]] = None,
    key_suffix: str = ""
) -> None:
    """
    Render a single lesson card with number, title, and click handler.

    Per Constitution I: Child-friendly design with:
    - Large fonts (20-24pt for lesson titles)
    - Bright, engaging colors
    - Clear touch targets (>=48px)
    - Simple, numbered layout

    Args:
        lesson: Lesson object to display
        on_click: Optional callback function called when card is clicked
        key_suffix: Suffix for Streamlit widget keys to ensure uniqueness

    Example:
        ```python
        from src.components.lesson_card import render_lesson_card

        def handle_lesson_click(lesson):
            st.session_state.selected_lesson_id = lesson.id
            st.switch_page("pages/3_Lesson_View.py")

        render_lesson_card(lesson, on_click=handle_lesson_click)
        ```
    """
    # Create a container for the card
    with st.container():
        # Lesson card with number and title
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                border-radius: 12px;
                padding: 1.5rem;
                margin: 0.5rem 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                ">
                    <div style="
                        background: white;
                        border-radius: 50%;
                        width: 50px;
                        height: 50px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        font-weight: bold;
                        color: #FFA500;
                    ">
                        {lesson.lesson_number}
                    </div>
                    <div style="flex: 1;">
                        <h3 style="
                            margin: 0;
                            color: #333;
                            font-size: 20px;
                        ">
                            {lesson.title}
                        </h3>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Large, child-friendly button
        button_key = f"lesson_btn_{lesson.lesson_number}_{key_suffix}"
        if st.button(
            f"📖 Start Lesson {lesson.lesson_number}",
            key=button_key,
            use_container_width=True,
            type="primary"
        ):
            if on_click:
                on_click(lesson)


def render_lesson_cards_list(
    lessons: list[Lesson],
    on_click: Optional[Callable[[Lesson], None]] = None
) -> None:
    """
    Render multiple lesson cards in a vertical list.

    Args:
        lessons: List of Lesson objects to display
        on_click: Optional callback function called when a card is clicked

    Example:
        ```python
        from src.components.lesson_card import render_lesson_cards_list

        def handle_lesson_click(lesson):
            st.session_state.selected_lesson_id = lesson.id
            st.switch_page("pages/3_Lesson_View.py")

        render_lesson_cards_list(lessons, on_click=handle_lesson_click)
        ```
    """
    for idx, lesson in enumerate(lessons):
        render_lesson_card(
            lesson,
            on_click=on_click,
            key_suffix=f"list_{idx}"
        )


def get_lesson_display_name(lesson: Lesson) -> str:
    """
    Get a child-friendly display name for a lesson.

    Args:
        lesson: Lesson object

    Returns:
        Display name string (e.g., "Lesson 1: What is Living?")
    """
    return f"Lesson {lesson.lesson_number}: {lesson.title}"


def get_lesson_progress_text(current_lesson_number: int, total_lessons: int) -> str:
    """
    Get progress text for current lesson position.

    Args:
        current_lesson_number: Current lesson number (1-indexed)
        total_lessons: Total number of lessons in chapter

    Returns:
        Progress text (e.g., "Lesson 2 of 3")
    """
    return f"Lesson {current_lesson_number} of {total_lessons}"
