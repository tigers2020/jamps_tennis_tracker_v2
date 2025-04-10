"""
Player Controls Widget Module

This module defines a widget for controlling the playback of tennis ball animations.
It provides play, pause, stop, rewind controls and a time slider.
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QSlider, 
                              QLabel, QFrame, QVBoxLayout)
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QIcon
import math
import os
import time
from datetime import timedelta
import logging

from src.models.app_state import AppState
from src.utils.logger import Logger
from src.utils.settings_manager import SettingsManager
from src.utils.ui_theme import (
    get_player_button_style, get_speed_button_style, get_player_slider_style
)

class PlayerControls(QWidget):
    """
    Player controls widget for controlling the playback of tennis ball animations.
    
    This widget provides:
    - Play, pause, stop, rewind, and fast forward buttons
    - Time slider for scrubbing through the animation
    - Speed control for adjusting playback speed
    """
    
    # Define constants
    MIN_FPS = 10        # Minimum playback speed: 10 fps
    DEFAULT_FPS = 1000  # Default playback speed: 1000 fps
    MAX_FPS = 3000      # Maximum playback speed: 3000 fps
    
    # Define speed presets
    SPEED_PRESETS = {
        "Slow": 100,      # 100 fps
        "Medium": 500,      # 500 fps
        "Normal": 1000,     # 1000 fps
        "Fast": 2000,     # 2000 fps
        "Ultra": 3000     # 3000 fps
    }
    
    def __init__(self, parent=None):
        super(PlayerControls, self).__init__(parent)
        
        # Get singleton instances
        self.app_state = AppState.instance()
        self.logger = Logger.instance()
        self.settings_manager = SettingsManager.instance()
        
        # Set up the UI
        self.setup_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Load saved playback speed
        self.load_saved_playback_speed()
        
        self.logger.debug("PlayerControls initialized")
    
    def load_saved_playback_speed(self):
        """Load saved playback speed settings"""
        # Always use DEFAULT_FPS (1000) regardless of saved settings
        saved_fps = self.DEFAULT_FPS
        
        # Set slider value
        slider_value = self.fps_to_slider_value(saved_fps)
        self.speed_slider.setValue(slider_value)
        
        # Update app state
        self.app_state.speed = saved_fps / 1000.0
        
        self.logger.debug(f"Set playback speed to: {saved_fps} fps")
    
    def setup_ui(self):
        """Set up the user interface"""
        # Create icons directory if it doesn't exist
        icons_dir = os.path.join("src", "resources", "images", "icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Upper section - time display and slider
        time_layout = QHBoxLayout()
        time_layout.setSpacing(10)
        
        # Time display
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: white; font-size: 12px;")
        time_layout.addWidget(self.time_label)
        
        # Time slider
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.setStyleSheet(get_player_slider_style())
        self.logger.debug(f"Time slider initialized: range=0-100")
        time_layout.addWidget(self.time_slider)
        
        self.layout.addLayout(time_layout)
        
        # Middle section - playback controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)
        
        # Add stretch before buttons to center them
        controls_layout.addStretch(1)
        
        # Playback buttons with modern icons
        self.rewind_btn = QPushButton()
        self.rewind_btn.setIcon(QIcon(os.path.join(icons_dir, "rewind.png")))
        self.rewind_btn.setToolTip("Rewind")
        
        self.prev_frame_btn = QPushButton()
        self.prev_frame_btn.setIcon(QIcon(os.path.join(icons_dir, "prev_frame.png")))
        self.prev_frame_btn.setToolTip("Previous Frame")
        
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(QIcon(os.path.join(icons_dir, "play.png")))
        self.play_pause_btn.setToolTip("Play/Pause")
        self.play_pause_btn.setCheckable(True)
        
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(QIcon(os.path.join(icons_dir, "stop.png")))
        self.stop_btn.setToolTip("Stop")
        
        self.next_frame_btn = QPushButton()
        self.next_frame_btn.setIcon(QIcon(os.path.join(icons_dir, "next_frame.png")))
        self.next_frame_btn.setToolTip("Next Frame")
        
        self.forward_btn = QPushButton()
        self.forward_btn.setIcon(QIcon(os.path.join(icons_dir, "forward.png")))
        self.forward_btn.setToolTip("Fast Forward")
        
        # Add buttons to layout with fixed size and icon size
        for btn in [self.rewind_btn, self.prev_frame_btn, self.play_pause_btn, 
                    self.stop_btn, self.next_frame_btn, self.forward_btn]:
            btn.setStyleSheet(get_player_button_style())
            btn.setFixedSize(45, 45)
            btn.setIconSize(QSize(24, 24))
            controls_layout.addWidget(btn)
        
        # Add stretch after buttons to center them
        controls_layout.addStretch(1)
        
        self.layout.addLayout(controls_layout)
        
        # Lower section - speed control
        speed_layout = QHBoxLayout()
        speed_layout.setSpacing(10)
        
        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background: rgba(85, 85, 85, 0.3);")
        self.layout.addWidget(separator)
        
        # Speed control
        speed_label = QLabel("Speed:")
        speed_label.setStyleSheet("color: white; font-size: 12px;")
        speed_layout.addWidget(speed_label)
        
        # Add speed preset buttons
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(5)
        for preset_name, preset_fps in self.SPEED_PRESETS.items():
            speed_btn = QPushButton(preset_name)
            speed_btn.setStyleSheet(get_speed_button_style())
            speed_btn.clicked.connect(lambda checked, fps=preset_fps: self.set_speed_preset(fps))
            speed_btn.setToolTip(f"{preset_name} speed: {preset_fps} fps")
            preset_layout.addWidget(speed_btn)
        
        # Add preset buttons to vertical layout
        preset_container = QWidget()
        preset_container.setLayout(preset_layout)
        self.layout.addWidget(preset_container)
        
        # Speed slider
        self.speed_slider = QSlider(Qt.Horizontal)
        # FPS range is logarithmically adjusted (log scale)
        # Slider range is set to 0-1000 and converted internally
        self.speed_slider.setRange(0, 1000)
        # Set initial value (slider value corresponding to 1000 fps)
        initial_slider_value = self.fps_to_slider_value(self.DEFAULT_FPS)
        self.speed_slider.setValue(initial_slider_value)
        self.speed_slider.setStyleSheet(get_player_slider_style())
        speed_layout.addWidget(self.speed_slider)
        
        # Initial label text
        self.speed_label = QLabel(f"1.0x (1000 fps)")
        self.speed_label.setStyleSheet("color: white; font-size: 12px;")
        speed_layout.addWidget(self.speed_label)
        
        # Add the speed layout to the main layout
        self.layout.addLayout(speed_layout)
        
        # Add slider tracking state variable
        self.slider_tracking = False
    
    def connect_signals(self):
        """Connect signals to slots"""
        # Button click events
        self.play_pause_btn.clicked.connect(self.on_play_pause)
        self.stop_btn.clicked.connect(self.on_stop)
        self.rewind_btn.clicked.connect(self.on_rewind)
        self.forward_btn.clicked.connect(self.on_forward)
        self.prev_frame_btn.clicked.connect(self.on_prev_frame)
        self.next_frame_btn.clicked.connect(self.on_next_frame)
        
        # Slider value changed events
        self.time_slider.valueChanged.connect(self.on_time_changed)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        
        # Connect app_state signals to UI update slots
        self.app_state.current_frame_changed.connect(self.update_time_display)
        self.app_state.total_frames_changed.connect(self.update_time_display)
        self.app_state.speed_changed.connect(self.update_speed_display)
        self.app_state.playback_state_changed.connect(self.update_control_states)
        
        # Time slider tracking event connection
        self.time_slider.sliderPressed.connect(self.on_slider_pressed)
        self.time_slider.sliderReleased.connect(self.on_slider_released)
    
    def on_play_pause(self, checked):
        """Handle play/pause button toggle"""
        if checked:
            self.logger.debug("Play/Pause button: Playing")
            self.play_pause_btn.setIcon(QIcon(os.path.join("src", "resources", "images", "icons", "pause.png")))
            self.app_state.playback_state = 'play'
        else:
            self.logger.debug("Play/Pause button: Paused")
            self.play_pause_btn.setIcon(QIcon(os.path.join("src", "resources", "images", "icons", "play.png")))
            self.app_state.playback_state = 'pause'
    
    def on_stop(self):
        """Handle stop button click"""
        self.logger.debug("Stop button clicked")
        self.app_state.playback_state = 'stop'
        self.app_state.current_frame = 0
    
    def on_rewind(self):
        """Handle rewind button click"""
        self.logger.debug("Rewind button clicked")
        # Move back 10 frames
        current = self.app_state.current_frame
        self.app_state.current_frame = max(0, current - 10)
    
    def on_forward(self):
        """Handle fast forward button click"""
        self.logger.debug("Fast forward button clicked")
        # Move forward 10 frames
        current = self.app_state.current_frame
        total = self.app_state.total_frames
        if total > 0:
            self.app_state.current_frame = min(total - 1, current + 10)
    
    def on_prev_frame(self):
        """Handle previous frame button click"""
        self.logger.debug("Previous frame button clicked")
        # Move exactly one frame back
        current = self.app_state.current_frame
        self.app_state.current_frame = max(0, current - 1)
    
    def on_next_frame(self):
        """Handle next frame button click"""
        self.logger.debug("Next frame button clicked")
        # Move exactly one frame forward
        current = self.app_state.current_frame
        total = self.app_state.total_frames
        if total > 0:
            self.app_state.current_frame = min(total - 1, current + 1)
    
    def on_time_changed(self, value):
        """Handle time slider value change
        
        Args:
            value (int): The slider value (0-100)
        """
        self.logger.debug(f"on_time_changed called: value={value}, tracking={self.slider_tracking}, total_frames={self.app_state.total_frames}")
        if self.app_state.total_frames <= 0:
            return
            
        # Convert slider value to frame number
        max_val = self.time_slider.maximum()
        total_frames = max(1, self.app_state.total_frames - 1)  # Prevent division by zero
        frame = int((value / max_val) * total_frames)
        
        # Update frame only if significantly different to avoid feedback loops
        # We don't need the threshold check anymore as we're using blockSignals
        self.logger.debug(f"Time slider changed: value={value}, max_val={max_val}, total_frames={total_frames}, calculated frame={frame}")
        self.app_state.current_frame = frame
    
    def on_speed_changed(self, value):
        """Handle speed slider value changed"""
        # Convert slider value to FPS
        fps = self.slider_value_to_fps(value)
        
        # Calculate speed multiplier (based on 1000 fps)
        speed_multiplier = fps / 1000.0
        
        self.logger.debug(f"Speed slider changed: value={value}, FPS={fps}")
        
        # Update app state
        self.app_state.speed = speed_multiplier
    
    def set_speed_preset(self, fps):
        """Set to preset speed"""
        # Set slider value based on corresponding FPS
        slider_value = self.fps_to_slider_value(fps)
        self.speed_slider.setValue(slider_value)
        # on_speed_changed function will be called to update app state
    
    def fps_to_slider_value(self, fps):
        """FPS value to slider value (log scale)"""
        # Convert to 0-1000 range
        if fps <= 0:
            return 0
        
        # Convert to log scale value between MIN_FPS and MAX_FPS
        log_min = math.log(self.MIN_FPS)
        log_max = math.log(self.MAX_FPS)
        log_value = math.log(fps)
        
        # Normalize to 0-1000 range
        normalized = (log_value - log_min) / (log_max - log_min)
        slider_value = int(normalized * 1000)
        
        return max(0, min(1000, slider_value))
    
    def slider_value_to_fps(self, value):
        """Slider value to FPS (log scale)"""
        # Convert to log scale
        normalized = value / 1000.0
        log_min = math.log(self.MIN_FPS)
        log_max = math.log(self.MAX_FPS)
        log_value = log_min + normalized * (log_max - log_min)
        
        # Convert to FPS
        fps = math.exp(log_value)
        
        # Round to nearest integer
        return max(self.MIN_FPS, min(self.MAX_FPS, int(fps)))
    
    @Slot(int)
    @Slot(int, int)
    def update_time_display(self, current_frame=None, total_frames=None):
        """Update the time display and slider position based on current and total frames.
        
        Args:
            current_frame (int, optional): Current frame number. If None, uses app_state value.
            total_frames (int, optional): Total number of frames. If None, uses app_state value.
        """
        if current_frame is None:
            current_frame = self.app_state.current_frame
        if total_frames is None:
            total_frames = self.app_state.total_frames
        
        # Display frame number starts from 1
        display_frame = current_frame + 1
        
        if total_frames > 0:
            # Display as frame numbers (1/480 format)
            self.time_label.setText(f"{display_frame}/{total_frames}")
            
            # Update slider position (prevent feedback loop)
            if not self.slider_tracking:
                # This was incorrectly calculating the slider position
                max_val = self.time_slider.maximum()
                slider_pos = int((current_frame / max(1, total_frames - 1)) * max_val)
                
                self.logger.debug(f"update_time_display: frame={current_frame}, total={total_frames}, max_val={max_val}, calculated_pos={slider_pos}, tracking={self.slider_tracking}")
                
                # Block signals during the update to prevent loops
                self.time_slider.blockSignals(True)
                self.time_slider.setValue(slider_pos)
                self.time_slider.blockSignals(False)
        else:
            self.time_label.setText("0/0")
            self.time_slider.setValue(0)
    
    @Slot(float)
    def update_speed_display(self, speed):
        """Update the speed display"""
        # Convert speed multiplier to fps
        fps = int(speed * 1000)
        
        # Show only FPS value
        self.speed_label.setText(f"{fps} fps")
        
        # Update slider position (avoid feedback loop)
        slider_value = self.fps_to_slider_value(fps)
        if self.speed_slider.value() != slider_value:
            self.speed_slider.blockSignals(True)
            self.speed_slider.setValue(slider_value)
            self.speed_slider.blockSignals(False)
    
    @Slot(str)
    def update_control_states(self, state):
        """
        Update the state of control buttons based on playback state
        
        Args:
            state: Current playback state ('play', 'pause', 'stop')
        """
        # Update play/pause button state
        self.play_pause_btn.setChecked(state == 'play')
        icons_dir = os.path.join("src", "resources", "images", "icons")
        self.play_pause_btn.setIcon(QIcon(os.path.join(icons_dir, "pause.png" if state == 'play' else "play.png")))
        
        # Enable/disable buttons based on state
        self.stop_btn.setEnabled(state != 'stop')
        
        # Visual feedback for stop button
        if state == 'stop':
            self.play_pause_btn.setChecked(False)
            self.play_pause_btn.setIcon(QIcon(os.path.join(icons_dir, "play.png")))
        
        # Visual feedback - highlight the active button
        self.play_pause_btn.setStyleSheet("" if state != 'play' else "background-color: #8af;")
    
    def update_speed(self, fps):
        """
        Update the playback speed from settings tab
        
        Args:
            fps: Frames per second (10-3000)
        """
        self.logger.debug(f"Updating speed from settings: {fps} fps")
        
        # Validate range and adjust if needed
        fps = max(self.MIN_FPS, min(self.MAX_FPS, fps))
        
        # Update slider without triggering signals
        slider_value = self.fps_to_slider_value(fps)
        self.speed_slider.blockSignals(True)
        self.speed_slider.setValue(slider_value)
        self.speed_slider.blockSignals(False)
        
        # Update speed display
        speed_multiplier = fps / 1000.0
        self.update_speed_display(speed_multiplier)
        
        # Update app state
        if self.app_state.speed != speed_multiplier:
            self.app_state.speed = speed_multiplier
    
    def on_slider_pressed(self):
        """Called when slider drag starts"""
        self.logger.debug(f"Slider drag started: current_value={self.time_slider.value()}")
        self.slider_tracking = True
        
    def on_slider_released(self):
        """Called when slider drag ends"""
        self.logger.debug(f"Slider drag ended: value={self.time_slider.value()}, total_frames={self.app_state.total_frames}")
        self.slider_tracking = False
        self.update_time_display() 