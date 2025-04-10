"""
Monitoring Tab Module

This module provides the main monitoring interface for the Tennis Ball Tracker system.
It displays the real-time ball tracking, status information, and controls.
"""

import os
import time
import random
import json
from PySide6.QtCore import Qt, Slot, QSize, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSlider, QComboBox, QGroupBox, QGridLayout, QFrame, QSplitter,
    QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage, QFont, QPainter

from src.views.widgets.player_controls import PlayerControls
from src.views.widgets.fpga_connection_panel import FpgaConnectionPanel
from src.models.app_state import AppState
from src.controllers.image_manager import ImageManager
from src.controllers.image_player_controller import ImagePlayerController
from src.controllers.simulation_controller import SimulationController
from src.controllers.ball_status_display_manager import BallStatusDisplayManager
from src.controllers.image_display_manager import ImageDisplayManager
from src.controllers.calibration_overlay_manager import CalibrationOverlayManager
from src.controllers.ball_detection_controller import BallDetectionController
from src.utils.logger import Logger
from src.utils.settings_manager import SettingsManager
from src.utils.ui_theme import (
    get_group_box_style, get_label_style, get_button_style, 
    get_combobox_style, get_separator_style, get_message_box_style,
    get_camera_image_style
)
from src.constants.ui_constants import (
    PRIMARY_COLOR, SUCCESS_COLOR, ERROR_COLOR, WARNING_COLOR, 
    INFO_COLOR, BG_LIGHT, TEXT_PRIMARY, BORDER_DARK,
    STATUS_STYLE_BASE, STATUS_NOT_DETECTED, STATUS_IN, STATUS_OUT,
    STATUS_OUT_OF_BOUNDS, STATUS_IN_SERVICE, STATUS_FAULT,
    DEFAULT_FRAME_IMAGE_PATH, CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT,
    CAMERA_IMAGE_WIDTH, CAMERA_IMAGE_HEIGHT, RESIZE_TIMER_DELAY,
    ASPECT_RATIO_16_9, TRANSPARENT_STYLE
)


class MonitoringTab(QWidget):
    """
    Monitoring tab for real-time tennis ball tracking and FPGA analysis.
    
    This tab provides:
    - Real-time 3D visualization of tennis ball movement
    - FPGA analysis view for in/out determination
    - LED display for visualizing in/out status
    - Playback controls for animation control
    - COM port connection for FPGA communication
    """
    
    def __init__(self, parent=None):
        super(MonitoringTab, self).__init__(parent)
        
        # Get singleton instances
        self.app_state = AppState.instance()
        self.logger = Logger.instance()
        self.image_manager = ImageManager.instance()
        self.settings_manager = SettingsManager.instance()
        
        # Initialize controllers
        self._init_controllers()
        
        # Set up the UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Timer for delayed resize events
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._delayed_resize)
        
        self.logger.debug("MonitoringTab initialized")
        
        # Load and display the first frame if available
        self._load_initial_image()
    
    def _init_controllers(self):
        """Initialize controllers"""
        # Image player controller with default speed multiplier (1.0 = 1000 fps)
        self.image_player = ImagePlayerController()
        
        # Ensure playback speed is set to 1000 fps consistently across all components
        self.settings_manager.set("playback_speed", 1000)
        self.app_state.speed = 1.0
        
        # Simulation controller
        self.simulation = SimulationController()
        
        # Image display manager (initialized after UI is created)
        self.image_display_manager = None
        
        # Calibration overlay manager
        self.overlay_manager = CalibrationOverlayManager()
        
        # Ball status display manager (initialized after UI is created)
        self.ball_status_manager = None
        
        # Ball detection controller - using qt_singleton pattern
        self.ball_detection = BallDetectionController.instance()
    
    class CameraViewLayout:
        """
        Camera view layout component that standardizes camera visualization
        
        This class creates a standard camera view layout with title, image and FPS counter.
        """
        
        def __init__(self, parent, title, group_title):
            """
            Initialize camera view layout with standard elements
            
            Args:
                parent: Parent widget
                title: Camera view title
                group_title: Title for the group box
            """
            self.parent = parent
            self.title = title
            self.group_title = group_title
            
            # Create container widget for frame and image
            self.image_container = QWidget()
            self.image_container.setMinimumSize(CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT)  # 16:9 ratio (640x360)
            self.image_container.setObjectName("imageContainer")
            
            # Use absolute positioning for precise overlay placement
            self.image_container.setLayout(QVBoxLayout())
            self.image_container.layout().setContentsMargins(0, 0, 0, 0)
            self.image_container.layout().setSpacing(0)
            
            # Frame background (outer frame)
            self.frame_label = QLabel(self.image_container)
            self.frame_label.setObjectName("frameLabel")
            self.frame_label.setAlignment(Qt.AlignCenter)
            self.frame_label.setGeometry(0, 0, CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT)  # 16:9 ratio (640x360)
            
            # Actual image label for camera images
            self.image_label = QLabel(self.image_container)
            self.image_label.setObjectName("imageLabel")
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setFixedSize(CAMERA_IMAGE_WIDTH, CAMERA_IMAGE_HEIGHT)  # 16:9 ratio (480x270)
            self.image_label.setStyleSheet(TRANSPARENT_STYLE)
            
            # Center the image label in the container
            self.image_label.setGeometry(
                (CAMERA_FRAME_WIDTH - CAMERA_IMAGE_WIDTH) // 2,  # Center horizontally
                (CAMERA_FRAME_HEIGHT - CAMERA_IMAGE_HEIGHT) // 2,  # Center vertically
                CAMERA_IMAGE_WIDTH, CAMERA_IMAGE_HEIGHT
            )
            
            # Explicitly set z-order
            self.frame_label.lower()  # Frame to the bottom
            self.image_label.raise_() # Image above frame
            
            # Create group box and layout
            self.group_box = QGroupBox(group_title)
            self.group_box.setStyleSheet(get_group_box_style())
            self.layout = QVBoxLayout(self.group_box)
            self.layout.setContentsMargins(10, 25, 10, 10)
            
            # Camera title
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet(get_label_style())
            self.layout.addWidget(title_label)
            
            # Add image container to the layout
            self.layout.addWidget(self.image_container, 0, Qt.AlignCenter)
            
            # FPS counter
            self.fps_label = QLabel("0/0 fps")
            self.fps_label.setAlignment(Qt.AlignRight)
            self.fps_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 12px; padding: 5px;")
            self.layout.addWidget(self.fps_label)
            
            # Load the frame background
            self._load_frame_background()
            
        def _load_frame_background(self):
            """Load the frame_16_9.png background image"""
            frame_path = DEFAULT_FRAME_IMAGE_PATH
            if os.path.exists(frame_path):
                frame_pixmap = QPixmap(frame_path)
                if not frame_pixmap.isNull():
                    # Scale frame to fit the frame label, maintain 16:9 ratio
                    scaled_frame = frame_pixmap.scaled(
                        CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT, 
                        Qt.IgnoreAspectRatio,  # Ensure exact 16:9 ratio is maintained
                        Qt.SmoothTransformation
                    )
                    self.frame_label.setPixmap(scaled_frame)
                    
                    # Ensure proper z-order is maintained after setting the pixmap
                    self.frame_label.lower()  # Frame to the bottom
                    self.image_label.raise_() # Image above frame
    
    def _setup_ui(self):
        """Set up the user interface for the monitoring tab"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        # Viewer layout - horizontally arrange left and right camera views
        viewers_layout = QHBoxLayout()
        viewers_layout.setSpacing(5)
        viewers_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create left camera view
        left_camera_view = self.CameraViewLayout(self, "Left Camera View", "Ball Tracking")
        self.left_camera_image = left_camera_view.image_label
        self.left_fps_label = left_camera_view.fps_label
        
        # Player controls
        self.player_controls = PlayerControls()
        left_camera_view.layout.addWidget(self.player_controls)
        
        # Ball detection controls
        detection_controls = QHBoxLayout()
        detection_controls.setContentsMargins(5, 5, 5, 5)
        detection_controls.setSpacing(10)
        
        # Ball detection toggle button
        self.detection_button = QPushButton("Start Ball Detection")
        self.detection_button.setStyleSheet(get_button_style())
        self.detection_button.clicked.connect(self._toggle_ball_detection)
        detection_controls.addWidget(self.detection_button)
        
        # Detection processing info label
        self.detection_info_label = QLabel("Detection inactive")
        self.detection_info_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.detection_info_label.setStyleSheet(get_label_style())
        detection_controls.addWidget(self.detection_info_label)
        
        left_camera_view.layout.addLayout(detection_controls)
        
        # Timeline slider (hidden)
        timeline_container = QWidget()
        timeline_container.setMaximumHeight(1)
        timeline_container.setVisible(False)
        left_camera_view.layout.addWidget(timeline_container)
        
        # Create right camera view
        right_camera_view = self.CameraViewLayout(self, "Right Camera View", "Ball Status Analysis")
        self.right_camera_image = right_camera_view.image_label
        self.right_fps_label = right_camera_view.fps_label
        
        # Create a separate container for explanation below the image
        explanation_container = QWidget()
        explanation_layout = QVBoxLayout(explanation_container)
        explanation_layout.setContentsMargins(5, 5, 5, 5)
        
        # Explanation label
        explanation_label = QLabel(
            "This panel displays ball status and FPGA analysis results. "
            "Connect to the FPGA or use the simulation button to see data."
        )
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet(get_label_style(is_description=True))
        explanation_layout.addWidget(explanation_label)
        
        # Add explanation container after the image
        right_camera_view.layout.addWidget(explanation_container)
        
        # Status info grid
        info_grid = QGridLayout()
        info_grid.setContentsMargins(5, 5, 5, 5)
        info_grid.setSpacing(5)
        
        # Status label
        self.ball_status_label = QLabel("Not Detected")
        self.ball_status_label.setAlignment(Qt.AlignCenter)
        self.ball_status_label.setStyleSheet(STATUS_NOT_DETECTED)
        info_grid.addWidget(self.ball_status_label, 0, 0, 1, 2)
        
        # Position label
        self.ball_position_label = QLabel("X: 0.00, Y: 0.00, Z: 0.00")
        self.ball_position_label.setAlignment(Qt.AlignCenter)
        self.ball_position_label.setStyleSheet(get_label_style())
        info_grid.addWidget(self.ball_position_label, 1, 0, 1, 2)
        
        # Detection confidence label
        self.detection_confidence_label = QLabel("Confidence: 0.00")
        self.detection_confidence_label.setAlignment(Qt.AlignCenter)
        self.detection_confidence_label.setStyleSheet(get_label_style())
        info_grid.addWidget(self.detection_confidence_label, 2, 0, 1, 2)
        
        right_camera_view.layout.addLayout(info_grid)
        
        # Add stretch
        right_camera_view.layout.addStretch()
        
        # FPGA connection panel
        self.fpga_connection_panel = FpgaConnectionPanel()
        right_camera_view.layout.addWidget(self.fpga_connection_panel)
        
        # Simulation button
        self.simulation_button = QPushButton("Start Simulation")
        self.simulation_button.setStyleSheet(get_button_style())
        self.simulation_button.clicked.connect(self._toggle_simulation)
        right_camera_view.layout.addWidget(self.simulation_button)
        
        # Store the group boxes to access them later
        self.tracking_group = left_camera_view.group_box
        self.fpga_group = right_camera_view.group_box
        
        # Add left and right groups to viewer layout (with equal ratio)
        viewers_layout.addWidget(self.tracking_group, 1)
        viewers_layout.addWidget(self.fpga_group, 1)
        
        # Add viewer layout to main layout
        self.layout.addLayout(viewers_layout)
        
        # Initialize display managers
        self.image_display_manager = ImageDisplayManager(
            self.left_camera_image,
            self.right_camera_image
        )
        
        self.ball_status_manager = BallStatusDisplayManager(
            self.ball_status_label
        )
    
    def _connect_signals(self):
        """Connect signals to slots"""
        # Image player controller signals
        self.image_player.fps_updated.connect(self._update_fps_display)
        self.image_player.images_updated.connect(self._on_images_updated)
        
        # Image display manager signals
        self.image_display_manager.images_updated.connect(self._process_overlay)
        
        # App state signals
        self.app_state.ball_position_changed.connect(self._update_tracking_view)
    
    @Slot(int)
    def _on_images_updated(self, frame_number):
        """
        Handle images updated signal from ImagePlayerController
        
        Args:
            frame_number: Current frame number
        """
        # Update images using ImageDisplayManager
        self.image_display_manager.update_displayed_images(frame_number)
        
        # Process overlay immediately after updating images
        self._process_overlay(frame_number)
        
        # Ensure images are properly scaled to fixed size
        self._apply_fixed_size_to_images(self.image_display_manager.images)
    
    def _apply_fixed_size_to_images(self, images):
        """
        Apply fixed height to the images, maintaining 16:9 aspect ratio and adding padding
        
        Args:
            images: Dictionary of camera images (left, right)
        
        Returns:
            Dictionary of resized images
        """
        resized_images = {}
        
        for camera, image in images.items():
            if image is not None:
                # Get original image dimensions
                orig_width = image.width()
                orig_height = image.height()
                
                # Target dimensions using 16:9 aspect ratio
                target_width = CAMERA_IMAGE_WIDTH  # Must maintain 16:9 ratio with target_height
                target_height = CAMERA_IMAGE_HEIGHT # 16:9 ratio with 480 width
                
                # Calculate new dimensions to fit within the frame while enforcing 16:9 ratio
                # Determine if we need to scale by width or height
                if (orig_width / orig_height) > (16 / 9):
                    # Image is wider than 16:9, constrain by width
                    new_width = target_width
                    new_height = int(new_width * 9 / 16)  # Force 16:9 ratio
                else:
                    # Image is taller than 16:9, constrain by height
                    new_height = target_height
                    new_width = int(new_height * 16 / 9)  # Force 16:9 ratio
                
                # Create scaled image using Qt's scaling
                scaled_image = image.scaled(
                    new_width, new_height,
                    Qt.IgnoreAspectRatio,  # Force exact 16:9 ratio
                    Qt.SmoothTransformation  # Better quality scaling
                )
                
                # Store the scaled result
                resized_images[camera] = scaled_image
            else:
                resized_images[camera] = None
                
        return resized_images
    
    @Slot(int)
    def _process_overlay(self, frame_number):
        """
        Process calibration point overlay for right camera image
        
        Args:
            frame_number: Current frame number
        """
        # Get the right camera pixmap from image display manager
        right_pixmap = self.image_display_manager.get_right_original_pixmap()
        if not right_pixmap:
            return
            
        # Check if we have calibration points for the right camera
        if self.overlay_manager.has_calibration_points("right_camera"):
            # Create overlay with calibration points
            overlay_pixmap = self.overlay_manager.create_overlay(
                "right_camera", 
                right_pixmap,
                frame_number
            )
            
            # Update right camera image with overlay
            if overlay_pixmap:
                # Get original dimensions
                orig_width = overlay_pixmap.width()
                orig_height = overlay_pixmap.height()
                
                # Target dimensions using 16:9 aspect ratio
                target_width = CAMERA_IMAGE_WIDTH  # Must maintain 16:9 ratio with target_height
                target_height = CAMERA_IMAGE_HEIGHT  # 16:9 ratio with 480 width
                
                # Calculate dimensions that enforce 16:9 ratio
                if (orig_width / orig_height) > (16 / 9):
                    # Image is wider than 16:9, constrain by width
                    new_width = target_width
                    new_height = int(new_width * 9 / 16)  # Force 16:9 ratio
                else:
                    # Image is taller than 16:9, constrain by height
                    new_height = target_height
                    new_width = int(new_height * 16 / 9)  # Force 16:9 ratio
                
                # Scale the overlay with correct aspect ratio
                scaled_overlay = overlay_pixmap.scaled(
                    new_width, new_height,
                    Qt.IgnoreAspectRatio,  # Force exact 16:9 ratio
                    Qt.SmoothTransformation
                )
                
                # Set the scaled overlay directly to the image label
                self.right_camera_image.setPixmap(scaled_overlay)
        # No else clause needed - if no calibration points, the base image is already displayed by ImageDisplayManager
    
    @Slot(float, float, float)
    def _update_tracking_view(self, x, y, z):
        """
        Update the tracking view when ball position changes
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
        """
        # Only update the text display if we're not showing an image
        if self.image_manager.get_total_images() == 0:
            # This is a placeholder. In a real implementation, this would 
            # update a 3D render or OpenGL view.
            self.ball_position_label.setText(f"X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}")
    
    @Slot(float, float)
    def _update_fps_display(self, current_fps, target_fps=None):
        """
        Update FPS display
        
        Args:
            current_fps: Current FPS
            target_fps: Target FPS (defaults to ImagePlayerController.BASE_FPS if None)
        """
        # Use ImagePlayerController.BASE_FPS as default if target_fps is not provided
        if target_fps is None:
            target_fps = ImagePlayerController.BASE_FPS
            
        # Update FPS display with improved format
        self.left_fps_label.setText(f"{current_fps:.1f}/{target_fps} fps")
        self.right_fps_label.setText(f"{current_fps:.1f}/{target_fps} fps")
    
    def _toggle_ball_detection(self):
        """Toggle ball detection on/off"""
        # Call the ball detection controller's toggle method
        detection_active = self.ball_detection.toggle_detection(self._on_ball_detection_result)
        
        # Update button text based on state
        if detection_active:
            self.detection_button.setText("Stop Ball Detection")
            self.detection_info_label.setText("Detection active")
        else:
            self.detection_button.setText("Start Ball Detection")
            self.detection_info_label.setText("Detection inactive")
            
        self.logger.debug(f"Ball detection {'activated' if detection_active else 'deactivated'}")
    
    def _on_ball_detection_result(self, detection_result, fps, process_time):
        """
        Handle ball detection results
        
        Args:
            detection_result: Detection result dictionary
            fps: Current detection FPS
            process_time: Processing time in seconds
        """
        try:
            # Update detection info label
            self.detection_info_label.setText(f"Detection: {fps:.1f} fps ({process_time*1000:.1f}ms)")
            
            # Get left and right camera detections
            left_detection = detection_result.get('left')
            right_detection = detection_result.get('right')
            
            # Update image overlays
            if left_detection:
                self.image_display_manager.set_ball_detection_result('left', left_detection)
            
            if right_detection:
                self.image_display_manager.set_ball_detection_result('right', right_detection)
            
            # Process 3D position if available
            position_data = detection_result.get('position')
            if position_data and position_data.get('has_position'):
                # Extract 3D position
                position = position_data.get('position')
                confidence = position_data.get('confidence', 0.0)
                
                # Update position display
                if position:
                    x, y, z = position
                    self.ball_position_label.setText(f"X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}")
                    
                    # Update 3D position overlay
                    self.image_display_manager.set_3d_position(position)
                    
                    # Update position in app state
                    self.app_state.set_ball_position(x, y, z)
                
                # Update confidence display
                self.detection_confidence_label.setText(f"Confidence: {confidence:.2f}")
                
                # Update ball status based on confidence
                if confidence > 0.7:
                    self.ball_status_manager.set_status('detected')
                elif confidence > 0.3:
                    self.ball_status_manager.set_status('uncertain')
                else:
                    self.ball_status_manager.set_status('not_detected')
            else:
                # No valid position - update UI to reflect that
                self.ball_status_manager.set_status('not_detected')
                self.detection_confidence_label.setText(f"Confidence: 0.00")
            
        except Exception as e:
            self.logger.error(f"Error handling ball detection result: {e}")
    
    def _load_initial_image(self):
        """Load and display the first frame if available"""
        # Only display default placeholder for camera views
        frame_image_path = DEFAULT_FRAME_IMAGE_PATH
        if os.path.exists(frame_image_path):
            # Load and stretch the frame for both camera views
            frame_pixmap = QPixmap(frame_image_path)
            if not frame_pixmap.isNull() and hasattr(self, 'left_camera_image') and hasattr(self, 'right_camera_image'):
                # Scale frame to exact 16:9 ratio (640x360)
                stretched_frame = frame_pixmap.scaled(
                    CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT,
                    Qt.IgnoreAspectRatio,
                    Qt.SmoothTransformation
                )
                
                # Update the frame labels if they exist
                if hasattr(self, 'tracking_group') and hasattr(self, 'fpga_group'):
                    # Find the frame labels and update them
                    for view in [self.tracking_group, self.fpga_group]:
                        for child in view.findChildren(QLabel):
                            if child != self.left_camera_image and child != self.right_camera_image:
                                if hasattr(child, 'objectName') and 'frameLabel' in child.objectName():
                                    child.setPixmap(stretched_frame)
            
            # Place instruction label below images
            instruction_label = QLabel("Please use File > Open Image Folder to load tennis match images.", self)
            instruction_label.setAlignment(Qt.AlignCenter)
            instruction_label.setStyleSheet(f"{get_label_style(is_description=True)} font-size: 14px; padding: 10px; margin: 10px;")
            instruction_label.setWordWrap(True)
            
            # Add the label to the main area
            if hasattr(self, 'layout'):
                # Remove any existing instruction labels
                for i in reversed(range(self.layout.count())):
                    widget = self.layout.itemAt(i).widget()
                    if isinstance(widget, QLabel) and widget != self.left_camera_image and widget != self.right_camera_image:
                        if 'load' in widget.text().lower() or 'image' in widget.text().lower():
                            widget.deleteLater()
                
                # Add the new instruction label
                self.layout.addWidget(instruction_label)
            
            self.logger.debug("Loading image placeholder complete")
        else:
            self.logger.warning("Default frame placeholder image not found")
    
    def resizeEvent(self, event):
        """
        Handle resize events to resize images when the container size changes
        
        Args:
            event: Resize event
        """
        super(MonitoringTab, self).resizeEvent(event)
        
        # Start or restart the resize timer (300ms delay)
        self._resize_timer.start(RESIZE_TIMER_DELAY)
        
        # Accept the event
        event.accept()
    
    def _delayed_resize(self):
        """Handle delayed resize events by rescaling existing pixmaps."""
        # Use ImageDisplayManager to handle resize
        if self.image_display_manager:
            self.image_display_manager.handle_resize()
            
            # Process overlay after resize
            if self.app_state.current_frame >= 0:
                self._process_overlay(self.app_state.current_frame + 1)
            
            # Apply fixed size constraints using the images property
            self._apply_fixed_size_to_images(self.image_display_manager.images)
    
    def _toggle_simulation(self):
        """Toggle the simulation on/off"""
        if not hasattr(self, '_simulation_running'):
            self._simulation_running = False
        
        self._simulation_running = not self._simulation_running
        
        if self._simulation_running:
            self.simulation_button.setText("Stop Simulation")
            self.simulation.start_simulation()
            self.logger.debug("Simulation started")
        else:
            self.simulation_button.setText("Start Simulation")
            self.simulation.stop_simulation()
            self.logger.debug("Simulation stopped")
    
    def update_fpga_settings(self, settings):
        """
        Update FPGA connection settings from the settings tab
        
        Args:
            settings: Dictionary containing FPGA settings
        """
        # Pass settings to FPGA connection panel
        self.fpga_connection_panel.update_fpga_settings(settings)

    @Slot(dict)
    def update_images(self, images):
        """Update images for both cameras from a dict with 'left' and 'right' keys"""
        if not hasattr(self, 'is_visible') or not self.is_visible:
            return
            
        # Resize images to fit within the frame
        resized_images = self._apply_fixed_size_to_images(images)
        
        # Update left camera image if available
        if 'left' in resized_images and resized_images['left'] is not None:
            self.left_camera_image.setPixmap(resized_images['left'])
            
        # Update right camera image if available
        if 'right' in resized_images and resized_images['right'] is not None:
            self.right_camera_image.setPixmap(resized_images['right'])
            
        # Update the timestamp and frame number display
        if hasattr(self, '_update_frame_info'):
            self._update_frame_info()