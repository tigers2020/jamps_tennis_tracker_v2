"""
Image Display Manager Module

This module provides a manager for handling image display related operations
for the Tennis Ball Tracker system.
"""

from PySide6.QtCore import QObject, Slot, Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QLabel
import cv2
import numpy as np

from src.controllers.image_manager import ImageManager
from src.controllers.image_player_controller import ImagePlayerController
from src.models.app_state import AppState
from src.utils.logger import Logger
from src.utils.tennis_ball_detector import draw_detection_overlay, draw_3d_position
from src.constants.ui_constants import (
    ASPECT_RATIO_16_9,
    OPENCV_GREEN,
    OPENCV_YELLOW
)


class ImageDisplayManager(QObject):
    """
    Manager for image display operations.
    
    This class handles:
    - Loading and displaying images
    - Caching and managing image pixmaps
    - Resizing images for display
    - Updating the UI elements based on current frame
    """

    # Signal emitted when images are updated
    images_updated = Signal(int)  # Current frame number

    def __init__(self, left_image_label=None, right_image_label=None):
        """
        Initialize the image display manager.
        
        Args:
            left_image_label: QLabel for displaying left camera images
            right_image_label: QLabel for displaying right camera images
        """
        super(ImageDisplayManager, self).__init__()
        
        # Get singleton instances
        self.logger = Logger.instance()
        self.app_state = AppState.instance()
        self.image_manager = ImageManager.instance()
        
        # UI elements
        self._left_image_label = left_image_label
        self._right_image_label = right_image_label
        
        # Cache for original pixmaps
        self._left_original_pixmap = None
        self._right_original_pixmap = None
        
        # Dictionary to store current images
        self._images = {'left': None, 'right': None}
        
        # Detection overlay state
        self._left_detection_result = None
        self._right_detection_result = None
        self._position_3d = None
        
        # Image cache for better performance (frame_num -> dict of images)
        self._image_cache = {}
        self._max_cache_size = 20  # Maximum number of frames to cache
        
        # Connect signals
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect to required signals"""
        if self.image_manager:
            self.image_manager.current_image_changed.connect(self._on_current_image_changed)
    
    def set_left_label(self, label):
        """
        Set the left image label.
        
        Args:
            label: QLabel for displaying left camera images
        """
        self._left_image_label = label
    
    def set_right_label(self, label):
        """
        Set the right image label.
        
        Args:
            label: QLabel for displaying right camera images
        """
        self._right_image_label = label
    
    @Slot(str)
    def _on_current_image_changed(self, image_path):
        """
        Handle current image changed signal.
        
        Args:
            image_path: Path to the current image (unused, kept for signal compatibility)
        """
        self.update_displayed_images()
    
    def update_displayed_images(self, frame_number=None):
        """
        Update all displayed images with the current frame.
        
        Args:
            frame_number: Optional frame number to display
        """
        try:
            # Early return if no frames loaded
            if self.image_manager.get_total_images() == 0:
                return
            
            # Determine the frame number to display
            if frame_number is None:
                frame_number = self.app_state.current_frame + 1  # Frame numbers start from 1
            elif frame_number == 0:
                frame_number = 1  # Convert index 0 to frame 1
            
            # Try to get images from cache first
            if frame_number in self._image_cache:
                cached_images = self._image_cache[frame_number]
                self._images = cached_images
                
                # Update display labels
                if 'left' in cached_images and cached_images['left'] is not None:
                    self._update_image_display(self._left_image_label, cached_images['left'])
                
                if 'right' in cached_images and cached_images['right'] is not None:
                    self._update_image_display(self._right_image_label, cached_images['right'])
                
                # Copy original pixmaps from cache
                self._left_original_pixmap = self._image_cache.get(f'left_orig_{frame_number}')
                self._right_original_pixmap = self._image_cache.get(f'right_orig_{frame_number}')
                
                # Emit signal that images have been updated
                self.images_updated.emit(frame_number)
                return
            
            # Get both camera images in one call
            left_pixmap, right_pixmap = self.image_manager.get_images(frame_number)
            
            # Update left camera image
            if left_pixmap and self._left_image_label:
                self._update_image_display(self._left_image_label, left_pixmap)
                self._left_original_pixmap = left_pixmap
            
            # Update right camera image
            if right_pixmap and self._right_image_label:
                self._update_image_display(self._right_image_label, right_pixmap)
                self._right_original_pixmap = right_pixmap
            
            # Apply detection overlays if available
            self._apply_detection_overlays()
            
            # Update cache
            self._image_cache[frame_number] = self._images
            self._image_cache[f'left_orig_{frame_number}'] = self._left_original_pixmap
            self._image_cache[f'right_orig_{frame_number}'] = self._right_original_pixmap
            
            # Limit cache size
            if len(self._image_cache) > self._max_cache_size * 3:  # Each frame takes 3 entries
                keys = sorted([k for k in self._image_cache.keys() if not isinstance(k, str)])
                for key in keys[:len(keys) - self._max_cache_size]:
                    del self._image_cache[key]
                    del self._image_cache[f'left_orig_{key}']
                    del self._image_cache[f'right_orig_{key}']
            
            # Emit signal that images have been updated
            self.images_updated.emit(frame_number)
            
        except Exception as e:
            self.logger.error(f"Error updating displayed images: {str(e)}")
    
    def _update_image_display(self, label, pixmap):
        """
        Update image display with proper scaling and maintaining 16:9 aspect ratio.
        
        Args:
            label: QLabel to update
            pixmap: QPixmap to display
        """
        if not label or pixmap.isNull():
            return
            
        # Store as attribute on the label for later reference
        label._original_pixmap = pixmap
        
        # Get original dimensions
        orig_width = pixmap.width()
        orig_height = pixmap.height()
        
        # Get label size (target size)
        label_width = label.width()
        label_height = label.height()
        
        # Ensure we have a valid label size
        if label_width <= 0 or label_height <= 0:
            label.setPixmap(pixmap)
            return
            
        # Calculate dimensions to enforce 16:9 ratio
        # Always maintain 16:9 ratio
        target_size = QSize(label_width, label_height)
        
        # Check if we need to scale by width or height
        if target_size.width() / target_size.height() > ASPECT_RATIO_16_9:
            # Label is wider than 16:9, use height as constraint
            new_height = target_size.height()
            new_width = int(new_height * ASPECT_RATIO_16_9)
        else:
            # Label is taller than 16:9, use width as constraint
            new_width = target_size.width()
            new_height = int(new_width / ASPECT_RATIO_16_9)
        
        # Scale the image maintaining 16:9 ratio
        scaled_pixmap = pixmap.scaled(
            new_width, new_height,
            Qt.IgnoreAspectRatio,  # We've manually calculated the ratio
            Qt.SmoothTransformation
        )
        
        # Update label with scaled image
        label.setPixmap(scaled_pixmap)
    
    def handle_resize(self, left_label=None, right_label=None):
        """
        Handle resize events for image labels.
        
        Args:
            left_label: Left camera image label (default: self._left_image_label)
            right_label: Right camera image label (default: self._right_image_label)
        """
        if left_label is None:
            left_label = self._left_image_label
        
        if right_label is None:
            right_label = self._right_image_label
        
        # Resize left image
        if left_label:
            self._resize_image(left_label)
        
        # Resize right image
        if right_label:
            self._resize_image(right_label)
            
        # Reapply detection overlays after resize
        self._apply_detection_overlays()
    
    def _resize_image(self, label):
        """
        Resize a single image maintaining 16:9 aspect ratio.
        
        Args:
            label: QLabel containing the image to resize
        """
        if not label:
            return
            
        # Get original pixmap (stored as attribute)
        original_pixmap = getattr(label, '_original_pixmap', None)
        if not original_pixmap or original_pixmap.isNull():
            # Try using current pixmap as fallback
            original_pixmap = label.pixmap()
            if not original_pixmap or original_pixmap.isNull():
                return
        
        # Get label size
        label_width = label.width()
        label_height = label.height()
        if label_width <= 0 or label_height <= 0:
            return
            
        # Always maintain 16:9 ratio
        target_size = QSize(label_width, label_height)
        
        # Check if we need to scale by width or height
        if target_size.width() / target_size.height() > ASPECT_RATIO_16_9:
            # Label is wider than 16:9, use height as constraint
            new_height = target_size.height()
            new_width = int(new_height * ASPECT_RATIO_16_9)
        else:
            # Label is taller than 16:9, use width as constraint
            new_width = target_size.width()
            new_height = int(new_width / ASPECT_RATIO_16_9)
        
        # Create scaled version with 16:9 ratio
        scaled_pixmap = original_pixmap.scaled(
            new_width, new_height,
            Qt.IgnoreAspectRatio,  # We've manually calculated the ratio
            Qt.SmoothTransformation
        )
        
        # Update label with scaled image
        label.setPixmap(scaled_pixmap)
    
    def get_left_original_pixmap(self):
        """Get the original left camera pixmap."""
        return self._left_original_pixmap
    
    def get_right_original_pixmap(self):
        """Get the original right camera pixmap."""
        return self._right_original_pixmap

    @property
    def images(self):
        """
        Get current images dictionary
        
        Returns:
            dict: Dictionary with 'left' and 'right' pixmap entries
        """
        # Update dictionary with latest pixmaps
        self._images['left'] = self._left_original_pixmap
        self._images['right'] = self._right_original_pixmap
        return self._images
        
    def set_ball_detection_result(self, camera, detection_result):
        """
        Set the ball detection result for a camera
        
        Args:
            camera: Camera name ('left' or 'right')
            detection_result: Detection result dictionary from ball detection
        """
        if camera.lower() == 'left':
            self._left_detection_result = detection_result
        elif camera.lower() == 'right':
            self._right_detection_result = detection_result
        
        # Apply overlays to update display
        self._apply_detection_overlays()
            
    def set_3d_position(self, position_3d):
        """
        Set the 3D position data for display
        
        Args:
            position_3d: (x, y, z) tuple with 3D position
        """
        self._position_3d = position_3d
        
        # Apply overlays to update display
        self._apply_detection_overlays()
        
    def _apply_detection_overlays(self):
        """Apply detection overlays to both camera images"""
        # Process left camera overlay
        if self._left_detection_result and self._left_original_pixmap and self._left_image_label:
            try:
                # Convert QPixmap to OpenCV image for processing
                image_array = self._pixmap_to_cv2(self._left_original_pixmap)
                if image_array is not None:
                    # Draw detection overlay
                    overlay_image = draw_detection_overlay(
                        image_array, 
                        self._left_detection_result, 
                        color=OPENCV_GREEN  # Green
                    )
                    
                    # Draw 3D position if available
                    if self._position_3d:
                        overlay_image = draw_3d_position(
                            overlay_image,
                            self._position_3d,
                            color=OPENCV_GREEN  # Green
                        )
                    
                    # Convert back to QPixmap and update label
                    overlay_pixmap = self._cv2_to_pixmap(overlay_image)
                    if overlay_pixmap and not overlay_pixmap.isNull():
                        # Update with proper scaling
                        self._update_image_display(self._left_image_label, overlay_pixmap)
            except Exception as e:
                self.logger.error(f"Error applying left camera detection overlay: {e}")
        
        # Process right camera overlay
        if self._right_detection_result and self._right_original_pixmap and self._right_image_label:
            try:
                # Convert QPixmap to OpenCV image for processing
                image_array = self._pixmap_to_cv2(self._right_original_pixmap)
                if image_array is not None:
                    # Draw detection overlay
                    overlay_image = draw_detection_overlay(
                        image_array, 
                        self._right_detection_result, 
                        color=OPENCV_YELLOW  # Yellow
                    )
                    
                    # Convert back to QPixmap and update label
                    overlay_pixmap = self._cv2_to_pixmap(overlay_image)
                    if overlay_pixmap and not overlay_pixmap.isNull():
                        # Update with proper scaling
                        self._update_image_display(self._right_image_label, overlay_pixmap)
            except Exception as e:
                self.logger.error(f"Error applying right camera detection overlay: {e}")
    
    def _pixmap_to_cv2(self, pixmap):
        """
        Convert QPixmap to OpenCV image
        
        Args:
            pixmap: QPixmap to convert
            
        Returns:
            numpy.ndarray: OpenCV image in BGR format
        """
        if pixmap is None or pixmap.isNull():
            return None
            
        # Convert QPixmap to QImage
        image = pixmap.toImage()
        
        # Extract dimensions
        width = image.width()
        height = image.height()
        
        # Convert to OpenCV format
        if image.format() == image.Format_RGB32 or image.format() == image.Format_ARGB32:
            # Create numpy array from image data
            ptr = image.constBits()
            # Convert to numpy array (accounting for 4-channel ARGB)
            arr = np.array(ptr).reshape(height, width, 4)
            # Convert RGBA to BGR for OpenCV
            return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        else:
            # For other formats, convert to RGB32 first
            rgb_image = image.convertToFormat(image.Format_RGB32)
            ptr = rgb_image.constBits()
            arr = np.array(ptr).reshape(height, width, 4)
            return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    
    def _cv2_to_pixmap(self, cv_img):
        """
        Convert OpenCV image to QPixmap
        
        Args:
            cv_img: OpenCV image in BGR format
            
        Returns:
            QPixmap: Converted pixmap
        """
        if cv_img is None:
            return None
            
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        # Create QPixmap from numpy array
        height, width, channel = rgb_image.shape
        bytes_per_line = 3 * width
        from PySide6.QtGui import QImage
        q_img = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        return QPixmap.fromImage(q_img) 