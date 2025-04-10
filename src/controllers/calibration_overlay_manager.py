"""
Calibration Overlay Manager Module

This module provides functionality for managing calibration point overlays
on camera views in the Tennis Ball Tracker system.
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap

from src.models.calibration.point_io import CalibrationPointIO
from src.utils.image.image_utils import draw_calibration_points
from src.utils.math.vector import Vector2D
from src.utils.logger import Logger


class CalibrationOverlayManager(QObject):
    """
    Manager for calibration point overlays.
    
    This class handles:
    - Loading calibration points from files
    - Converting normalized points to actual pixel coordinates
    - Drawing calibration points on camera view overlays
    - Caching overlay images for better performance
    """
    
    # Signal emitted when overlay is updated
    overlay_updated = Signal(str)  # Camera type
    
    def __init__(self, num_points=12):
        """
        Initialize the calibration overlay manager.
        
        Args:
            num_points: Number of calibration points (default: 12)
        """
        super(CalibrationOverlayManager, self).__init__()
        
        # Get logger instance
        self.logger = Logger.instance()
        
        # Initialize point I/O helper
        self.point_io = CalibrationPointIO(num_points)
        
        # Storage for normalized and actual coordinates
        self.normalized_points = {"left_camera": [], "right_camera": []}
        self.calibration_points = {"left_camera": [], "right_camera": []}
        
        # Cache for overlay pixmaps
        self._overlay_cache = {"left_camera": None, "right_camera": None}
        self._last_drawn_frame = {"left_camera": -1, "right_camera": -1}
        
        # Load calibration points
        self._load_calibration_points()
    
    def _load_calibration_points(self):
        """Load normalized calibration points from saved file"""
        try:
            # Load points without scaling (we'll scale dynamically later)
            success, _, message = self.point_io.load_points()
            
            if success:
                # Get the raw normalized points from the file
                with open(self.point_io.default_file, 'r') as f:
                    import json
                    data = json.load(f)
                
                # Store normalized coordinates (0-1 range)
                left_points = data.get("left_camera", [])
                right_points = data.get("right_camera", [])
                
                if left_points:
                    self.normalized_points["left_camera"] = left_points
                    self.logger.info(f"Loaded {len(left_points)} normalized left camera points")
                
                if right_points:
                    self.normalized_points["right_camera"] = right_points
                    self.logger.info(f"Loaded {len(right_points)} normalized right camera points")
                    
                # Emit signals for both cameras
                self.overlay_updated.emit("left_camera")
                self.overlay_updated.emit("right_camera")
            else:
                self.logger.warning(f"Failed to load calibration points: {message}")
                
        except Exception as e:
            self.logger.error(f"Error loading calibration points: {str(e)}")
    
    def has_calibration_points(self, camera_type):
        """
        Check if calibration points exist for the specified camera.
        
        Args:
            camera_type: Camera type ("left_camera" or "right_camera")
            
        Returns:
            bool: True if calibration points exist, False otherwise
        """
        return bool(self.normalized_points.get(camera_type, []))
    
    def create_overlay(self, camera_type, pixmap, frame_number):
        """
        Create an overlay with calibration points for the specified camera.
        
        Args:
            camera_type: Camera type ("left_camera" or "right_camera")
            pixmap: Base image pixmap
            frame_number: Current frame number for caching
            
        Returns:
            QPixmap: Pixmap with calibration points drawn, or None if error
        """
        # Check if we need to draw or can use cache
        if (self._overlay_cache[camera_type] is not None and 
            self._last_drawn_frame[camera_type] == frame_number):
            return self._overlay_cache[camera_type]
        
        # Check if we have points to draw
        if not self.normalized_points.get(camera_type, []):
            return pixmap
        
        try:
            # Create a copy of the pixmap for drawing
            overlay_pixmap = QPixmap(pixmap)
            
            # Calculate actual pixel coordinates based on image dimensions
            img_width, img_height = pixmap.width(), pixmap.height()
            scaled_points = []
            
            for point in self.normalized_points[camera_type]:
                # Denormalize coordinates to match image dimensions
                x = point["x"] * img_width
                y = point["y"] * img_height
                scaled_points.append(Vector2D(x, y))
            
            # Store the current pixel coordinates
            self.calibration_points[camera_type] = scaled_points
            
            # Draw points on the overlay
            draw_calibration_points(
                overlay_pixmap,
                scaled_points,
                -1,  # No selected point
                len(scaled_points),
                is_monitoring_view=False
            )
            
            # Cache the overlay and update frame number
            self._overlay_cache[camera_type] = overlay_pixmap
            self._last_drawn_frame[camera_type] = frame_number
            
            return overlay_pixmap
            
        except Exception as e:
            self.logger.error(f"Error creating overlay for {camera_type}: {str(e)}")
            return pixmap
    
    def get_calibration_points(self, camera_type):
        """
        Get the calibration points for the specified camera.
        
        Args:
            camera_type: Camera type ("left_camera" or "right_camera")
            
        Returns:
            list: List of Vector2D points
        """
        return self.calibration_points.get(camera_type, [])
    
    def clear_cache(self):
        """Clear the overlay cache to force redraw"""
        self._overlay_cache = {"left_camera": None, "right_camera": None}
        self._last_drawn_frame = {"left_camera": -1, "right_camera": -1} 