"""
Ball Detection Controller Module

This module provides the controller for detecting tennis balls in video frames.
It manages the detection thread and coordinates with the image manager.
"""

import threading
import time
import cv2
import numpy as np
from src.models.singleton import Singleton
from src.models.app_state import AppState
from src.controllers.image_manager import ImageManager
from src.utils.logger import Logger
from src.utils.settings_manager import SettingsManager


class BallDetectionThread(threading.Thread):
    """
    Thread class for ball detection processing.
    Handles frame differencing and optional Hough circle detection.
    """
    
    def __init__(self, callback=None):
        """
        Initialize the ball detection thread.
        
        Args:
            callback: Function to call with detection results
        """
        super().__init__()
        self.daemon = True  # Set as daemon thread to terminate when main program exits
        self.interrupt_flag = threading.Event()
        self.paused = threading.Event()
        self.callback = callback
        self.image_manager = ImageManager.instance()
        self.app_state = AppState.instance()
        self.logger = Logger.instance()
        self.settings_manager = SettingsManager.instance()
        
        # Load detection parameters from settings
        self.threshold = self.settings_manager.get('ball_detection_threshold', 30)
        self.min_contour_area = self.settings_manager.get('min_contour_area', 50)
        self.use_hough = self.settings_manager.get('use_hough_detection', False)
        self.hough_params = {
            'dp': self.settings_manager.get('hough_dp', 1),
            'min_dist': self.settings_manager.get('hough_min_dist', 20),
            'param1': self.settings_manager.get('hough_param1', 50),
            'param2': self.settings_manager.get('hough_param2', 30),
            'min_radius': self.settings_manager.get('hough_min_radius', 5),
            'max_radius': self.settings_manager.get('hough_max_radius', 50)
        }
        
        self.logger.debug("Ball detection thread initialized")

    def run(self):
        """Execute ball detection process in a loop until interrupted"""
        self.logger.debug("Ball detection thread started")
        
        prev_frame = None
        prev_time = time.time()
        
        while not self.interrupt_flag.is_set():
            # Handle pause state
            if self.paused.is_set():
                time.sleep(0.1)  # Short sleep to prevent CPU thrashing
                continue
            
            # Measure FPS
            current_time = time.time()
            elapsed = current_time - prev_time
            fps = 1.0 / elapsed if elapsed > 0 else 0
            prev_time = current_time
            
            # Get current frame
            current_frame_idx = self.app_state.current_frame
            if current_frame_idx < 0:
                time.sleep(0.1)
                continue
                
            # Get current frame image
            current_frame = self.image_manager.get_frame('left', current_frame_idx)
            if current_frame is None:
                time.sleep(0.1)
                continue
            
            # Skip processing if we don't have two frames yet
            if prev_frame is None:
                prev_frame = current_frame
                time.sleep(0.1)
                continue
            
            # Process frames to detect ball
            try:
                start_process = time.time()
                result = self.process_frames(prev_frame, current_frame)
                process_time = time.time() - start_process
                
                # Update previous frame for next iteration
                prev_frame = current_frame
                
                # Call callback with results if one was provided
                if self.callback and result:
                    self.callback(result, fps, process_time)
                    
            except Exception as e:
                self.logger.error(f"Error in ball detection processing: {e}")
            
            # Adaptive sleep to maintain desired processing rate
            time.sleep(0.01)  # 10ms sleep to prevent CPU thrashing
    
    def process_frames(self, prev_frame, current_frame):
        """
        Process two consecutive frames to detect tennis ball movement.
        
        Args:
            prev_frame: Previous video frame
            current_frame: Current video frame
            
        Returns:
            Dictionary containing detection results
        """
        # Convert to grayscale for processing
        if len(prev_frame.shape) == 3:
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        else:
            prev_gray = prev_frame
            
        if len(current_frame.shape) == 3:
            current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        else:
            current_gray = current_frame
        
        # Frame differencing to detect motion
        diff = cv2.absdiff(current_gray, prev_gray)
        _, thresh = cv2.threshold(diff, self.threshold, 255, cv2.THRESH_BINARY)
        
        # Find contours in the thresholded difference image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size to eliminate noise
        valid_contours = [c for c in contours if cv2.contourArea(c) > self.min_contour_area]
        
        result = {
            'detection_type': 'none',
            'candidate_centers': [],
            'circle_detections': [],
            'selected_center': None,
            'frame_shape': current_frame.shape[:2]  # (height, width)
        }
        
        # Process contours to find candidate centers
        if valid_contours:
            result['detection_type'] = 'diff'
            for contour in valid_contours:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    area = cv2.contourArea(contour)
                    result['candidate_centers'].append({
                        'x': cx,
                        'y': cy,
                        'area': area
                    })
        
        # Optional: Hough Circle detection for verification
        if self.use_hough and len(current_frame.shape) == 3:
            circles = self.hough_circle_detection(current_frame)
            if circles is not None:
                result['detection_type'] = 'hough'
                for (x, y, r) in circles:
                    result['circle_detections'].append({
                        'x': int(x),
                        'y': int(y),
                        'radius': int(r)
                    })
        
        # Select best candidate (either largest contour or most confident circle)
        if result['candidate_centers']:
            # Sort by area (descending)
            candidates_sorted = sorted(result['candidate_centers'], key=lambda c: c['area'], reverse=True)
            result['selected_center'] = candidates_sorted[0]
        elif result['circle_detections']:
            # Use first circle (could implement more sophisticated selection)
            result['selected_center'] = result['circle_detections'][0]
            
        return result
            
    def hough_circle_detection(self, frame, roi=None):
        """
        Detect circles in frame using Hough Circle Transform
        
        Args:
            frame: Input color frame
            roi: Optional region of interest (x, y, w, h)
            
        Returns:
            Array of detected circles (x, y, r) or None if none detected
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply ROI if provided
        if roi:
            x, y, w, h = roi
            gray = gray[y:y+h, x:x+w]
        
        # Blur to reduce noise
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect circles
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=self.hough_params['dp'],
            minDist=self.hough_params['min_dist'],
            param1=self.hough_params['param1'],
            param2=self.hough_params['param2'],
            minRadius=self.hough_params['min_radius'],
            maxRadius=self.hough_params['max_radius']
        )
        
        # Adjust coordinates if ROI was used
        if circles is not None and roi:
            circles[0, :, 0] += roi[0]  # Add x offset
            circles[0, :, 1] += roi[1]  # Add y offset
            
        return circles[0] if circles is not None else None
    
    def stop(self):
        """Stop the detection thread"""
        self.interrupt_flag.set()
        self.logger.debug("Ball detection thread stopping")
    
    def pause(self):
        """Pause detection processing"""
        self.paused.set()
        self.logger.debug("Ball detection thread paused")
    
    def resume(self):
        """Resume detection processing"""
        self.paused.clear()
        self.logger.debug("Ball detection thread resumed")


class BallDetectionController(metaclass=Singleton):
    """
    Controller for tennis ball detection.
    Manages the detection thread and coordinates with UI.
    """
    
    def __init__(self):
        """Initialize the ball detection controller"""
        self.detection_thread = None
        self.detection_active = False
        self.logger = Logger.instance()
        self.app_state = AppState.instance()
        self.settings_manager = SettingsManager.instance()
        
        # Register for app state changes
        self.app_state.playback_state_changed.connect(self._on_playback_state_changed)
        self.app_state.current_frame_changed.connect(self._on_current_frame_changed)
        
        self.logger.debug("Ball detection controller initialized")
    
    def start_detection(self, callback=None):
        """
        Start the ball detection thread
        
        Args:
            callback: Function to call with detection results
        """
        if self.detection_thread and self.detection_thread.is_alive():
            self.logger.debug("Detection thread already running, stopping first")
            self.stop_detection()
        
        self.logger.debug("Starting ball detection")
        self.detection_thread = BallDetectionThread(callback)
        self.detection_thread.start()
        self.detection_active = True
    
    def stop_detection(self):
        """Stop the ball detection thread"""
        if self.detection_thread:
            self.logger.debug("Stopping ball detection")
            self.detection_thread.stop()
            self.detection_thread = None
            self.detection_active = False
    
    def pause_detection(self):
        """Pause the ball detection thread"""
        if self.detection_thread:
            self.logger.debug("Pausing ball detection")
            self.detection_thread.pause()
    
    def resume_detection(self):
        """Resume the ball detection thread"""
        if self.detection_thread:
            self.logger.debug("Resuming ball detection")
            self.detection_thread.resume()
    
    def toggle_detection(self, callback=None):
        """
        Toggle ball detection on/off
        
        Args:
            callback: Function to call with detection results
        
        Returns:
            bool: New detection state (True if active)
        """
        if self.detection_active:
            self.stop_detection()
        else:
            self.start_detection(callback)
        return self.detection_active
    
    def _on_playback_state_changed(self, is_playing):
        """
        Handle playback state changes
        
        Args:
            is_playing: Whether playback is active
        """
        if self.detection_active:
            if is_playing:
                self.resume_detection()
            else:
                self.pause_detection()
    
    def _on_current_frame_changed(self, frame_number):
        """
        Handle frame changes (e.g., from slider)
        
        Args:
            frame_number: New current frame number
        """
        # No action needed here, thread will get latest frame on next iteration
        pass 