"""
Environment configuration management.

Loads configuration from environment variables using python-dotenv.
Provides type-safe access to application settings.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    """
    Application configuration loaded from environment variables.

    Attributes:
        database_url: PostgreSQL connection string for Neon database
        app_env: Application environment (development, staging, production)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        streamlit_server_port: Port for Streamlit server
        streamlit_server_enable_cors: Enable CORS for Streamlit
        enable_analytics: Feature flag for analytics tracking
    """

    # Database
    database_url: Optional[str]

    # Application
    app_env: str
    log_level: str

    # Streamlit
    streamlit_server_port: int
    streamlit_server_enable_cors: bool

    # Feature Flags
    enable_analytics: bool

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.app_env.lower() == "staging"


def find_env_file() -> Optional[Path]:
    """
    Find .env file by searching from current directory up to repository root.

    Returns:
        Path to .env file if found, None otherwise
    """
    current_dir = Path.cwd()

    # Search up to 5 levels up
    for _ in range(5):
        env_file = current_dir / ".env"
        if env_file.exists():
            return env_file

        # Check if we've reached repository root (contains .git or .specify)
        if (current_dir / ".git").exists() or (current_dir / ".specify").exists():
            env_file = current_dir / ".env"
            if env_file.exists():
                return env_file
            break

        # Move up one directory
        parent = current_dir.parent
        if parent == current_dir:  # Reached filesystem root
            break
        current_dir = parent

    return None


def load_config(env_file: Optional[Path] = None) -> Config:
    """
    Load configuration from environment variables.

    Args:
        env_file: Path to .env file. If None, searches automatically.

    Returns:
        Config object with loaded settings

    Example:
        ```python
        from src.utils.config import load_config

        config = load_config()
        print(f"Database URL: {config.database_url}")
        print(f"Environment: {config.app_env}")
        ```
    """
    # Find and load .env file
    if env_file is None:
        env_file = find_env_file()

    if env_file and env_file.exists():
        load_dotenv(env_file)
        print(f"✓ Loaded environment from: {env_file}")
    else:
        print("⚠ No .env file found, using system environment variables")

    # Load configuration with defaults
    config = Config(
        # Database
        database_url=os.getenv("DATABASE_URL"),

        # Application
        app_env=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),

        # Streamlit
        streamlit_server_port=int(os.getenv("STREAMLIT_SERVER_PORT", "8501")),
        streamlit_server_enable_cors=os.getenv("STREAMLIT_SERVER_ENABLE_CORS", "false").lower() == "true",

        # Feature Flags
        enable_analytics=os.getenv("ENABLE_ANALYTICS", "false").lower() == "true",
    )

    return config


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance (singleton pattern).

    Returns:
        Config: Global configuration object

    Example:
        ```python
        from src.utils.config import get_config

        config = get_config()
        if config.is_development:
            print("Running in development mode")
        ```
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(env_file: Optional[Path] = None) -> Config:
    """
    Reload configuration from environment (useful for testing).

    Args:
        env_file: Path to .env file. If None, searches automatically.

    Returns:
        Config: Reloaded configuration object
    """
    global _config
    _config = load_config(env_file)
    return _config
