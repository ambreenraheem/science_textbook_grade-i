"""
Database connection management for Neon PostgreSQL.

This module provides SQLAlchemy engine and session management with connection pooling.
Supports graceful degradation per Constitution VIII when database is unavailable.
"""

from contextlib import contextmanager
from typing import Generator, Optional
import time

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.pool import QueuePool

from .config import get_config
from .logger import get_logger

logger = get_logger(__name__)


class DatabaseConnectionError(Exception):
    """Raised when database connection cannot be established."""
    pass


class DatabaseManager:
    """
    Manages database connections with retry logic and connection pooling.

    Features:
    - Connection pooling (5 connections, 10 overflow)
    - Automatic retry with exponential backoff
    - Connection health checks
    - Graceful error handling
    """

    def __init__(self):
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._initialized = False

    def initialize(self, database_url: Optional[str] = None) -> None:
        """
        Initialize database engine and session factory.

        Args:
            database_url: PostgreSQL connection string. If None, loads from config.

        Raises:
            DatabaseConnectionError: If connection cannot be established after retries.
        """
        if self._initialized:
            logger.info("Database already initialized")
            return

        # Get database URL from config or parameter
        url = database_url or get_config().database_url

        if not url:
            raise DatabaseConnectionError("DATABASE_URL not configured")

        try:
            # Create engine with connection pooling
            self._engine = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=5,  # Number of connections to maintain
                max_overflow=10,  # Additional connections when pool exhausted
                pool_timeout=30,  # Timeout waiting for connection
                pool_recycle=3600,  # Recycle connections after 1 hour
                pool_pre_ping=True,  # Verify connection health before use
                echo=False,  # Set to True for SQL query logging
            )

            # Add connection event listeners
            event.listen(self._engine, "connect", self._on_connect)
            event.listen(self._engine, "checkout", self._on_checkout)

            # Create session factory
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )

            # Test connection with retry
            self._test_connection_with_retry()

            self._initialized = True
            logger.info(
                "Database initialized successfully",
                extra={"pool_size": 5, "max_overflow": 10}
            )

        except Exception as e:
            logger.error(
                "Failed to initialize database",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise DatabaseConnectionError(f"Database initialization failed: {e}")

    def _test_connection_with_retry(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> None:
        """
        Test database connection with exponential backoff retry.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds (doubles each retry)

        Raises:
            DatabaseConnectionError: If all retries fail
        """
        for attempt in range(1, max_retries + 1):
            try:
                with self._engine.connect() as conn:
                    conn.execute("SELECT 1")
                logger.info(f"Database connection test successful (attempt {attempt})")
                return
            except OperationalError as e:
                delay = base_delay * (2 ** (attempt - 1))
                logger.warning(
                    f"Database connection test failed (attempt {attempt}/{max_retries})",
                    extra={"error": str(e), "retry_delay_seconds": delay}
                )
                if attempt < max_retries:
                    time.sleep(delay)
                else:
                    raise DatabaseConnectionError(
                        f"Database connection test failed after {max_retries} attempts"
                    )

    def _on_connect(self, dbapi_conn, connection_record):
        """Event listener called when new database connection is created."""
        logger.debug("New database connection established")

    def _on_checkout(self, dbapi_conn, connection_record, connection_proxy):
        """Event listener called when connection is checked out from pool."""
        logger.debug("Database connection checked out from pool")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions with automatic cleanup.

        Yields:
            Session: SQLAlchemy session

        Raises:
            DatabaseConnectionError: If database not initialized

        Example:
            ```python
            db = DatabaseManager()
            db.initialize()

            with db.get_session() as session:
                chapters = session.query(Chapter).all()
            ```
        """
        if not self._initialized or not self._session_factory:
            raise DatabaseConnectionError("Database not initialized. Call initialize() first.")

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(
                "Database session error",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            raise
        finally:
            session.close()

    def close(self) -> None:
        """Close database engine and dispose of connection pool."""
        if self._engine:
            self._engine.dispose()
            self._initialized = False
            logger.info("Database connection pool closed")

    @property
    def is_initialized(self) -> bool:
        """Check if database is initialized and ready."""
        return self._initialized

    @property
    def engine(self) -> Engine:
        """Get SQLAlchemy engine (for migrations, advanced usage)."""
        if not self._engine:
            raise DatabaseConnectionError("Database not initialized")
        return self._engine


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """
    Get global database manager instance (singleton pattern).

    Returns:
        DatabaseManager: Global database manager
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def initialize_database(database_url: Optional[str] = None) -> None:
    """
    Initialize global database manager.

    Args:
        database_url: PostgreSQL connection string. If None, loads from config.

    Raises:
        DatabaseConnectionError: If initialization fails
    """
    db_manager = get_db_manager()
    db_manager.initialize(database_url)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Convenience function to get database session from global manager.

    Yields:
        Session: SQLAlchemy session

    Example:
        ```python
        from src.utils.database import initialize_database, get_db_session

        initialize_database()

        with get_db_session() as session:
            chapters = session.query(Chapter).all()
        ```
    """
    db_manager = get_db_manager()
    with db_manager.get_session() as session:
        yield session


def close_database() -> None:
    """Close global database manager and dispose of connections."""
    global _db_manager
    if _db_manager:
        _db_manager.close()
        _db_manager = None
