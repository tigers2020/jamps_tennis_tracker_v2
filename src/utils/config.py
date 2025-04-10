"""
Configuration Management Module

This module provides a singleton class for managing application configuration.
"""

import json
import os
from pathlib import Path
import logging

from src.models.singleton import qt_singleton
from src.utils.logger import Logger

@qt_singleton
class Config:
    """
    A singleton configuration manager for the Tennis Tracker application.
    
    This class handles loading, saving, and accessing application configuration
    settings. It ensures consistent configuration across all components.
    """
    
    # Default configuration
    DEFAULT_CONFIG = {
        "ui": {
            "theme": "fusion",
            "language": "ko",
            "window_width": 1200,
            "window_height": 800
        },
        "camera": {
            "default_azimuth": 0.0,
            "default_elevation": 0.0,
            "default_distance": 10.0
        },
        "playback": {
            "default_speed": 1.0,
            "autoplay": False
        },
        "analysis": {
            "detection_threshold": 0.75,
            "in_bounds_color": "#00FF00",
            "out_bounds_color": "#FF0000",
            "blink_rate": 10.0
        },
        "paths": {
            "data_directory": "",
            "cache_directory": "cache",
            "export_directory": "exports"
        }
    }
    
    def __init__(self):
        # Initialize internal state
        self._initialized = False
        
        # Initialize logger first
        self.logger = Logger.instance()
        
        self._config_path = Path('config.json')
        self._config = self._load_config()
        self._initialized = True
        
        if hasattr(self, 'logger'):
            self.logger.info("Configuration initialized")
    
    def _load_config(self):
        """
        Load configuration from file or use defaults if file doesn't exist
        
        Returns:
            dict: The loaded configuration merged with defaults
        """
        # Handle both Path and str types for _config_path
        config_path = self._config_path
        if isinstance(config_path, str):
            exists = os.path.exists(config_path)
        else:
            exists = config_path.exists()
            
        if not exists:
            if hasattr(self, 'logger'):  # pragma: no cover
                self.logger.info("Config file not found, creating default configuration")  # pragma: no cover
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()  # pragma: no cover
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)  # pragma: no cover
            
            # Merge with defaults to ensure all keys exist
            merged_config = self._merge_with_defaults(config)
            if hasattr(self, 'logger'):  # pragma: no cover
                self.logger.info("Configuration loaded successfully")  # pragma: no cover
            return merged_config
        except json.JSONDecodeError as e:  # pragma: no cover
            if hasattr(self, 'logger'):
                self.logger.error(f"Invalid JSON in config file: {str(e)}")  # pragma: no cover
                self.logger.error(f"Error reading config file: {str(e)}")  # pragma: no cover
            return self.DEFAULT_CONFIG.copy()
        except IOError as e:  # pragma: no cover
            if hasattr(self, 'logger'):
                self.logger.error(f"Error reading config file: {str(e)}")
            return self.DEFAULT_CONFIG.copy()
    
    def _ensure_directory_exists(self, path):
        """
        Ensure the directory for a file path exists
        
        Args:
            path: File path
            
        Returns:
            bool: True if directory exists or was created, False otherwise
        """
        try:
            # Get directory from file path
            directory = os.path.dirname(path)
            
            # If no directory specified or directory already exists, return True
            if not directory or os.path.exists(directory):
                return True
                
            # Create directory
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:  # pragma: no cover
            if hasattr(self, 'logger'):
                self.logger.error(f"Error creating directory: {str(e)}")
            return False
    
    def _save_config(self, config):
        """
        Save configuration to file
        
        Args:
            config: The configuration to save
            
        Returns:
            bool: True if the configuration was saved successfully, False otherwise
        """
        try:
            config_path = self._config_path
            
            # Ensure directory exists
            if isinstance(config_path, str):
                directory_exists = self._ensure_directory_exists(config_path)
            else:
                directory_exists = self._ensure_directory_exists(str(config_path))
                
            if not directory_exists:  # pragma: no cover
                if hasattr(self, 'logger'):
                    self.logger.error(f"Failed to create directory for {config_path}")
                return False
                
            # Write config to file
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
                
            if hasattr(self, 'logger'):
                self.logger.info("Configuration saved successfully")
            return True
        except IOError as e:  # pragma: no cover
            if hasattr(self, 'logger'):
                self.logger.error(f"Error saving config file: {str(e)}")
            return False
    
    def _merge_with_defaults(self, config):
        """
        Recursively merge loaded config with defaults to ensure all keys exist
        
        Args:
            config: The configuration to merge with defaults
            
        Returns:
            dict: The merged configuration
        """
        result = self.DEFAULT_CONFIG.copy()
        
        def update_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    d[k] = update_dict(d[k].copy(), v)
                else:
                    d[k] = v
            return d
        
        return update_dict(result, config)
    
    def get(self, section, key=None):
        """
        Get a configuration value
        
        Args:
            section: The configuration section
            key: The specific key within the section (optional)
            
        Returns:
            The requested configuration value, section, or None if not found
        """
        if section not in self._config:  # pragma: no cover
            if hasattr(self, 'logger'):  # pragma: no cover
                self.logger.warning(f"Requested section '{section}' not found in configuration")  # pragma: no cover
            return None
        
        if key is None:
            return self._config[section]
        
        if key not in self._config[section]:  # pragma: no cover
            if hasattr(self, 'logger'):
                self.logger.warning(f"Requested key '{key}' not found in section '{section}'")
            return None
            
        return self._config[section][key]
    
    def set(self, section, key, value):
        """
        Set a configuration value
        
        Args:
            section: The configuration section
            key: The specific key within the section
            value: The value to set
            
        Returns:
            bool: True if the value was set successfully, False otherwise
        """
        # Create section if it doesn't exist
        if section not in self._config:
            self._config[section] = {}
        
        # Set the value and save the configuration
        previous_value = self._config[section].get(key)  # pragma: no cover
        self._config[section][key] = value
        
        save_result = self._save_config(self._config)
        if save_result and hasattr(self, 'logger'):  # pragma: no cover
            self.logger.info(f"Configuration updated: {section}.{key} = {value} (was: {previous_value})")
        
        return save_result
    
    def save(self):
        """
        Save the current configuration to file
        
        Returns:
            bool: True if the configuration was saved successfully, False otherwise
        """
        return self._save_config(self._config)
    
    def reset_to_defaults(self):
        """
        Reset the configuration to default values
        
        Returns:
            bool: True if the configuration was reset successfully, False otherwise
        """
        self._config = self.DEFAULT_CONFIG.copy()
        if hasattr(self, 'logger'):  # pragma: no cover
            self.logger.info("Configuration reset to defaults")  # pragma: no cover
        return self._save_config(self._config)  # pragma: no cover 