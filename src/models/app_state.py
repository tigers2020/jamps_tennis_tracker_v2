"""
Application State Management

This module provides a singleton class for managing global application state.
The AppState class uses Qt signals to notify UI components of state changes.
"""

from PySide6.QtCore import QObject, Signal
import logging

from src.models.singleton import qt_singleton

@qt_singleton
class AppState(QObject):
    """
    Global application state manager implemented as a Singleton.
    
    This class maintains all global state that needs to be shared across
    different components of the application. It uses Qt signals to notify
    subscribers when state changes occur.
    """
    
    # Define signals for state changes
    speed_changed = Signal(float)
    camera_position_changed = Signal(float, float, float)  # azimuth, elevation, distance
    ball_position_changed = Signal(float, float, float)    # x, y, z
    playback_state_changed = Signal(str)                   # 'play', 'pause', 'stop'
    current_frame_changed = Signal(int)
    total_frames_changed = Signal(int)
    led_state_changed = Signal(bool, float)                # in_bounds, blink_rate
    images_loaded_changed = Signal(list)
    current_image_changed = Signal(str)
    active_tab_changed = Signal(str)                       # active tab name

    def __init__(self):
        super(AppState, self).__init__()
        
        # Initialize state values
        self._speed = 1.0
        self._azimuth = 0.0
        self._elevation = 0.0
        self._distance = 10.0
        self._ball_position = (0.0, 0.0, 0.0)
        self._playback_state = 'stop'
        self._current_frame = 0
        self._total_frames = 0
        self._led_state = (True, 0.0)  # (in_bounds, blink_rate)
        self._file_path = ""
        self._image_paths = []
        self._current_image = ""
        self._active_tab = "home"  # Default active tab
    
    # Speed control
    @property
    def speed(self):
        """Get the current playback speed"""
        return self._speed
    
    @speed.setter
    def speed(self, value):
        """Set the playback speed and emit signal if changed"""
        if self._speed != value:
            self._speed = value
            self.speed_changed.emit(value)
    
    # Camera position control
    @property
    def camera_position(self):
        """Get the current camera position as (azimuth, elevation, distance)"""
        return (self._azimuth, self._elevation, self._distance)
    
    @camera_position.setter
    def camera_position(self, position):
        """Set the camera position and emit signal if changed"""
        azimuth, elevation, distance = position
        if (self._azimuth != azimuth or 
            self._elevation != elevation or 
            self._distance != distance):
            self._azimuth = azimuth
            self._elevation = elevation
            self._distance = distance
            self.camera_position_changed.emit(azimuth, elevation, distance)
    
    # Ball position
    @property
    def ball_position(self):
        """Get the current ball position as (x, y, z)"""
        return self._ball_position
    
    @ball_position.setter
    def ball_position(self, position):
        """Set the ball position and emit signal if changed"""
        if self._ball_position != position:
            self._ball_position = position
            self.ball_position_changed.emit(*position)
    
    # Playback state
    @property
    def playback_state(self):
        """Get the current playback state ('play', 'pause', 'stop')"""
        return self._playback_state
    
    @playback_state.setter
    def playback_state(self, state):
        """Set the playback state and emit signal if changed"""
        if self._playback_state != state:
            self._playback_state = state
            self.playback_state_changed.emit(state)
    
    # Current frame
    @property
    def current_frame(self):
        """Get the current frame number"""
        return self._current_frame
    
    @current_frame.setter
    def current_frame(self, frame):
        """Set the current frame and emit signal if changed"""
        logger = logging.getLogger(__name__)
        
        if self._current_frame != frame:
            logger.debug(f"AppState: current_frame changed: {self._current_frame} -> {frame}, total_frames={self._total_frames}")
            self._current_frame = frame
            self.current_frame_changed.emit(frame)
            
            # Also update current image if available
            if 0 <= frame < len(self._image_paths):
                self.current_image = self._image_paths[frame]
    
    # Total frames
    @property
    def total_frames(self):
        """Get the total number of frames"""
        return self._total_frames
    
    @total_frames.setter
    def total_frames(self, frames):
        """Set the total frames and emit signal if changed"""
        if self._total_frames != frames:
            self._total_frames = frames
            self.total_frames_changed.emit(frames)
    
    # LED state
    @property
    def led_state(self):
        """Get the LED state as (in_bounds, blink_rate)"""
        return self._led_state
    
    @led_state.setter
    def led_state(self, state):
        """Set the LED state and emit signal if changed"""
        in_bounds, blink_rate = state
        if self._led_state != state:
            self._led_state = state
            self.led_state_changed.emit(in_bounds, blink_rate)
            
    # Current file path
    @property
    def file_path(self):
        """Get the current file path"""
        return self._file_path
    
    @file_path.setter
    def file_path(self, path):
        """Set the current file path"""
        if self._file_path != path:
            self._file_path = path
    
    @property
    def image_paths(self):
        """Get the list of image paths for playback"""
        return self._image_paths
    
    @image_paths.setter
    def image_paths(self, paths):
        """Set the list of image paths and emit signal"""
        self._image_paths = paths
        self.images_loaded_changed.emit(paths)
    
    @property
    def current_image(self):
        """Get the current image path"""
        return self._current_image
    
    @current_image.setter
    def current_image(self, path):
        """Set the current image path and emit signal"""
        self._current_image = path
        self.current_image_changed.emit(path)
        
    # Active tab
    @property
    def active_tab(self):
        """Get the active tab name"""
        return self._active_tab
    
    @active_tab.setter 
    def active_tab(self, tab_name):
        """Set the active tab and emit signal"""
        if self._active_tab != tab_name:
            self._active_tab = tab_name
            self.active_tab_changed.emit(tab_name)
            
    def set_active_tab(self, tab_name):
        """Set the active tab and emit signal (convenience method)"""
        self.active_tab = tab_name 