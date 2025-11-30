"""Tests for common utilities."""

import pytest

from common.core import AppConfig, setup_logger


def test_setup_logger():
    """Test logger setup."""
    logger = setup_logger("test_logger", level="INFO")
    assert logger is not None
    assert logger.name == "test_logger"


def test_app_config_defaults():
    """Test AppConfig default values."""
    config = AppConfig()
    assert config.app_name == "reachy-mini-app"
    assert config.log_level == "INFO"
    assert config.localhost_only is True


def test_app_config_custom():
    """Test AppConfig with custom values."""
    config = AppConfig(
        app_name="test-app",
        log_level="DEBUG",
        localhost_only=False,
    )
    assert config.app_name == "test-app"
    assert config.log_level == "DEBUG"
    assert config.localhost_only is False


def test_app_config_to_dict():
    """Test AppConfig serialization."""
    config = AppConfig(app_name="test-app")
    config_dict = config.to_dict()
    assert isinstance(config_dict, dict)
    assert config_dict["app_name"] == "test-app"
