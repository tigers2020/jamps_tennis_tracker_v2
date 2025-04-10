"""
Settings Manager Module

This module provides a singleton class for managing application settings.
The SettingsManager class uses a JSON file to persist settings across application restarts.
"""

import os
import json
from PySide6.QtCore import QObject, Signal, QSize, QPoint
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TypeVar, cast

from src.models.singleton import qt_singleton
from src.utils.logger import Logger

# Type definitions for better type checking
SettingValue = TypeVar('SettingValue', str, int, float, bool, list, dict)
SettingsDict = Dict[str, Any]

@qt_singleton
class SettingsManager:
    """
    Singleton class that manages application settings
    
    This class provides the following features:
    - Saving settings
    - Loading settings
    - Managing default values
    - Validating settings
    """
    
    # Default settings definitions
    DEFAULT_SETTINGS: SettingsDict = {
        "last_file_path": "",          # Last opened file path
        "last_folder_path": "",        # Last opened folder path
        "playback_speed": 1000,        # Playback speed (fps)
        "window_size": [1280, 720],    # Window size
        "window_position": [100, 100], # Window position
        "autoplay": False,             # Auto-play when loading images
        "loop_playback": True,         # Loop playback
        "data_directory": "",          # Default data directory
        "auto_save_results": False,    # Auto-save analysis results
        "fpga_com_port": "",           # Default FPGA COM port
        "fpga_baud_rate": 115200,      # Default FPGA baud rate
        "fpga_data_bits": 8,           # Default FPGA data bits
        "fpga_auto_connect": False,    # Auto-connect to FPGA on startup
        "calibration_points_dir": "",  # Directory for calibration points files
        "calibration_points_file": "", # Default calibration points file
    }
    
    # Settings validation constraints
    SETTINGS_CONSTRAINTS = {
        "playback_speed": {"min": 1, "max": 10000},
        "window_size": {"min_width": 640, "min_height": 480},
    }
    
    def __init__(self) -> None:
        """Initialize settings manager"""
        self.logger = Logger.instance()
        
        # Create settings file path (in user's home directory)
        self.settings_dir = Path.home() / ".tennis_tracker"
        self.settings_file = self.settings_dir / "settings.json"
        
        # Initialize settings with default values
        self.settings: SettingsDict = self._get_default_settings()
        
        # Track if directory existence was checked
        self._directory_checked = False
        
        # Initialize settings
        self._initialize_settings()
    
    def _get_default_settings(self) -> SettingsDict:
        """
        Get a copy of the default settings
        
        Returns:
            SettingsDict: Copy of default settings
        """
        return self.DEFAULT_SETTINGS.copy()
    
    def _initialize_settings(self) -> None:
        """Initialize settings directory and load settings file"""
        self._ensure_settings_directory_exists()
        
        # Load settings file
        if not self.load_settings():
            # Save default settings if settings file doesn't exist
            self.save_settings()
            self.logger.info("Created default settings file.")
    
    def _ensure_settings_directory_exists(self) -> bool:
        """
        Ensure settings directory exists
        
        Returns:
            bool: True if directory exists or was created successfully, False otherwise
        """
        # Check if directory existence was already verified
        if self._directory_checked:
            return True
            
        # Mark as checked
        self._directory_checked = True
            
        if self.settings_dir.exists():
            return True
            
        try:
            self.settings_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created settings directory: {self.settings_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create settings directory: {e}")
            return False
    
    def save_settings(self) -> bool:
        """
        Save current settings to file
        
        Returns:
            bool: True if settings were saved successfully, False otherwise
        """
        # Ensure settings directory exists
        if not self._ensure_settings_directory_exists():
            return False
                
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as file:
                json.dump(self.settings, file, indent=4)
            self.logger.info(f"Settings saved: {self.settings_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            return False
    
    def load_settings(self) -> bool:
        """
        Load settings from file
        
        Returns:
            bool: True if settings were loaded successfully, False otherwise
        """
        if not self.settings_file.exists():
            self.logger.warning(f"Settings file not found. Using defaults.")
            return False
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as file:
                loaded_settings = json.load(file)
                
                # Override playback_speed to force 1000 fps
                if "playback_speed" in loaded_settings and loaded_settings["playback_speed"] != 1000:
                    self.logger.info(f"Forcing playback_speed to 1000 fps (was {loaded_settings['playback_speed']})")
                    loaded_settings["playback_speed"] = 1000
                
                # Verify and merge loaded settings into current settings
                self._merge_settings(loaded_settings)
                
            self.logger.info(f"Settings loaded: {self.settings_file}")
            
            # Force save to ensure the speed change is stored permanently
            if "playback_speed" in loaded_settings:
                self.save_settings()
                
            return True
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse settings file: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            return False
    
    def _merge_settings(self, loaded_settings: Dict[str, Any]) -> None:
        """
        Merge loaded settings with current settings, validating values
        
        Args:
            loaded_settings: Settings loaded from file
        """
        for key, value in loaded_settings.items():
            if self._validate_setting(key, value):
                self.settings[key] = value
            else:
                self.logger.warning(f"Invalid setting value: {key}={value}, using default")
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        """
        Validate a setting value against constraints
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            bool: True if value is valid, False otherwise
        """
        # Skip validation for unknown settings
        if key not in self.DEFAULT_SETTINGS and key not in self.SETTINGS_CONSTRAINTS:
            return True
            
        # Validate based on constraints
        if key == "playback_speed":
            return isinstance(value, int) and value >= self.SETTINGS_CONSTRAINTS[key]["min"] and value <= self.SETTINGS_CONSTRAINTS[key]["max"]
        elif key == "window_size":
            return (isinstance(value, list) and len(value) == 2 and 
                    isinstance(value[0], int) and isinstance(value[1], int) and
                    value[0] >= self.SETTINGS_CONSTRAINTS[key]["min_width"] and
                    value[1] >= self.SETTINGS_CONSTRAINTS[key]["min_height"])
        
        # Default validation based on type
        if key in self.DEFAULT_SETTINGS:
            return isinstance(value, type(self.DEFAULT_SETTINGS[key]))
            
        return True
    
    def get(self, key: str, default: Optional[SettingValue] = None) -> Any:
        """
        Return specific setting value
        
        Args:
            key: The setting key to retrieve
            default: Default value to return if key doesn't exist
            
        Returns:
            The setting value or default if not found
        """
        if default is None and key in self.DEFAULT_SETTINGS:
            default = self.DEFAULT_SETTINGS[key]
            
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Change setting value and save
        
        Args:
            key: The setting key to change
            value: The new value for the setting
            
        Returns:
            bool: True if the setting was saved successfully, False otherwise
        """
        # Check if value changed
        if key in self.settings and self.settings[key] == value:
            return True
         
        # Validate the value
        if not self._validate_setting(key, value):
            self.logger.warning(f"Invalid setting value: {key}={value}")
            return False
            
        self.settings[key] = value
        self.logger.info(f"Setting updated: {key}={value}")
        return self.save_settings()
    
    def update_last_file_path(self, path: str) -> bool:
        """
        Update last opened file path
        
        Args:
            path: The file path to save
            
        Returns:
            bool: True if the setting was saved successfully, False otherwise
        """
        if not path or not os.path.exists(path):
            self.logger.warning(f"Invalid file path: {path}")
            return False
            
        return self.set("last_file_path", path)
    
    def update_playback_speed(self, speed_fps: int) -> bool:
        """
        Update playback speed setting
        
        Args:
            speed_fps: Playback speed in frames per second
            
        Returns:
            bool: True if the setting was saved successfully, False otherwise
        """
        if speed_fps <= 0:
            self.logger.warning(f"Invalid playback speed: {speed_fps}")
            return False
            
        return self.set("playback_speed", speed_fps)
    
    def update_window_geometry(self, size: QSize, position: QPoint) -> bool:
        """
        Update window size and position
        
        Args:
            size: Window size
            position: Window position
            
        Returns:
            bool: True if the settings were saved successfully, False otherwise
        """
        # Validate window size
        min_width = self.SETTINGS_CONSTRAINTS["window_size"]["min_width"]
        min_height = self.SETTINGS_CONSTRAINTS["window_size"]["min_height"]
        
        if size.width() < min_width or size.height() < min_height:
            self.logger.warning(f"Window size too small: {size.width()}x{size.height()}")
            return False
            
        self.settings["window_size"] = [size.width(), size.height()]
        self.settings["window_position"] = [position.x(), position.y()]
        return self.save_settings()
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all settings to default values
        
        Returns:
            bool: True if the settings were reset successfully, False otherwise
        """
        self.settings = self._get_default_settings()
        self.logger.info("Settings reset to defaults")  # pragma: no cover
        return self.save_settings()
    
    # Convenience getters for common settings
    def get_last_file_path(self) -> str:
        """Get the last opened file path"""
        return cast(str, self.get("last_file_path"))
    
    def get_playback_speed(self) -> int:
        """Get the playback speed in frames per second"""
        return cast(int, self.get("playback_speed"))
    
    def get_window_size(self) -> List[int]:
        """Get the window size as [width, height]"""
        return cast(List[int], self.get("window_size"))
    
    def get_window_position(self) -> List[int]:
        """Get the window position as [x, y]"""
        return cast(List[int], self.get("window_position"))
    
    def get_last_folder_path(self) -> str:
        """Get the last opened folder path"""
        return cast(str, self.get("last_folder_path"))
    
    def update_last_folder_path(self, path: str) -> bool:
        """
        Update last opened folder path
        
        Args:
            path: The folder path to save
            
        Returns:
            bool: True if the setting was saved successfully, False otherwise
        """
        if not path or not os.path.exists(path):
            self.logger.warning(f"Invalid folder path: {path}")
            return False
            
        return self.set("last_folder_path", path)
        
    def get_app_data_dir(self) -> Path:
        """
        Get the application data directory (same as settings directory)
        
        Returns:
            Path: The application data directory path
        """
        self._ensure_settings_directory_exists()
        return self.settings_dir 