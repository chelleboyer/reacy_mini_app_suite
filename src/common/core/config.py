"""Configuration management for Reachy Mini apps."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AppConfig:
    """Base configuration for Reachy Mini apps.
    
    This provides common configuration options that can be extended
    by individual apps.
    """
    
    # App identification
    app_name: str = "reachy-mini-app"
    app_version: str = "0.1.0"
    
    # Logging
    log_level: str = "INFO"
    
    # Reachy connection
    localhost_only: bool = True
    spawn_daemon: bool = False
    use_sim: bool = False
    connection_timeout: float = 5.0
    
    # Media
    media_backend: str = "default"  # "default", "gstreamer", or "no_media"
    
    # Runtime options
    debug_mode: bool = False
    
    # Custom app-specific config
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, config_path: Path) -> "AppConfig":
        """Load configuration from a JSON file.
        
        Args:
            config_path: Path to JSON configuration file
            
        Returns:
            AppConfig instance with loaded values
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, "r") as f:
            data = json.load(f)
        
        return cls(**data)
    
    @classmethod
    def from_env(cls, prefix: str = "REACHY_") -> "AppConfig":
        """Load configuration from environment variables.
        
        Args:
            prefix: Prefix for environment variables (default: "REACHY_")
            
        Returns:
            AppConfig instance with values from environment
        """
        config = cls()
        
        # Map environment variables to config fields
        env_mapping = {
            f"{prefix}APP_NAME": "app_name",
            f"{prefix}LOG_LEVEL": "log_level",
            f"{prefix}LOCALHOST_ONLY": "localhost_only",
            f"{prefix}SPAWN_DAEMON": "spawn_daemon",
            f"{prefix}USE_SIM": "use_sim",
            f"{prefix}MEDIA_BACKEND": "media_backend",
            f"{prefix}DEBUG_MODE": "debug_mode",
        }
        
        for env_var, field_name in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if field_name in ["localhost_only", "spawn_daemon", "use_sim", "debug_mode"]:
                    value = value.lower() in ("true", "1", "yes")
                elif field_name == "connection_timeout":
                    value = float(value)
                
                setattr(config, field_name, value)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.
        
        Returns:
            Dictionary representation of config
        """
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "log_level": self.log_level,
            "localhost_only": self.localhost_only,
            "spawn_daemon": self.spawn_daemon,
            "use_sim": self.use_sim,
            "connection_timeout": self.connection_timeout,
            "media_backend": self.media_backend,
            "debug_mode": self.debug_mode,
            "custom_config": self.custom_config,
        }
    
    def save(self, config_path: Path) -> None:
        """Save configuration to a JSON file.
        
        Args:
            config_path: Path where to save the configuration
        """
        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
