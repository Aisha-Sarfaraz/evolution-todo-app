"""
Main application entry point for Todo CLI.

Implements:
- Dependency injection (MemoryRepository)
- Logging configuration (JSON structured format)
- Global exception handling
- Application lifecycle

Usage:
    python -m src.main
    OR
    python src/main.py
"""

import logging
import os
import sys
from pathlib import Path

# Add Phase-1 directory to Python path to support both execution methods
# This allows: python src/main.py AND python -m src.main
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

from src.cli.menu import display_menu
from src.storage.memory_repository import MemoryRepository


def configure_logging() -> None:
    """
    Configure JSON structured logging.

    Log Format:
        {
            "timestamp": "ISO8601",
            "level": "INFO",
            "service": "todo-cli",
            "message": "...",
            "context": {...}
        }

    Log Level:
        - Environment variable: LOG_LEVEL (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - Default: INFO

    Implementation Note:
        Phase I uses simple Python logging module.
        Phase II will use python-json-logger for proper JSON formatting.
    """
    # Get log level from environment or default to INFO
    log_level_str = os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"service": "todo-cli", "message": "%(message)s"}'
        ),
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # Log application startup
    logger = logging.getLogger(__name__)
    logger.info("Todo Application starting...")


def main() -> None:
    """
    Main application entry point.

    Workflow:
    1. Configure logging (JSON structured format)
    2. Initialize MemoryRepository (dependency injection)
    3. Call display_menu (main menu loop)
    4. Handle global exceptions gracefully

    Dependency Injection:
        Phase I: repository = MemoryRepository()
        Phase II: repository = PostgresRepository()  (one-line swap)

    Exit Codes:
        0: Normal exit
        1: Critical error (logged)
    """
    try:
        # Configure UTF-8 encoding for Windows console (fixes Unicode character display)
        # Skip during pytest to preserve capsys functionality
        if sys.platform == "win32" and "pytest" not in sys.modules:
            import io

            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

        # Configure logging
        configure_logging()
        logger = logging.getLogger(__name__)

        # Initialize repository (dependency injection)
        logger.info("Initializing MemoryRepository...")
        repository = MemoryRepository()

        # Display main menu (blocks until user exits)
        logger.info("Starting main menu...")
        display_menu(repository)

        # Normal exit
        logger.info("Todo Application exited normally")
        sys.exit(0)

    except KeyboardInterrupt:
        # User pressed Ctrl+C at global level
        print("\n\nExiting Todo Application. Goodbye!\n")
        logging.info("Application interrupted by user (Ctrl+C)")
        sys.exit(0)

    except Exception as e:
        # Log critical error
        logging.critical(f"Unexpected error occurred: {e}", exc_info=True)

        # Display user-friendly message (no stack trace)
        print("\n✗ An unexpected error occurred. Please check the logs.\n")
        print("Exiting application...\n")

        sys.exit(1)


if __name__ == "__main__":
    main()
