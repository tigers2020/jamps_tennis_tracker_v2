"""
Logger Module

This module provides a singleton logger for the application.
"""

import logging
import os
import sys
from datetime import datetime

class Logger:
    """
    Singleton logger class for the application
    
    Provides consistent logging across the application with common formatting
    and multiple output options (console, file, etc.)
    """
    
    # Singleton instance
    _instance = None
    
    @classmethod
    def instance(cls):
        """
        Get singleton instance
        
        Returns:
            Logger: Singleton logger instance
        """
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance
    
    def __init__(self, console_level=logging.DEBUG, file_level=logging.DEBUG):
        """
        Initialize the logger
        
        Args:
            console_level: Console logging level (default: INFO)
            file_level: File logging level (default: DEBUG)
        """
        if Logger._instance is not None:
            raise Exception("Logger is a singleton - use Logger.instance() instead")
            
        # Create logger with name 'tennis_tracker'
        self._logger = logging.getLogger('tennis_tracker')
        self._logger.setLevel(logging.DEBUG)  # Capture all logs, filter at handler level
        
        # Avoid duplicate handlers on reload
        if self._logger.hasHandlers():
            self._logger.handlers.clear()
        
        # 재귀 호출 방지를 위한 안전 기능 추가
        self._recursion_guard = False
        
        # Create the logs directory if it doesn't exist
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)
        
        # Configure console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        
        # Create formatters
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        
        # Set formatters for handlers
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        self._logger.addHandler(console_handler)
        
        # File logging disabled
        self.log_filename = None
    
    def debug(self, message):
        """Log a debug message"""
        # 재귀 방지
        if self._recursion_guard:
            return
        try:
            self._recursion_guard = True
            self._logger.debug(message)  # pragma: no cover
        finally:
            self._recursion_guard = False
    
    def info(self, message):
        """Log an info message"""
        # 재귀 방지
        if self._recursion_guard:
            return
        try:
            self._recursion_guard = True
            self._logger.info(message)  # pragma: no cover
        finally:
            self._recursion_guard = False
    
    def warning(self, message):
        """Log a warning message"""
        # 재귀 방지
        if self._recursion_guard:
            return
        try:
            self._recursion_guard = True
            self._logger.warning(message)  # pragma: no cover
        finally:
            self._recursion_guard = False
    
    def error(self, message):
        """Log an error message"""
        # 재귀 방지
        if self._recursion_guard:
            return
        try:
            self._recursion_guard = True
            self._logger.error(message)  # pragma: no cover
        finally:
            self._recursion_guard = False
    
    def critical(self, message):
        """Log a critical message"""
        # 재귀 방지
        if self._recursion_guard:
            return
        try:
            self._recursion_guard = True
            self._logger.critical(message)  # pragma: no cover
        finally:
            self._recursion_guard = False
    
    def get_log_file(self):
        """Get the log file path"""
        return self.log_filename 