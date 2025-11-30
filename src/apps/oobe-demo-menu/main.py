"""Main entry point for OOBE Demo Menu."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from common.core import AppConfig, setup_logger


def main():
    """Run the OOBE Demo Menu application."""
    logger = setup_logger(__name__)
    logger.info("Starting OOBE Demo Menu...")
    
    # Load configuration
    config = AppConfig(
        app_name="oobe-demo-menu",
        app_version="0.1.0",
    )
    
    logger.info(f"App: {config.app_name} v{config.app_version}")
    
    # TODO: Implement menu UI
    logger.warning("OOBE Demo Menu is not yet fully implemented")
    logger.info("Available apps:")
    logger.info("  1. Wave Hello - Simple greeting demo")
    logger.info("  2. Dance - Robot dance performance")
    logger.info("  3. Reachy Sings - Robot singing demo")
    logger.info("  4. Karaoke Duet - Sing along with Reachy")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
