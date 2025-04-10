"""
Image Display Manager Module

This module provides a manager for handling image display related operations
for the Tennis Ball Tracker system.
"""

from PySide6.QtCore import QObject, Slot, Signal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel

from src.controllers.image_manager import ImageManager
from src.controllers.image_player_controller import ImagePlayerController
from src.models.app_state import AppState
from src.utils.logger import Logger


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
            
            # Emit signal that images have been updated
            self.images_updated.emit(frame_number)
            
        except Exception as e:
            self.logger.error(f"Error updating displayed images: {str(e)}")
    
    def _update_image_display(self, label, pixmap):
        """
        Update image display with proper scaling and maintaining 4:3 aspect ratio.
        
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
            
        # Calculate dimensions to enforce 4:3 ratio
        # Always maintain 4:3 ratio
        target_ratio = 4.0 / 3.0
        
        # Determine scaling based on label constraints
        if (label_width / label_height) > target_ratio:
            # Label is wider than 4:3, use height as constraint
            new_height = label_height
            new_width = int(new_height * target_ratio)
        else:
            # Label is taller than 4:3, use width as constraint
            new_width = label_width
            new_height = int(new_width / target_ratio)
        
        # Scale the image maintaining 4:3 ratio
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
    
    def _resize_image(self, label):
        """
        Resize a single image maintaining 4:3 aspect ratio.
        
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
            
        # Always maintain 4:3 ratio
        target_ratio = 4.0 / 3.0
        
        # Determine scaling based on label constraints
        if (label_width / label_height) > target_ratio:
            # Label is wider than 4:3, use height as constraint
            new_height = label_height
            new_width = int(new_height * target_ratio)
        else:
            # Label is taller than 4:3, use width as constraint
            new_width = label_width
            new_height = int(new_width / target_ratio)
        
        # Create scaled version with 4:3 ratio
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