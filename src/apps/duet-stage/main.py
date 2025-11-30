"""Main entry point for Duet Stage app."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from common.core import AppConfig, setup_logger
from common.reachy import ReachyWrapper


def main():
    """Run the Duet Stage application."""
    logger = setup_logger(__name__)
    logger.info("Starting Duet Stage...")
    
    # Load configuration
    config = AppConfig(
        app_name="duet-stage",
        app_version="0.1.0",
        media_backend="no_media",
    )
    
    logger.info(f"App: {config.app_name} v{config.app_version}")
    
    # TODO: Implement duet stage app
    logger.warning("Duet Stage is not yet fully implemented")
    logger.info("This app requires TWO Reachy Mini robots")
    
    # TODO: Connect to two robots
    # TODO: Load duet choreography
    # TODO: Synchronize performance between both robots
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
