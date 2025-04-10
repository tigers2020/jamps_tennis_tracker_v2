"""
Image Player Controller Module

This module provides a controller for playing image sequences.
It handles playback control, frame navigation, and timing.
"""

import time
from enum import Enum
from typing import Callable, Optional

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
import os

from src.controllers.image_manager import ImageManager
from src.models.app_state import AppState
from src.utils.logger import Logger

class ImagePlayerController(QObject):
    """
    Controller for managing image playback and display
    
    This class provides the following functionality:
    - Managing image playback timers
    - Transitioning between frames
    - Image display and scaling
    - FPS calculation and monitoring
    """
    
    # Constants
    BASE_FPS = 1000
    MAX_SKIP_PERCENT = 0.20
    MAX_SKIP_FRAMES = 100
    ENABLE_UNLIMITED_SKIP = True
    FPS_UPDATE_INTERVAL = 500  # ms
    TIMER_INTERVAL = 1  # ms
    
    # Camera types
    CAMERA_LEFT = "left"
    CAMERA_RIGHT = "right"
    
    # Signals
    fps_updated = Signal(float, int)  # current FPS, target FPS
    images_updated = Signal(int)      # current frame number
    
    def __init__(self):
        super(ImagePlayerController, self).__init__()
        
        # Get singleton instances
        self.app_state = AppState.instance()
        self.image_manager = ImageManager.instance()
        self.logger = Logger.instance()
        
        # Frame timing tracking variables
        self._frame_time_tracker = 0
        self._last_frame_time = 0
        self._fps_update_timer = 0
        self._current_fps = 0
        self._frames_processed = 0
        
        # Image playback timer
        self._image_timer = QTimer(self)
        self._image_timer.timeout.connect(self._advance_image)
        
        # Connect app state signals
        self.app_state.playback_state_changed.connect(self._handle_playback_state_changed)
        self.app_state.speed_changed.connect(self._handle_speed_changed)
        self.app_state.current_frame_changed.connect(self._handle_frame_changed)
    
    def _handle_frame_changed(self, frame):
        """
        Handle frame change
        
        Args:
            frame: New frame index
        """
        # Emit signal
        self.logger.debug(f"_handle_frame_changed called: current_frame={frame}, total_frames={self.app_state.total_frames}")
        self.images_updated.emit(frame + 1)  # Send frame number starting from 1
    
    def _handle_playback_state_changed(self, state):
        """
        Handle playback state change
        
        Args:
            state: New playback state ('play', 'pause', 'stop')
        """
        # Image mode
        if self.image_manager.get_total_images() > 0:
            if state == 'play':
                # Update total_frames before starting
                real_total_frames = self.image_manager.get_total_images()
                if self.app_state.total_frames != real_total_frames:
                    self.logger.debug(f"Updating total_frames: {self.app_state.total_frames} -> {real_total_frames}")
                    self.app_state.total_frames = real_total_frames
                
                self._setup_playback_timers()
                self._image_timer.start()
            elif state == 'pause':
                self._image_timer.stop()
            elif state == 'stop':
                self._image_timer.stop()
                self.app_state.current_frame = 0
                # Emit signal
                self.images_updated.emit(1)  # First frame (starting from 1)
    
    def _setup_playback_timers(self):
        """Set up timers for image playback"""
        # Calculate interval based on speed multiplier and base FPS
        target_fps = int(self.app_state.speed * self.BASE_FPS)
        
        # Use consistent timer interval
        timer_interval = self.TIMER_INTERVAL
        
        # Initialize frame timing variables
        self._frame_time_tracker = 0
        self._last_frame_time = time.time() * 1000
        self._fps_update_timer = 0
        self._current_fps = 0
        self._frames_processed = 0
        
        self._image_timer.setInterval(timer_interval)
        self.logger.debug(f"Playback started at {target_fps} fps")
    
    def _handle_speed_changed(self, speed):
        """
        Handle playback speed change
        
        Args:
            speed: New playback speed multiplier
        """
        # Only update if currently playing
        if self.app_state.playback_state == 'play' and self._image_timer.isActive():
            self._setup_playback_timers()
            self.logger.debug(f"Playback speed updated to {int(speed * self.BASE_FPS)} fps")
    
    def _advance_image(self):
        """
        Advance to the next image in the playback sequence
        
        This method is called by the timer at the specified interval
        and updates the display to the next image in the sequence.
        """
        total_images = self.image_manager.get_total_images()
        if total_images == 0:
            return
        
        # Record current time (high precision)
        current_time = time.time() * 1000  # convert to ms
        
        # Calculate target playback rate
        target_fps = int(self.app_state.speed * self.BASE_FPS)
        target_frame_time = 1000 / target_fps  # target time per frame (ms)
        
        # Initialize last frame time if not set
        if self._last_frame_time == 0:
            self._last_frame_time = current_time
            self._frame_time_tracker = 0
            return  # Skip first cycle to establish baseline
        
        # Time elapsed since last frame update
        elapsed_time = current_time - self._last_frame_time
        self._last_frame_time = current_time
        
        # Accumulate time for FPS calculation
        self._fps_update_timer += elapsed_time
        
        # Update frame time tracker - 더 정밀한 시간 추적을 위해 부동소수점 유지
        self._frame_time_tracker += elapsed_time
        
        # Calculate how many frames should have been shown by now
        frames_to_show = self._frame_time_tracker / target_frame_time
        
        # Only proceed if we need to show at least one frame
        if frames_to_show < 1:
            return
        
        # 개선된 프레임 스킵 로직
        # 더 정확한 프레임 수를 위해 반올림(round) 사용 - 원래는 내림(int) 사용
        frames_to_advance = round(frames_to_show)
        
        # Exclude time used for these frames - 더 정확한 시간 보정
        self._frame_time_tracker -= frames_to_advance * target_frame_time
        
        # 무제한 스킵 모드가 활성화된 경우 제한 없이 건너뛰기
        if self.ENABLE_UNLIMITED_SKIP:
            # 너무 많이 건너뛰지 않도록 전체 프레임의 30%로만 제한
            # 이 제한은 매우 느린 시스템에서 너무 큰 점프를 방지하기 위한 안전장치
            max_skip = int(total_images * 0.3)
            frames_to_advance = min(frames_to_advance, max_skip)
        else:
            # 기존 로직보다 더 강화된 건너뛰기 허용
            max_skip = max(1, min(self.MAX_SKIP_FRAMES, 
                                int(total_images * self.MAX_SKIP_PERCENT)))
            frames_to_advance = min(frames_to_advance, max_skip)
        
        # 최소 1프레임은 보장
        frames_to_advance = max(1, frames_to_advance)
        
        # Update current frame
        current_frame = self.app_state.current_frame
        next_frame = current_frame + frames_to_advance
        
        self.logger.debug(f"_advance_image: current={current_frame}, next={next_frame}, total={total_images}, frames_to_advance={frames_to_advance}")
        
        # Handle reaching the end
        if next_frame >= total_images:
            # Loop back to the beginning for repeat playback
            self.logger.debug("Reached the last frame. Restarting playback from the beginning.")
            next_frame = 0  # Set to first frame
        
        # Update current frame - only if within valid range
        if 0 <= next_frame < total_images:
            self.app_state.current_frame = next_frame
        
        # Count frames processed for FPS calculation
        self._frames_processed += frames_to_advance
        
        # Update actual FPS display every 500ms for more stable readings
        if self._fps_update_timer >= self.FPS_UPDATE_INTERVAL:
            self._update_fps_display(target_fps)
    
    def _update_fps_display(self, target_fps):
        """
        FPS display update
        
        Args:
            target_fps: Target FPS
        """
        # Calculate actual FPS
        elapsed_seconds = self._fps_update_timer / 1000
        self._current_fps = self._frames_processed / elapsed_seconds
        
        # Update FPS display
        self.fps_updated.emit(self._current_fps, target_fps)
        
        # Reset FPS calculation variables
        self._frames_processed = 0
        self._fps_update_timer = 0
    
    def get_current_frame_number(self):
        """
        Get frame number corresponding to current image index
        
        Returns:
            int: Current frame number (starting from 1)
        """
        return self.app_state.current_frame + 1
    
    def scale_image(self, pixmap, view_widget):
        """
        Scale image to fit view
        
        Args:
            pixmap: Original image pixmap
            view_widget: View widget to display image
            
        Returns:
            Scaled pixmap
        """
        if pixmap is None or pixmap.isNull():
            return None
            
        # Scale image to fit view
        return pixmap.scaled(
            view_widget.width(),
            view_widget.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
    
    def display_camera_image(self, view_widget, frame_number, camera_type, black_bg_style=""):
        """
        Display camera image on specified view widget
        
        Args:
            view_widget: View widget to display image
            frame_number: Frame number to display
            camera_type: Camera type (left or right)
            black_bg_style: Style to use for black background if image is missing
            
        Returns:
            bool: True if successful, False if failed
        """
        # Get images for the specified frame (this uses the optimized GPU loading)
        if camera_type == self.CAMERA_LEFT:
            pixmap, _ = self.image_manager.get_images(frame_number)
        else:  # right camera
            _, pixmap = self.image_manager.get_images(frame_number)
        
        if pixmap and not pixmap.isNull():
            # Use common scaling method
            scaled_pixmap = self.scale_image(pixmap, view_widget)
            
            if scaled_pixmap:
                # Set pixmap to view
                view_widget.setPixmap(scaled_pixmap)
                
                # Remove all styles that can hide image
                view_widget.setStyleSheet("")
                
                # Update tooltip with image information
                image_path = self.image_manager.get_frame_path(frame_number, camera=camera_type)
                if image_path:
                    filename = os.path.basename(image_path)
                    view_widget.setToolTip(f"{camera_type.capitalize()} Camera: {filename} (Frame {frame_number})")
                
                return True
        else:
            # Show message if image cannot be used
            view_widget.clear()
            view_widget.setText(f"Analysis Area ({camera_type} Camera Image Missing)")
            
            if black_bg_style:
                view_widget.setStyleSheet(black_bg_style)
            
            if camera_type == self.CAMERA_LEFT:
                self.logger.warning(f"Failed to load {camera_type} image for frame {frame_number}")
        
        return False
            
    def start_playback(self):
        """Start playback"""
        self.app_state.playback_state = 'play'
    
    def pause_playback(self):
        """Pause playback"""
        self.app_state.playback_state = 'pause'
    
    def stop_playback(self):
        """Stop playback"""
        self.app_state.playback_state = 'stop'
        
    def is_playing(self):
        """
        Check if currently playing
        
        Returns:
            bool: True if playing, False if not
        """
        return self.app_state.playback_state == 'play' and self._image_timer.isActive() 