"""
Calibration Point I/O
===================

Handle file I/O operations for calibration points.
"""

import os
import json
import logging
from typing import Dict, List, Tuple, Any, Optional, Union
from pathlib import Path

from src.utils.math.vector import Vector2D
from src.utils.settings_manager import SettingsManager


class CalibrationPointIO:
    """
    Handles file I/O operations for calibration points.
    
    This class provides methods for saving, loading, and managing
    calibration point data for both left and right cameras.
    """
    
    # Define standard resolutions
    STANDARD_RESOLUTIONS = {
        "1080p": (1920, 1080),  # Full HD
        "480p": (854, 480),     # SD
        "280p": (497, 280)      # Low resolution
    }
    
    # Default calibration resolution
    DEFAULT_RESOLUTION = "1080p"
    
    def __init__(self, total_points: int = 12):
        """Initialize the point I/O manager"""
        # Logger setup
        self.logger = logging.getLogger(__name__)
        self.total_points = total_points
        
        # Get settings manager
        self.settings = SettingsManager.instance()
        
        # Get or initialize calibration directory and file paths
        self._initialize_paths()
        
    def _initialize_paths(self):
        """Initialize default paths for calibration files"""
        # Get paths from settings or create defaults
        calibration_dir = self.settings.get("calibration_points_dir", "")
        calibration_file = self.settings.get("calibration_points_file", "")
        
        # If paths not set in settings, create default paths
        if not calibration_dir:
            # Default: [User Home]/.tennis_tracker/calibration
            calibration_dir = os.path.join(
                Path.home(), 
                ".tennis_tracker", 
                "calibration"
            )
            self.settings.set("calibration_points_dir", calibration_dir)
            
        if not calibration_file:
            # Default: [calibration_dir]/court_key_points.json
            calibration_file = os.path.join(
                calibration_dir, 
                "court_key_points.json"
            )
            self.settings.set("calibration_points_file", calibration_file)
        
        # Set instance variables
        self.base_dir = calibration_dir
        self.default_file = calibration_file
    
    def save_points(self, left_points: List[Union[Vector2D, Tuple[int, int]]], 
                   right_points: List[Union[Vector2D, Tuple[int, int]]], 
                   filepath: Optional[str] = None, 
                   resolution: str = DEFAULT_RESOLUTION,
                   silent: bool = False) -> Tuple[bool, str]:
        """
        Save calibration points to a JSON file.
        
        Args:
            left_points: List of Vector2D objects or (x, y) coordinate tuples for left camera
            right_points: List of Vector2D objects or (x, y) coordinate tuples for right camera
            filepath: Optional custom filepath (defaults to standard location)
            resolution: Resolution name used for calibration (default: 1080p)
            silent: If True, no logging occurs
            
        Returns:
            (success, message) tuple
        """
        # Skip if both point sets are incomplete
        left_complete = len(left_points) == self.total_points
        right_complete = len(right_points) == self.total_points
        
        if not left_complete and not right_complete:
            return False, "No complete point sets to save"
        
        # Determine save location
        save_path = filepath or self.default_file
        
        # Get resolution dimensions
        if resolution in self.STANDARD_RESOLUTIONS:
            width, height = self.STANDARD_RESOLUTIONS[resolution]
        else:
            # Default to 1080p if unknown resolution
            self.logger.warning(f"Unknown resolution: {resolution}, using 1080p")
            width, height = self.STANDARD_RESOLUTIONS[self.DEFAULT_RESOLUTION]
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Convert Vector2D objects to dictionaries with normalized coordinates
        def point_to_normalized_dict(p):
            if isinstance(p, Vector2D):
                # Normalize coordinates (convert to 0-1 range)
                norm_x, norm_y = p.to_normalized(width, height)
                return {'x': norm_x, 'y': norm_y}
            else:
                # Handle tuple input (less common)
                norm_x, norm_y = p[0] / width, p[1] / height
                return {'x': norm_x, 'y': norm_y}
        
        # Prepare data with resolution information
        data = {
            "resolution": {
                "name": resolution,
                "width": width,
                "height": height
            },
            "left_camera": [point_to_normalized_dict(p) for p in left_points] if left_complete else [],
            "right_camera": [point_to_normalized_dict(p) for p in right_points] if right_complete else []
        }
        
        # Save to file
        try:
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            # Update settings if using a custom path
            if filepath and filepath != self.default_file:
                self.settings.set("calibration_points_file", filepath)
                
            # Log success
            if not silent:
                self.logger.info(f"Saved calibration points to: {save_path} (resolution: {resolution})")
                
            return True, save_path
            
        except Exception as e:
            error_msg = f"Failed to save calibration points: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def load_points(self, filepath: Optional[str] = None, 
                   target_resolution: Optional[str] = None,
                   exact_dimensions: Optional[Tuple[int, int]] = None) -> Tuple[bool, Dict[str, List[Vector2D]], str]:
        """
        Load calibration points from a JSON file.
        
        Args:
            filepath: Optional custom filepath (defaults to standard location)
            target_resolution: Target resolution to scale points to (defaults to original)
            exact_dimensions: Optional tuple (width, height) for exact scaling to specific dimensions
            
        Returns:
            (success, points_dict, message) tuple
            points_dict contains 'left_camera' and 'right_camera' keys with lists of Vector2D points
        """
        # Initialize return value
        result = {
            "left_camera": [],
            "right_camera": []
        }
        
        # Determine load location
        load_path = filepath or self.default_file
        
        # If file doesn't exist, return empty points
        if not os.path.exists(load_path):
            return True, result, "No saved points found"
        
        try:
            with open(load_path, 'r') as f:
                data = json.load(f)
            
            # Get resolution information
            resolution_info = data.get("resolution", {})
            src_resolution_name = resolution_info.get("name", self.DEFAULT_RESOLUTION)
            src_width = resolution_info.get("width", self.STANDARD_RESOLUTIONS[self.DEFAULT_RESOLUTION][0])
            src_height = resolution_info.get("height", self.STANDARD_RESOLUTIONS[self.DEFAULT_RESOLUTION][1])
            
            # Determine target resolution
            if exact_dimensions:
                # Use exact dimensions if provided
                dst_width, dst_height = exact_dimensions
                scaling_needed = (src_width != dst_width or src_height != dst_height)
                resolution_name = f"custom_{dst_width}x{dst_height}"
                self.logger.info(f"Scaling to exact dimensions: {dst_width}x{dst_height}")
            elif target_resolution and target_resolution in self.STANDARD_RESOLUTIONS:
                dst_width, dst_height = self.STANDARD_RESOLUTIONS[target_resolution]
                scaling_needed = (src_width != dst_width or src_height != dst_height)
                resolution_name = target_resolution
            else:
                # Use original resolution if no target specified
                dst_width, dst_height = src_width, src_height
                scaling_needed = False
                resolution_name = src_resolution_name
            
            # Extract left camera points and convert to Vector2D
            left_points = data.get("left_camera", [])
            if left_points and len(left_points) == self.total_points:
                # Convert normalized coordinates to pixel coordinates
                result["left_camera"] = [
                    Vector2D.from_normalized(p['x'], p['y'], dst_width, dst_height) 
                    for p in left_points
                ]
            
            # Extract right camera points and convert to Vector2D
            right_points = data.get("right_camera", [])
            if right_points and len(right_points) == self.total_points:
                # Convert normalized coordinates to pixel coordinates
                result["right_camera"] = [
                    Vector2D.from_normalized(p['x'], p['y'], dst_width, dst_height) 
                    for p in right_points
                ]
            
            # Update settings if using a custom path and successful
            if filepath and filepath != self.default_file:
                self.settings.set("calibration_points_file", filepath)
            
            # Log success
            if scaling_needed:
                self.logger.info(
                    f"Loaded and scaled calibration points from {src_resolution_name} "
                    f"({src_width}x{src_height}) to {resolution_name} ({dst_width}x{dst_height})"
                )
            else:
                self.logger.info(f"Loaded calibration points from: {load_path} ({resolution_name})")
            
            # Generate success message
            has_left = len(result["left_camera"]) == self.total_points
            has_right = len(result["right_camera"]) == self.total_points
            
            if has_left and has_right:
                message = f"Loaded points for both cameras ({resolution_name})"
            elif has_left:
                message = f"Loaded points for left camera only ({resolution_name})"
            elif has_right:
                message = f"Loaded points for right camera only ({resolution_name})"
            else:
                message = "No valid points found in file"
                
            return True, result, message
            
        except Exception as e:
            error_msg = f"Failed to load calibration points: {str(e)}"
            self.logger.error(error_msg)
            return False, result, error_msg 