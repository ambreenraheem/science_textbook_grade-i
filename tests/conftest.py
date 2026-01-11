"""
Pytest configuration and shared fixtures for Grade-1 Science Learning App tests.

Provides:
- Database setup with test database
- Test data seeding
- DatabaseManager and ContentLoader fixtures
- Session management
"""

import os
import pytest
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.lib.curriculum import Base, Chapter, Lesson, Video
from src.utils.database import DatabaseManager
from src.lib.content_loader import ContentLoader


# Test database URL (using SQLite for tests to avoid dependency on Neon)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./test_grade1_science.db"
)


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create a test database engine for the entire test session.

    Uses SQLite for testing to avoid external dependencies.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
    )

    # Create all tables
    Base.metadata.create_all(engine)

    yield engine

    # Cleanup: drop all tables
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.

    Clears all tables before each test to ensure isolation.
    """
    # Clear all tables before each test
    Base.metadata.drop_all(test_db_engine)
    Base.metadata.create_all(test_db_engine)

    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture(scope="function")
def seed_chapters(db_session: Session) -> list[Chapter]:
    """
    Seed the database with the 4 Grade-1 science chapters.

    Returns:
        List of Chapter objects (ordered by chapter_number)
    """
    chapters = [
        Chapter(
            title="Living and Non-Living Things",
            chapter_number=1,
            description="Learn about things that are alive and things that are not.",
            image_url="https://via.placeholder.com/400x300/87CEEB/333333?text=Living+%26+Non-Living"
        ),
        Chapter(
            title="Plants",
            chapter_number=2,
            description="Discover different types of plants and how they grow.",
            image_url="https://via.placeholder.com/400x300/90EE90/333333?text=Plants"
        ),
        Chapter(
            title="Animals",
            chapter_number=3,
            description="Explore the animal kingdom and their habitats.",
            image_url="https://via.placeholder.com/400x300/FFB6C1/333333?text=Animals"
        ),
        Chapter(
            title="Food",
            chapter_number=4,
            description="Understand where our food comes from and why it is important.",
            image_url="https://via.placeholder.com/400x300/FFD700/333333?text=Food"
        )
    ]

    for chapter in chapters:
        db_session.add(chapter)

    db_session.commit()

    # Refresh to get IDs
    for chapter in chapters:
        db_session.refresh(chapter)

    return chapters


@pytest.fixture(scope="function")
def seed_lessons(db_session: Session, seed_chapters: list[Chapter]) -> list[Lesson]:
    """
    Seed the database with sample lessons for testing.

    Creates lessons for Chapter 1 (Living and Non-Living Things).

    Returns:
        List of Lesson objects
    """
    chapter1 = seed_chapters[0]

    lessons = [
        Lesson(
            chapter_id=chapter1.id,
            title="What is Living?",
            lesson_number=1,
            heading="Living Things",
            content="Living things can grow, eat, and move. Plants and animals are living. They need water and food to stay alive.",
            image_url="https://via.placeholder.com/600x400/87CEEB/333333?text=Living+Things",
            daily_life_examples=["Your pet dog is living because it eats and plays.", "The tree in your yard grows bigger every year."]
        ),
        Lesson(
            chapter_id=chapter1.id,
            title="What is Non-Living?",
            lesson_number=2,
            heading="Non-Living Things",
            content="Non-living things do not grow or eat. Rocks, toys, and chairs are non-living. They stay the same size.",
            image_url="https://via.placeholder.com/600x400/87CEEB/333333?text=Non-Living+Things",
            daily_life_examples=["Your toy car does not need food or water.", "A rock does not grow bigger like you do."]
        ),
        Lesson(
            chapter_id=chapter1.id,
            title="How Are They Different?",
            lesson_number=3,
            heading="Living vs Non-Living",
            content="Living things need food, water, and air. Non-living things do not need these. Look around your room!",
            image_url="https://via.placeholder.com/600x400/87CEEB/333333?text=Differences",
            daily_life_examples=["Your stuffed animal is non-living, but your pet fish is living.", "The flower on the table is living, but the table is not."]
        )
    ]

    for lesson in lessons:
        db_session.add(lesson)

    db_session.commit()

    # Refresh to get IDs
    for lesson in lessons:
        db_session.refresh(lesson)

    return lessons


@pytest.fixture(scope="function")
def seed_videos(db_session: Session, seed_lessons: list[Lesson]) -> list[Video]:
    """
    Seed the database with sample videos for testing.

    Creates videos for the first lesson.

    Returns:
        List of Video objects
    """
    lesson1 = seed_lessons[0]

    videos = [
        Video(
            lesson_id=lesson1.id,
            title="Living Things for Kids",
            youtube_video_id="ABC1234WXYZ",
            display_order=1,
            duration_seconds=180,
            is_active=True
        ),
        Video(
            lesson_id=lesson1.id,
            title="Examples of Living Things",
            youtube_video_id="DEF5678UVWX",
            display_order=2,
            duration_seconds=120,
            is_active=True
        )
    ]

    for video in videos:
        db_session.add(video)

    db_session.commit()

    # Refresh to get IDs
    for video in videos:
        db_session.refresh(video)

    return videos


@pytest.fixture(scope="function")
def db_manager_mock(test_db_engine):
    """
    Create a mock DatabaseManager for testing ContentLoader.

    This provides a DatabaseManager-like interface but uses the test database.
    """
    class TestDatabaseManager:
        """Mock DatabaseManager for testing."""

        def __init__(self, engine):
            self.engine = engine
            self._session_factory = sessionmaker(
                bind=engine,
                expire_on_commit=False,  # Keep objects usable after commit
                autoflush=False
            )

        def get_session(self):
            """Context manager for database sessions."""
            from contextlib import contextmanager

            @contextmanager
            def session_context():
                session = self._session_factory()
                try:
                    yield session
                    session.commit()
                except Exception:
                    session.rollback()
                    raise
                finally:
                    session.expunge_all()  # Detach all objects before closing
                    session.close()

            return session_context()

    return TestDatabaseManager(test_db_engine)


@pytest.fixture(scope="function")
def content_loader(db_manager_mock, seed_chapters) -> ContentLoader:
    """
    Create a ContentLoader instance with test database and seeded data.

    The database is pre-seeded with chapters via the seed_chapters fixture.
    """
    return ContentLoader(db_manager_mock)
