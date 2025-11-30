"""Main entry point for Karaoke Duet app."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from common.core import AppConfig, setup_logger
from common.reachy import ReachyWrapper


def main():
    """Run the Karaoke Duet application."""
    logger = setup_logger(__name__)
    logger.info("Starting Karaoke Duet...")
    
    # Load configuration
    config = AppConfig(
        app_name="karaoke-duet",
        app_version="0.1.0",
        media_backend="no_media",
    )
    
    logger.info(f"App: {config.app_name} v{config.app_version}")
    
    # TODO: Implement karaoke app
    logger.warning("Karaoke Duet is not yet fully implemented")
    
    # Example: Connect to robot
    try:
        with ReachyWrapper(
            localhost_only=config.localhost_only,
            use_sim=config.use_sim,
            media_backend=config.media_backend,
            log_level=config.log_level,
        ) as robot:
            logger.info("Connected to Reachy Mini")
            robot.wake_up(duration=2.0)
            
            logger.info("Ready for karaoke! (Implementation pending)")
            
            # TODO: Start web server for lyrics display
            # TODO: Load karaoke song data
            # TODO: Sync robot animations with audio
            
    except Exception as e:
        logger.error(f"Error running Karaoke Duet: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
