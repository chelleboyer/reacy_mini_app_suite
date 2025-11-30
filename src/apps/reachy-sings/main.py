"""Main entry point for Reachy Sings app."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from common.core import AppConfig, setup_logger
from common.reachy import ReachyWrapper


def main():
    """Run the Reachy Sings application."""
    logger = setup_logger(__name__)
    logger.info("Starting Reachy Sings...")
    
    # Load configuration
    config = AppConfig(
        app_name="reachy-sings",
        app_version="0.1.0",
        media_backend="no_media",  # We'll handle audio separately
    )
    
    logger.info(f"App: {config.app_name} v{config.app_version}")
    
    # TODO: Implement singing app
    logger.warning("Reachy Sings is not yet fully implemented")
    
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
            
            logger.info("Ready to sing! (Implementation pending)")
            
            # TODO: Load song data from HF
            # TODO: Play audio
            # TODO: Animate robot with singing motions
            
    except Exception as e:
        logger.error(f"Error running Reachy Sings: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
