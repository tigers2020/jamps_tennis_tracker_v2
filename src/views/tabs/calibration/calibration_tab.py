"""
Calibration Tab Module
=====================

Tennis court calibration tab for selecting key points on tennis court images.
This module provides a tab interface for users to select key points on 
tennis court images and save those points to a JSON file for later use
in the tracking system.
"""

import logging
import os
from typing import List, Tuple, Optional, Dict, Union

from PySide6.QtCore import Qt, Signal, QPoint, QEvent
from PySide6.QtGui import QPixmap, QColor, QImage, QPainter
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QGridLayout, QFrame, QSizePolicy, QMessageBox, QGroupBox
)

from src.models.app_state import AppState
from src.utils.settings_manager import SettingsManager
from src.controllers.calibration.point_manager import CalibrationPointManager
from src.models.calibration.point_io import CalibrationPointIO
from src.utils.image.image_utils import scale_pos_to_original, draw_calibration_points
from src.utils.math.vector import Vector2D
from src.utils.ui_theme import (
    get_group_box_style, get_label_style, get_button_style, 
    get_separator_style, get_message_box_style, get_image_label_style,
    get_active_image_label_style, get_inactive_image_label_style,
    get_status_label_style, get_disabled_button_style
)


class CalibrationTab(QWidget):
    """
    A tab widget for selecting key points on tennis court images.
    
    This tab allows a user to select 12 key points on an image, view the selected points,
    and save them to a JSON file.
    """
    
    # Signal emitted when calibration is completed (all points selected)
    calibration_completed = Signal(str)  # Signal parameter: camera_name
    
    def __init__(self, parent=None):
        """Initialize the calibration tab"""
        super().__init__(parent)
        
        # Set constant parameters
        self.TOTAL_POINTS = 12
        
        # Initialize component managers
        self.point_manager = CalibrationPointManager(self.TOTAL_POINTS)
        self.point_io = CalibrationPointIO(self.TOTAL_POINTS)
        
        # Connect point manager signals
        self.point_manager.points_changed.connect(self._on_points_changed)
        
        # Dragging state variables
        self.dragging = False
        self.drag_start_pos = None
        
        # Image pixmaps
        self.left_pixmap: Optional[QPixmap] = None
        self.right_pixmap: Optional[QPixmap] = None
        
        # Cached scaled pixmaps for better performance
        self.scaled_left_pixmap: Optional[QPixmap] = None
        self.scaled_right_pixmap: Optional[QPixmap] = None
        
        # Current calibration frame number
        self.calibration_frame_number = 1
        
        # Get singleton instances
        self.app_state = AppState.instance()
        self.logger = logging.getLogger(__name__)
                
        # Setup the user interface
        self._setup_ui()
        
        # Load any saved points
        self._load_points()
        
        # Load the calibration frame
        self._load_calibration_frame()
        
        # Set active camera to left by default
        self.point_manager.set_active_camera("left")
        
        # Update status and button states
        self._update_status_info()
        self._update_button_states()
    
    def _setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # =================== TITLE AND INSTRUCTIONS ===================
        # Create a grouped section for title and instructions
        instruction_group = QGroupBox("Tennis Court Calibration Instructions")
        instruction_group.setObjectName("instructionGroup")
        instruction_group.setStyleSheet(get_group_box_style(is_title_centered=True))
        instruction_layout = QVBoxLayout(instruction_group)
        instruction_layout.setContentsMargins(15, 20, 15, 15)
        
        # Create a horizontal layout for two-column instructions
        instruction_columns = QHBoxLayout()
        instruction_columns.setSpacing(0)
        
        # Left column
        left_instructions_text = (
            "<b>Tennis Court Calibration Guide:</b><br><br>"
            
            "1. <b>Select 12 key points:</b><br>"
            "   • Click precisely at <b>white line</b><br>"
            "     <b>intersections</b> on the court<br>"
            "   • Set points for both camera images<br><br>"
            
            "2. <b>Select points in this order:</b><br>"
            "   • Baseline: 5 points (left to right)<br>"
            "   • Net line: 3 points (left to right)<br>"
            "   • Service line: 4 points (left to right)<br>"
        )
        
        # Right column
        right_instructions_text = (
            "<b>Controls & Functions:</b><br><br>"
            
            "• <b>Click</b>: Add new point<br>"
            "• <b>Drag</b>: Adjust existing point<br>"
            "• <b>Reset button</b>: Clear all points<br><br>"
            
            "<b>Post Process function:</b><br>"
            "• Automatically aligns points<br>"
            "• Detects white line centers<br>"
            "• Improves calibration accuracy<br>"
            "• Run after selecting all points<br><br>"
            
            "<b>Click 'Save Points' when complete</b>"
        )
        
        # Create and add left column label
        left_instructions = QLabel(left_instructions_text)
        left_instructions.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        left_instructions.setTextFormat(Qt.RichText)
        left_instructions.setWordWrap(True)
        left_instructions.setStyleSheet(get_label_style(is_description=True))
        instruction_columns.addWidget(left_instructions)
        
        # Add vertical separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(get_separator_style())
        instruction_columns.addWidget(separator)
        
        # Create and add right column label
        right_instructions = QLabel(right_instructions_text)
        right_instructions.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        right_instructions.setTextFormat(Qt.RichText)
        right_instructions.setWordWrap(True)
        right_instructions.setStyleSheet(get_label_style(is_description=True))
        instruction_columns.addWidget(right_instructions)
        
        # Add the columns layout to the instruction layout
        instruction_layout.addLayout(instruction_columns)
        
        # Status label
        self.status_label = QLabel("Select points on the tennis court")
        self.status_label.setStyleSheet(get_label_style())
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(30)
        instruction_layout.addWidget(self.status_label)
        
        main_layout.addWidget(instruction_group)
        
        # =================== CAMERA IMAGES ===================
        # Images row (left and right images side by side)
        images_layout = QHBoxLayout()
        images_layout.setSpacing(15)
        
        # Left camera image
        left_camera_group = QGroupBox("Left Camera Image")
        left_camera_group.setStyleSheet(get_group_box_style(is_title_centered=True))
        left_camera_layout = QVBoxLayout(left_camera_group)
        
        # Left camera label
        self.left_image_label = QLabel()
        self.left_image_label.setAlignment(Qt.AlignCenter)
        self.left_image_label.setMinimumSize(640, 360)
        self.left_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.left_image_label.setStyleSheet(get_image_label_style())
        
        # Install event filter for mouse interactions
        self.left_image_label.installEventFilter(self)
        self.left_image_label.setMouseTracking(True)
        
        left_camera_layout.addWidget(self.left_image_label)
        
        images_layout.addWidget(left_camera_group)
        
        # Right camera image
        right_camera_group = QGroupBox("Right Camera Image")
        right_camera_group.setStyleSheet(get_group_box_style(is_title_centered=True))
        right_camera_layout = QVBoxLayout(right_camera_group)
        
        # Right camera label
        self.right_image_label = QLabel()
        self.right_image_label.setAlignment(Qt.AlignCenter)
        self.right_image_label.setMinimumSize(640, 360)
        self.right_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_image_label.setStyleSheet(get_image_label_style())
        
        # Install event filter for mouse interactions
        self.right_image_label.installEventFilter(self)
        self.right_image_label.setMouseTracking(True)
        
        right_camera_layout.addWidget(self.right_image_label)
        
        images_layout.addWidget(right_camera_group)
        
        main_layout.addLayout(images_layout)
        
        # =================== ACTIONS ===================
        # Actions row (Reset, Load, Post-Process, Save)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        # Add left spacer for centering
        action_layout.addStretch(1)
        
        # Reset button
        self.reset_button = QPushButton("Reset Points")
        self.reset_button.clicked.connect(self._reset_points)
        self.reset_button.setToolTip("Remove all selected points for the current camera")
        self.reset_button.setStyleSheet(get_button_style(is_destructive=True))
        action_layout.addWidget(self.reset_button)
        
        # Load button
        self.load_button = QPushButton("Load Points")
        self.load_button.clicked.connect(self._load_points)
        self.load_button.setToolTip("Load previously saved calibration points")
        self.load_button.setStyleSheet(get_button_style())
        action_layout.addWidget(self.load_button)
        
        # Post-process button
        self.process_button = QPushButton("Post Process")
        self.process_button.clicked.connect(self._post_process_points)
        self.process_button.setToolTip("Optimize and align selected points automatically")
        self.process_button.setStyleSheet(get_button_style())
        action_layout.addWidget(self.process_button)
        
        # Save button
        self.save_button = QPushButton("Save Points")
        self.save_button.clicked.connect(self._save_points)
        self.save_button.setToolTip("Save calibration points for future use")
        self.save_button.setStyleSheet(get_button_style(is_primary=True))
        action_layout.addWidget(self.save_button)
        
        # Add right spacer for centering
        action_layout.addStretch(1)
        
        main_layout.addLayout(action_layout)
    
    def _select_camera(self, camera_type):
        """Select the active camera type ('left' or 'right')"""
        # Set the active camera in the point manager
        self.point_manager.set_active_camera(camera_type)
        
        # Update UI state
        self._update_status_info()
        self._update_button_states()
        self._display_images()
    
    def _on_points_changed(self, camera):
        """
        Handle points changes from the point manager.
        
        This method is called when points are added, updated, or removed in the
        point manager. It updates the UI to reflect the changes and emits the
        calibration_completed signal if all points for a camera have been selected.
        
        Args:
            camera: The camera type ('left' or 'right') that had its points changed
        """
        # Update UI elements
        self._display_images()
        self._update_status_info()
        self._update_button_states()
        
        # Check if calibration is complete for the camera and emit signal if so
        if self.point_manager.is_complete(camera):
            self.logger.info(f"Calibration completed for {camera} camera")
            self.calibration_completed.emit(camera)
    
    def _display_images(self):
        """
        Display calibration images with calibration points.
        This method efficiently renders images and calibration points.
        """
        # Early return if images aren't loaded
        if not self.left_pixmap or not self.right_pixmap:
            return
            
        # Process left image
        if self.left_image_label:
            self._render_image(
                self.left_image_label,
                self.left_pixmap, 
                self.point_manager.left_key_points,
                self.point_manager.left_selected_point_idx if self.point_manager.active_camera == "left" else -1,
                is_active=(self.point_manager.active_camera == "left")
            )
            
        # Process right image
        if self.right_image_label:
            self._render_image(
                self.right_image_label,
                self.right_pixmap,
                self.point_manager.right_key_points,
                self.point_manager.right_selected_point_idx if self.point_manager.active_camera == "right" else -1,
                is_active=(self.point_manager.active_camera == "right")
            )
    
    def _render_image(self, image_label, source_pixmap, points, selected_point_idx, is_active=False):
        """
        Render a single image with calibration points.
        
        Args:
            image_label: The QLabel to display the image in
            source_pixmap: The source image pixmap
            points: List of calibration points to draw
            selected_point_idx: Index of selected point (-1 if none)
            is_active: Whether this is the active camera
        """
        # Create a copy of the pixmap for drawing
        display_pixmap = QPixmap(source_pixmap)
        
        # If we have points, draw them
        if points:
            # Set parameters for point drawing
            active_color = QColor(0, 255, 0)  # Green for active camera
            inactive_color = QColor(255, 255, 0)  # Yellow for inactive camera
            point_color = active_color if is_active else inactive_color
            
            # Draw points on the image
            draw_calibration_points(
                display_pixmap, 
                points, 
                selected_point_idx,
                point_color=point_color,
                selected_color=QColor(255, 0, 0)  # Red for selected point
            )
        
        # Scale the pixmap to fit in the label while maintaining aspect ratio
        scaled_pixmap = display_pixmap.scaled(
            image_label.width(), 
            image_label.height(),
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # Store the scaled pixmap for event handling
        if image_label == self.left_image_label:
            self.scaled_left_pixmap = scaled_pixmap
        else:
            self.scaled_right_pixmap = scaled_pixmap
        
        # Set the pixmap to the label
        image_label.setPixmap(scaled_pixmap)
        
        # Add highlight border for active camera
        if is_active:
            style = get_active_image_label_style()
            image_label.setStyleSheet(style)
        else:
            style = get_inactive_image_label_style()
            image_label.setStyleSheet(style)
    
    def _update_status_info(self):
        """Update the status information displayed to the user"""
        camera_type = self.point_manager.active_camera.capitalize()
        points = self.point_manager.key_points
        points_selected = len(points)
        points_remaining = self.TOTAL_POINTS - points_selected
        
        # Create a status message based on the current state
        if points_remaining > 0:
            status_msg = f"{camera_type} Camera: {points_selected}/{self.TOTAL_POINTS} points selected, {points_remaining} remaining"
        else:
            status_msg = f"{camera_type} Camera: All {self.TOTAL_POINTS} points selected - Ready to save!"
            
        # Check both cameras status for completion status
        left_complete = self.point_manager.is_complete("left")
        right_complete = self.point_manager.is_complete("right")
        
        if left_complete and right_complete:
            status_msg += " (Both cameras calibrated)"
        elif left_complete and not right_complete and self.point_manager.active_camera == "left":
            status_msg += " - Switch to Right Camera"
        elif right_complete and not left_complete and self.point_manager.active_camera == "right":
            status_msg += " - Switch to Left Camera"
            
        # Update the status label text
        self.status_label.setText(status_msg)
        
        # Set color based on completion status
        if points_remaining == 0:
            self.status_label.setStyleSheet(get_status_label_style("complete"))
        elif points_remaining <= 3:
            self.status_label.setStyleSheet(get_status_label_style("progress"))
        else:
            self.status_label.setStyleSheet(get_status_label_style("start"))
    
    def _update_button_states(self):
        """Update button enabled/disabled states based on current data"""
        # Current camera points
        points = self.point_manager.key_points
        
        # Enable/disable reset button based on if there are points to reset
        self.reset_button.setEnabled(len(points) > 0)
        
        # Enable/disable save button based on if at least one camera is completely calibrated
        left_complete = self.point_manager.is_complete("left")
        right_complete = self.point_manager.is_complete("right")
        self.save_button.setEnabled(left_complete or right_complete)
        
        # Enable/disable post-process button based on if there are enough points to process
        self.process_button.setEnabled(len(points) == self.TOTAL_POINTS)
        
        # Add visual styling to indicate button states
        for button in [self.reset_button, self.save_button, self.process_button]:
            if button.isEnabled():
                if button == self.reset_button:
                    button.setStyleSheet(get_button_style(is_destructive=True))
                elif button == self.save_button:
                    button.setStyleSheet(get_button_style(is_primary=True))
                else:
                    button.setStyleSheet(get_button_style())
            else:
                button.setStyleSheet(get_disabled_button_style())
    
    def _load_points(self):
        """Load points from a file"""
        try:
            # Get current resolution information for automatic scaling
            if not hasattr(self, 'resolution_name'):
                self.resolution_name = "1080p"  # Default if not detected
                
            # Pass current resolution to scale points appropriately
            success, points, message = self.point_io.load_points(
                target_resolution=self.resolution_name
            )
            
            if success:
                # Update UI with loaded points
                left_points = points.get("left_camera", [])
                right_points = points.get("right_camera", [])
                
                # Set left camera points if available
                if left_points:
                    self.point_manager.set_active_camera("left")
                    self.point_manager.key_points = left_points
                    self.logger.info(f"Loaded {len(left_points)} left camera points")
                    
                # Set right camera points if available    
                if right_points:
                    self.point_manager.set_active_camera("right")
                    self.point_manager.key_points = right_points
                    self.logger.info(f"Loaded {len(right_points)} right camera points")
                
                if left_points or right_points:
                    self._display_images()  # Update display with loaded points
                    
            else:
                # Show error message only for errors
                QMessageBox.warning(self, "Load Warning", message)
                
            # Update button states based on loaded points
            self._update_button_states()
            
        except Exception as e:
            self.logger.error(f"Error loading points: {str(e)}")
            QMessageBox.critical(self, "Load Error", f"Failed to load points: {str(e)}")
    
    def _save_points(self):
        """Save points to a file"""
        # Only allow saving if at least one camera is complete
        left_complete = self.point_manager.is_complete("left")
        right_complete = self.point_manager.is_complete("right")
        
        if not left_complete and not right_complete:
            QMessageBox.warning(self, "Warning", "You must select all points for at least one camera.")
            return
        
        # Get current resolution information
        if not hasattr(self, 'resolution_name'):
            self.resolution_name = "1080p"  # Default if not detected
        
        # Log resolution info for debugging
        self.logger.info(f"Saving calibration points with resolution: {self.resolution_name}")
        if hasattr(self, 'left_resolution'):
            self.logger.info(f"Actual image resolution: {self.left_resolution[0]}x{self.left_resolution[1]}")
        
        # Save points with resolution information
        success, filepath = self.point_io.save_points(
            self.point_manager.left_key_points,
            self.point_manager.right_key_points,
            resolution=self.resolution_name
        )
        
        # Log detailed info about the save operation
        if success:
            self.logger.info(f"Calibration points saved to: {filepath}")
            
            # Check if the file was saved correctly
            import json
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                if "resolution" in data and len(data.get("left_camera", [])) > 0:
                    first_point = data["left_camera"][0]
                    self.logger.info(f"First point saved as: {first_point}")
                    if 0 <= first_point.get('x', 0) <= 1 and 0 <= first_point.get('y', 0) <= 1:
                        self.logger.info("Coordinates appear to be normalized correctly")
                    else:
                        self.logger.warning("Coordinates do not appear to be normalized!")
            except Exception as e:
                self.logger.error(f"Error checking saved file: {str(e)}")
            
            # Show success message
            left_status = "Complete" if left_complete else "Incomplete"
            right_status = "Complete" if right_complete else "Incomplete"
            
            QMessageBox.information(
                self, 
                "Save Complete",
                f"Key points have been saved.\n"
                f"- Left Camera: {left_status}\n"
                f"- Right Camera: {right_status}\n"
                f"- Resolution: {self.resolution_name}\n"
                f"File path: {filepath}"
            )
        else:
            # Show error message
            QMessageBox.critical(self, "Save Error", filepath)
    
    def _silent_save(self):
        """Save points without showing a message box"""
        # Get current resolution information
        if not hasattr(self, 'resolution_name'):
            self.resolution_name = "1080p"  # Default if not detected
            
        self.point_io.save_points(
            self.point_manager.left_key_points,
            self.point_manager.right_key_points,
            resolution=self.resolution_name,
            silent=True
        )
    
    def _reset_points(self):
        """Reset points for the current active camera"""
        self.point_manager.reset_points()
        # UI is updated via the points_changed signal
    
    def _post_process_points(self):
        """Post-process the points to improve alignments"""
        # Set refinement parameters
        iterations = 3  # Number of iterations
        convergence_threshold = 1.5  # Convergence threshold (in pixels)
        
        # Image-based refinement first (find white line centers)
        left_refined = 0
        right_refined = 0
        
        # Perform white line detection if images are available
        if self.left_pixmap and self.right_pixmap:
            # Convert QPixmap to QImage for pixel access
            left_image = self.left_pixmap.toImage()
            right_image = self.right_pixmap.toImage()
            
            # Apply white line center detection with multiple iterations
            self.logger.info(f"Starting point refinement with {iterations} iterations (threshold: {convergence_threshold}px)")
            left_refined, right_refined = self.point_manager.refine_point_positions(
                left_image=left_image, 
                right_image=right_image,
                iterations=iterations,
                convergence_threshold=convergence_threshold
            )
        
        # Apply geometric alignment as well
        alignment_applied = self.point_manager.process_points()
        
        if alignment_applied or left_refined > 0 or right_refined > 0:
            # Prepare success message
            camera_name = self.point_manager.active_camera.capitalize()
            refinement_msg = ""
            
            if left_refined > 0 or right_refined > 0:
                refinement_msg = (
                    f"- White line detection applied to {left_refined} left and {right_refined} right points\n"
                    f"- Performed up to {iterations} iterations of refinement\n"
                    f"- Stopped when point movements were below {convergence_threshold}px\n"
                )
            
            # Show success message
            QMessageBox.information(
                self,
                "Post-Processing Complete",
                f"{camera_name} camera points have been aligned:\n"
                f"{refinement_msg}"
                "- Minor alignment applied to preserve original positions\n"
                "- Partial adjustment for vertical alignments\n"
                "- Original point characteristics maintained"
            )
            
            # Auto-save the processed points
            self._silent_save()
        else:
            # Show error message if processing failed
            QMessageBox.critical(
                self,
                "Post-Processing Error",
                "Failed to process points. Make sure all points are selected."
            )
    
    def _handle_image_click(self, click_pos, image_label, pixmap):
        """
        Handle mouse click on an image label for point creation or selection.
        
        This method converts the click position to image coordinates and either
        selects an existing point or adds a new one depending on context.
        
        Args:
            click_pos: Position where the mouse was clicked in label coordinates
            image_label: The QLabel that received the click
            pixmap: The original pixmap being displayed
            
        Returns:
            None
        """
        # Get the dimensions needed for coordinate conversion
        label_size = (image_label.width(), image_label.height())
        pixmap_size = (pixmap.width(), pixmap.height())
        
        # Get the correct scaled pixmap
        if image_label == self.left_image_label:
            scaled_pixmap = self.scaled_left_pixmap
        else:
            scaled_pixmap = self.scaled_right_pixmap
            
        if scaled_pixmap is None:
            self.logger.warning("Scaled pixmap is None in _handle_image_click")
            return
            
        scaled_size = (scaled_pixmap.width(), scaled_pixmap.height())
        
        # Convert from label coordinates to original image coordinates
        image_pos = scale_pos_to_original(
            click_pos, 
            label_size, 
            pixmap_size, 
            scaled_size
        )
        
        # Skip invalid positions
        if image_pos.x < 0 or image_pos.y < 0:
            self.logger.warning(f"Invalid click position: {image_pos.x}, {image_pos.y}")
            return
        
        # Add a new point if we haven't reached the maximum
        if len(self.point_manager.key_points) < self.TOTAL_POINTS:
            self.point_manager.add_point(int(image_pos.x), int(image_pos.y))
            self.logger.info(f"Added new point at ({int(image_pos.x)}, {int(image_pos.y)})")
            
            # Auto-save if all points have been selected
            if self.point_manager.is_complete():
                self._silent_save()
        else:
            self.logger.info(f"Maximum points ({self.TOTAL_POINTS}) already reached")
            QMessageBox.information(
                self,
                "Maximum Points Reached",
                f"You've already selected all {self.TOTAL_POINTS} points for this camera.\n"
                "To modify existing points, click and drag them."
            )
    
    def eventFilter(self, obj, event):
        """
        Event filter to handle mouse and key press events on the image labels.
        
        This method intercepts events for the left and right image labels and
        handles mouse clicks, movements, and key presses for point selection
        and manipulation.
        
        Args:
            obj: The object that received the event
            event: The event that occurred
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        # Skip processing for non-image label objects
        if not (obj == self.left_image_label or obj == self.right_image_label):
            return super().eventFilter(obj, event)
            
        # Check if we have valid pixmaps
        is_left = obj == self.left_image_label
        current_pixmap = self.left_pixmap if is_left else self.right_pixmap
        if current_pixmap is None or current_pixmap.isNull():
            return super().eventFilter(obj, event)
        
        # Handle different event types
        if event.type() == QEvent.MouseButtonPress:
            return self._handle_mouse_press(event, is_left, current_pixmap)
        elif event.type() == QEvent.MouseMove:
            if self.dragging:
                return self._handle_mouse_move(event, is_left, current_pixmap)
            else:
                return self._handle_mouse_hover(event, is_left, current_pixmap)
        elif event.type() == QEvent.MouseButtonRelease:
            return self._handle_mouse_release(event)
        elif event.type() == QEvent.KeyPress:
            return self._handle_key_press(event)
        
        # Pass to parent's event filter
        return super().eventFilter(obj, event)
        
    def _handle_mouse_press(self, event, is_left, current_pixmap):
        """
        Handle mouse press events for point selection and creation.
        
        Args:
            event: The mouse press event
            is_left: True if the event occurred on the left image label
            current_pixmap: The pixmap of the current image label
            
        Returns:
            bool: True if the event was handled
        """
        # Left button click only
        if event.button() != Qt.LeftButton:
            return False
            
        # Set active camera
        camera_type = "left" if is_left else "right"
        if self.point_manager.active_camera != camera_type:
            self.point_manager.set_active_camera(camera_type)
        
        # Get position and convert to image coordinates
        pos = event.pos()
        current_label = self.left_image_label if is_left else self.right_image_label
        current_scaled_pixmap = self.scaled_left_pixmap if is_left else self.scaled_right_pixmap
        
        if current_scaled_pixmap is None:
            self.logger.warning("Scaled pixmap is None, cannot handle mouse press")
            return True
            
        scaled_pos = scale_pos_to_original(
            pos,
            (current_label.width(), current_label.height()),
            (current_pixmap.width(), current_pixmap.height()),
            (current_scaled_pixmap.width(), current_scaled_pixmap.height())
        )
        
        # Skip invalid positions
        if scaled_pos.x < 0 or scaled_pos.y < 0:
            self.logger.warning(f"Invalid position: {scaled_pos.x}, {scaled_pos.y}")
            return True
            
        # Check if selecting an existing point
        points = self.point_manager.left_key_points if is_left else self.point_manager.right_key_points
        if points:
            nearest_idx = self.point_manager.find_nearest_point(scaled_pos, threshold=20)
            
            if nearest_idx >= 0:
                # Select the point and prepare for dragging
                self.point_manager.selected_point_idx = nearest_idx
                self.dragging = True
                self.drag_start_pos = scaled_pos
                
                # Initialize update time for performance optimization
                self.last_update_time = 0
                self._display_images()  # Update display to show selected point
                self.logger.info(f"Selected point {nearest_idx+1} at ({int(scaled_pos.x)}, {int(scaled_pos.y)})")
                return True
        
        # Add a new point
        self._handle_image_click(pos, current_label, current_pixmap)
        return True
        
    def _handle_mouse_move(self, event, is_left, current_pixmap):
        """
        Handle mouse move events for dragging points.
        
        Args:
            event: The mouse move event
            is_left: True if the event occurred on the left image label
            current_pixmap: The pixmap of the current image label
            
        Returns:
            bool: True if the event was handled
        """
        # Skip if not dragging or no point selected
        if not self.dragging or self.point_manager.selected_point_idx < 0:
            return False
        
        # Limit update frequency for better performance (target ~30fps)
        import time
        current_time = time.time() * 1000  # In milliseconds
        if hasattr(self, 'last_update_time') and current_time - self.last_update_time < 33:
            return True
        
        self.last_update_time = current_time
        
        # Get current label and pixmap
        current_label = self.left_image_label if is_left else self.right_image_label
        current_scaled_pixmap = self.scaled_left_pixmap if is_left else self.scaled_right_pixmap
        
        if current_scaled_pixmap is None:
            return True
            
        # Calculate new position
        pos = event.pos()
        scaled_pos = scale_pos_to_original(
            pos,
            (current_label.width(), current_label.height()),
            (current_pixmap.width(), current_pixmap.height()),
            (current_scaled_pixmap.width(), current_scaled_pixmap.height())
        )
        
        # Skip invalid positions
        if scaled_pos.x < 0 or scaled_pos.y < 0:
            return True
        
        # Update point position
        self.point_manager.update_point(
            self.point_manager.selected_point_idx,
            int(scaled_pos.x),
            int(scaled_pos.y)
        )
        
        return True
        
    def _handle_mouse_release(self, event):
        """
        Handle mouse release events to end dragging operations.
        
        Args:
            event: The mouse release event
            
        Returns:
            bool: True if the event was handled
        """
        if self.dragging:
            self.dragging = False
            self.drag_start_pos = None
            
            # Auto-save if all points are selected
            if self.point_manager.is_complete():
                self._silent_save()
            
            return True
        
        return False
        
    def _handle_key_press(self, event):
        """
        Handle key press events for point manipulation.
        
        Args:
            event: The key press event
            
        Returns:
            bool: True if the event was handled
        """
        # Delete selected point
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            if self.point_manager.selected_point_idx >= 0:
                self.point_manager.delete_point(self.point_manager.selected_point_idx)
                return True
        
        return False

    def _handle_mouse_hover(self, event, is_left, current_pixmap):
        """
        Handle mouse hover events to change cursor when over points.
        
        Args:
            event: The mouse move event
            is_left: True if the event occurred on the left image label
            current_pixmap: The pixmap of the current image label
            
        Returns:
            bool: True if the event was handled
        """
        # Get current position
        current_label = self.left_image_label if is_left else self.right_image_label
        current_scaled_pixmap = self.scaled_left_pixmap if is_left else self.scaled_right_pixmap
        
        if current_scaled_pixmap is None:
            return False
            
        # Get mouse position and convert to image coordinates
        pos = event.pos()
        scaled_pos = scale_pos_to_original(
            pos,
            (current_label.width(), current_label.height()),
            (current_pixmap.width(), current_pixmap.height()),
            (current_scaled_pixmap.width(), current_scaled_pixmap.height())
        )
        
        # Check if hovering over a point
        points = self.point_manager.left_key_points if is_left else self.point_manager.right_key_points
        if points:
            nearest_idx = self.point_manager.find_nearest_point(scaled_pos, threshold=20)
            if nearest_idx >= 0:
                # Change cursor to pointing hand
                current_label.setCursor(Qt.PointingHandCursor)
                return True
        
        # Reset cursor to default
        current_label.setCursor(Qt.ArrowCursor)
        return False

    def _load_calibration_frame(self):
        """Load the calibration frame from settings or default test images"""
        left_img_path = None
        right_img_path = None
        
        try:
            # Get settings singleton
            settings = SettingsManager.instance()
            calibration_images = settings.get('calibration_images', {})
            
            # Get image paths from settings
            frame_key = f"frame_{self.calibration_frame_number}"
            left_img_path = calibration_images.get(f"{frame_key}_left", "")
            right_img_path = calibration_images.get(f"{frame_key}_right", "")
            
            # Ensure only JPG files are used - explicitly avoid PNG
            if left_img_path and left_img_path.lower().endswith('.png'):
                self.logger.warning(f"PNG file detected in settings, ignoring: {left_img_path}")
                left_img_path = ""
                
            if right_img_path and right_img_path.lower().endswith('.png'):
                self.logger.warning(f"PNG file detected in settings, ignoring: {right_img_path}")
                right_img_path = ""
            
            # Check if the paths exist and are valid JPG files
            if not (left_img_path and os.path.exists(left_img_path) and left_img_path.lower().endswith('.jpg') and 
                    right_img_path and os.path.exists(right_img_path) and right_img_path.lower().endswith('.jpg')):
                # Always use test images from src/resources/tests/images
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
                test_dir = os.path.join(base_path, "src", "resources", "tests", "images")
                
                # Using proper zero-padded file name format (0001 instead of 1)
                # Explicitly use JPG extension
                left_img_path = os.path.join(test_dir, f"frame_{self.calibration_frame_number:04d}_LeftCamera.jpg")
                right_img_path = os.path.join(test_dir, f"frame_{self.calibration_frame_number:04d}_RightCamera.jpg")
                
                self.logger.info(f"Using test images from: {test_dir}")
            else:
                self.logger.info(f"Using calibration images from settings")
            
            # Load the left image (JPG only)
            if os.path.exists(left_img_path) and left_img_path.lower().endswith('.jpg'):
                self.left_pixmap = QPixmap(left_img_path)
                if self.left_pixmap.isNull():
                    raise ValueError(f"Failed to load left image: {left_img_path}")
            else:
                raise FileNotFoundError(f"Left image not found or not JPG: {left_img_path}")
                
            # Load the right image (JPG only)
            if os.path.exists(right_img_path) and right_img_path.lower().endswith('.jpg'):
                self.right_pixmap = QPixmap(right_img_path)
                if self.right_pixmap.isNull():
                    raise ValueError(f"Failed to load right image: {right_img_path}")
            else:
                raise FileNotFoundError(f"Right image not found or not JPG: {right_img_path}")
            
            # Store resolution information
            self.left_resolution = (self.left_pixmap.width(), self.left_pixmap.height())
            self.right_resolution = (self.right_pixmap.width(), self.right_pixmap.height())
            
            # Detect standard resolution
            self.resolution_name = self._detect_resolution(self.left_resolution)
            self.logger.info(f"Detected resolution: {self.resolution_name} ({self.left_resolution[0]}x{self.left_resolution[1]})")
            
            # Display the loaded images
            self._display_images()
            
        except Exception as e:
            self.logger.error(f"Error loading calibration images: {str(e)}")
            
            # Create a warning message dialog with attempted paths
            warning_msg = (
                f"Failed to load calibration images:\n{str(e)}\n\n"
                f"Attempted paths:\n"
                f"Left: {left_img_path}\n"
                f"Right: {right_img_path}"
            )
            
            QMessageBox.warning(self, "Image Loading Error", warning_msg)
    
    def _detect_resolution(self, resolution):
        """Detect the standard resolution name based on image dimensions"""
        width, height = resolution
        
        # Check standard resolutions with some tolerance
        for name, (std_width, std_height) in self.point_io.STANDARD_RESOLUTIONS.items():
            # Allow small variations (5%)
            width_diff = abs(width - std_width) / std_width
            height_diff = abs(height - std_height) / std_height
            
            if width_diff <= 0.05 and height_diff <= 0.05:
                return name
        
        # If no exact match, classify based on height
        if height >= 900:
            return "1080p"
        elif height >= 400 and height < 900:
            return "480p"
        else:
            return "280p" 