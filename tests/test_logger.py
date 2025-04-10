"""
Tests for the Logger class.
"""

import os
import logging
import pytest
from unittest.mock import patch, MagicMock
from src.utils.logger import Logger

class TestLogger:
    """Test the Logger singleton class."""
    
    @pytest.fixture
    def reset_logger(self):
        """Reset the Logger singleton between tests."""
        # Store the original instance
        original_instance = Logger._instance
        Logger._instance = None
        yield
        # Restore the original instance
        Logger._instance = original_instance
    
    @pytest.fixture
    def mock_logging(self):
        """Mock the logging module."""
        with patch('src.utils.logger.logging') as mock_logging:
            mock_logger = MagicMock(spec=logging.Logger)
            mock_logging.getLogger.return_value = mock_logger
            yield mock_logging, mock_logger
    
    @pytest.fixture
    def mock_makedirs(self):
        """Mock os.makedirs to avoid filesystem operations."""
        with patch('os.makedirs') as mock_makedirs, \
             patch('os.path.exists', return_value=False):
            yield mock_makedirs
    
    def test_singleton_instance(self, reset_logger):
        """Test that Logger follows the singleton pattern."""
        # Create first instance
        logger1 = Logger.instance()
        
        # Create second instance
        logger2 = Logger.instance()
        
        # Verify both variables reference the same instance
        assert logger1 is logger2
    
    def test_logger_initialization(self, reset_logger, mock_logging, mock_makedirs):
        """Test Logger initialization and handler setup."""
        mock_logging_module, mock_logger_instance = mock_logging
        
        # Create Logger instance
        logger = Logger.instance()
        
        # Verify logger was created with correct name
        mock_logging_module.getLogger.assert_called_once_with('TennisTracker')
        
        # Verify log level was set
        mock_logger_instance.setLevel.assert_called_once_with(mock_logging_module.DEBUG)
        
        # Verify handlers were created and added
        assert mock_logging_module.FileHandler.call_count == 1
        assert mock_logging_module.StreamHandler.call_count == 1
        assert mock_logger_instance.addHandler.call_count == 2
        
        # Verify log directory creation
        mock_makedirs.assert_called_once_with('logs')
    
    def test_info_method(self, reset_logger, mock_logging):
        """Test the info method."""
        _, mock_logger_instance = mock_logging
        
        # Create Logger instance
        logger = Logger.instance()
        
        # Call info method
        test_message = "Test info message"
        logger.info(test_message)
        
        # Verify info method was called on underlying logger
        mock_logger_instance.info.assert_called_once_with(test_message)
    
    def test_warning_method(self, reset_logger, mock_logging):
        """Test the warning method."""
        _, mock_logger_instance = mock_logging
        
        # Create Logger instance
        logger = Logger.instance()
        
        # Call warning method
        test_message = "Test warning message"
        logger.warning(test_message)
        
        # Verify warning method was called on underlying logger
        mock_logger_instance.warning.assert_called_once_with(test_message)
    
    def test_debug_method(self, reset_logger, mock_logging):
        """Test the debug method with pragma no cover."""
        _, mock_logger_instance = mock_logging
        
        # Create Logger instance with mock
        logger = Logger.instance()
        
        # Call debug method
        test_message = "Test debug message"
        logger.debug(test_message)
        
        # Verify debug method was called on underlying logger
        mock_logger_instance.debug.assert_called_once_with(test_message)
    
    def test_error_method(self, reset_logger, mock_logging):
        """Test the error method with pragma no cover."""
        _, mock_logger_instance = mock_logging
        
        # Create Logger instance
        logger = Logger.instance()
        
        # Call error method
        test_message = "Test error message"
        logger.error(test_message)
        
        # Verify error method was called on underlying logger
        mock_logger_instance.error.assert_called_once_with(test_message)
    
    def test_critical_method(self, reset_logger, mock_logging):
        """Test the critical method with pragma no cover."""
        _, mock_logger_instance = mock_logging
        
        # Create Logger instance
        logger = Logger.instance()
        
        # Call critical method
        test_message = "Test critical message"
        logger.critical(test_message)
        
        # Verify critical method was called on underlying logger
        mock_logger_instance.critical.assert_called_once_with(test_message) 