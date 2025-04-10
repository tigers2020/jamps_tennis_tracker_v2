"""
Frame Manager Module

This module provides a class for managing frame information
in the Tennis Ball Tracker application.
"""

import os
import json
from src.utils.logger import Logger
from src.utils.file_utils import FileUtils

class FrameManager:
    """
    Manages frame information for the Tennis Ball Tracker
    
    This class handles:
    - Loading frame information from JSON files
    - Extracting frame paths
    - Validating frame data
    """
    
    def __init__(self):
        """Initialize the frame manager"""
        self._frames_info = None
        self._base_path = ""
        self.logger = Logger.instance()
    
    def set_base_path(self, base_path):
        """
        Set the base path for relative paths in frame info
        
        Args:
            base_path: Base directory path
        """
        # Normalize the path to ensure consistent directory separators
        normalized_path = os.path.normpath(base_path)
        self._base_path = normalized_path
        self.logger.info(f"Base path set to: {self._base_path}")
        
        # Verify if the directory exists
        if not os.path.exists(self._base_path):
            self.logger.error(f"Base path does not exist: {self._base_path}")
        elif not os.path.isdir(self._base_path):
            self.logger.error(f"Base path is not a directory: {self._base_path}")
    
    def get_base_path(self):
        """
        Get the base path
        
        Returns:
            str: Base directory path
        """
        return self._base_path
    
    def load_from_json(self, json_file_path):
        """
        Load frame information from a JSON file
        
        Args:
            json_file_path: Path to the frames_info.json file
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info(f"Loading frames from JSON file: {json_file_path}")
        
        # Verify the file exists
        if not os.path.exists(json_file_path):
            self.logger.error(f"JSON file does not exist: {json_file_path}")
            return False
            
        # Load JSON file
        frames_info = FileUtils.load_json_file(json_file_path)
        if not frames_info:
            self.logger.error(f"Failed to load or parse JSON file: {json_file_path}")
            return False
            
        # Set base path to the directory containing the JSON file
        json_dir = os.path.dirname(json_file_path)
        self.logger.info(f"Setting base path to JSON file directory: {json_dir}")
        self.set_base_path(json_dir)
        
        # Validate and store frames info
        if not self.load_frames_info(frames_info):
            self.logger.error("Failed to load frames info from JSON data")
            return False
            
        # Verify if we have frames
        total_frames = self.get_total_frames()
        self.logger.info(f"Loaded {total_frames} frames from JSON file")
        if total_frames <= 0:
            self.logger.error("No frames found in JSON data")
            return False
            
        return True
    
    def load_frames_info(self, frames_info):
        """
        Load frame information from JSON data
        
        Args:
            frames_info: Dictionary containing frame information
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not frames_info or "total_frames" not in frames_info or "frame_info" not in frames_info:
            self.logger.error("Invalid frames_info format")
            return False
        
        # Store frames info
        self._frames_info = frames_info
        return True
    
    def get_frames_info(self):
        """
        Get the current frames info
        
        Returns:
            dict: The frames info or None if not loaded
        """
        return self._frames_info
    
    def get_total_frames(self):
        """
        Get the total number of frames
        
        Returns:
            int: Total number of frames or 0 if no frames info
        """
        if not self._frames_info or "total_frames" not in self._frames_info:
            return 0
            
        return self._frames_info["total_frames"]
    
    def _get_path_key(self, camera):
        """
        Get the key used in frame data based on camera type
        
        Args:
            camera: Camera type ('left' or 'right')
            
        Returns:
            str: The key for the camera path in frame data
        """
        return "left_resize" if camera == "left" else "right_resize"
    
    def _create_full_path(self, relative_path):
        """
        Create a full path from a relative path
        
        Args:
            relative_path: Relative path from base_path
            
        Returns:
            str: Full path
        """
        # Normalize path separators
        normalized_path = relative_path.replace("\\", "/")
        # Join with base path
        return os.path.join(self._base_path, normalized_path)
    
    def _get_paths_from_frames_info(self, camera=None):
        """
        Extract paths from frames info for a specific camera or all cameras
        
        Args:
            camera: Camera type ('left', 'right' or None for all)
        
        Returns:
            list: List of valid frame paths
        """
        if not self._frames_info:
            self.logger.error("_get_paths_from_frames_info: No frames info available")
            return []
        
        valid_paths = []
        
        # If camera is None, get paths for both cameras
        cameras = ["left", "right"] if camera is None else [camera]
        
        for cam in cameras:
            # Determine path key based on camera type
            path_key = self._get_path_key(cam)
            self.logger.debug(f"get_frame_paths: Using path_key={path_key}, base_path={self._base_path}")
            
            for frame_number in range(1, self.get_total_frames() + 1):
                frame_key = str(frame_number)
                if frame_key in self._frames_info["frame_info"]:
                    frame_data = self._frames_info["frame_info"][frame_key]
                    
                    if path_key in frame_data:
                        path = self._create_full_path(frame_data[path_key])
                        
                        if os.path.exists(path):
                            valid_paths.append(path)
                        else:
                            self.logger.warning(f"File not found: {path}")
                    else:
                        self.logger.warning(f"Path key '{path_key}' not found in frame {frame_key}")
                else:
                    self.logger.warning(f"Frame key '{frame_key}' not found in frames_info")
        
        if camera is not None:
            self.logger.info(f"Found {len(valid_paths)} valid {camera} camera frames out of {self.get_total_frames()} total frames")
        else:
            self.logger.info(f"Found {len(valid_paths)} valid camera frames out of {self.get_total_frames()} total frames")
        return valid_paths
    
    def get_frame_paths(self, camera=None):
        """
        Get paths for all frames for a specific camera or all cameras
        
        Args:
            camera: Camera type (if None, get all frames)
        
        Returns:
            list: List of frame paths
        """
        return self._get_paths_from_frames_info(camera=camera)
    
    def get_frame_path(self, frame_number, camera="left"):
        """
        Get the path for a specific frame and camera
        
        Args:
            frame_number: Frame number
            camera: Camera type ('left' or 'right')
            
        Returns:
            str: Path to the frame or None if not found
        """
        if not self._frames_info:
            return None
        
        frame_key = str(frame_number)
        if frame_key not in self._frames_info["frame_info"]:
            return None
        
        frame_data = self._frames_info["frame_info"][frame_key]
        path_key = self._get_path_key(camera)
        
        if path_key in frame_data:
            path = self._create_full_path(frame_data[path_key])
            if os.path.exists(path):
                return path
                
        return None
    
    def is_loaded(self):
        """
        Check if frames information is loaded
        
        Returns:
            bool: True if frames information is loaded, False otherwise
        """
        return self._frames_info is not None and len(self._frames_info) > 0 