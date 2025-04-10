"""
Tennis Ball Detection Controller Module

This module provides the controller for detecting tennis balls in both camera views
and calculating 3D positions using stereo correspondence.
"""

import threading
import time
import json
import numpy as np
import cv2
from src.models.singleton import Singleton
from src.models.app_state import AppState
from src.controllers.image_manager import ImageManager
from src.controllers.ball_detection_controller import BallDetectionController
from src.utils.logger import Logger
from src.utils.settings_manager import SettingsManager
from src.utils.tennis_ball_detector import (
    detect_tennis_ball_by_color,
    calculate_3d_position,
    draw_detection_overlay
)


class TennisBallDetectionThread(threading.Thread):
    """
    Thread that performs tennis ball detection on both cameras using multiple methods,
    and calculates 3D position using stereo correspondence.
    """
    
    def __init__(self, callback=None):
        """
        Initialize the tennis ball detection thread
        
        Args:
            callback: Function to call with detection results
        """
        super().__init__()
        self.daemon = True
        self.interrupt_flag = threading.Event()
        self.paused = threading.Event()
        self.callback = callback
        
        # Get singleton instances
        self.app_state = AppState.instance()
        self.image_manager = ImageManager.instance()
        self.logger = Logger.instance()
        self.settings_manager = SettingsManager.instance()
        
        # Initialize detection parameters
        self._load_detection_settings()
        
        # Camera parameters for stereo calculation
        self.camera_params = self._load_camera_parameters()
        
        self.logger.debug("Tennis ball detection thread initialized")
    
    def _load_detection_settings(self):
        """Load detection settings from settings manager"""
        # Frame difference detection settings
        self.frame_diff_threshold = self.settings_manager.get("ball_detection_threshold", 30)
        self.min_contour_area = self.settings_manager.get("min_contour_area", 50)
        
        # Color detection settings
        self.use_color_detection = self.settings_manager.get("use_color_detection", True)
        hsv_low_h = self.settings_manager.get("hsv_low_h", 25)
        hsv_low_s = self.settings_manager.get("hsv_low_s", 50)
        hsv_low_v = self.settings_manager.get("hsv_low_v", 50)
        hsv_high_h = self.settings_manager.get("hsv_high_h", 65)
        hsv_high_s = self.settings_manager.get("hsv_high_s", 255)
        hsv_high_v = self.settings_manager.get("hsv_high_v", 255)
        
        self.hsv_lower = np.array([hsv_low_h, hsv_low_s, hsv_low_v])
        self.hsv_upper = np.array([hsv_high_h, hsv_high_s, hsv_high_v])
        
        # Hough circle detection settings
        self.use_hough = self.settings_manager.get("use_hough_detection", False)
        self.hough_params = {
            'dp': self.settings_manager.get("hough_dp", 1),
            'min_dist': self.settings_manager.get("hough_min_dist", 20),
            'param1': self.settings_manager.get("hough_param1", 50),
            'param2': self.settings_manager.get("hough_param2", 30),
            'min_radius': self.settings_manager.get("hough_min_radius", 5),
            'max_radius': self.settings_manager.get("hough_max_radius", 50)
        }
    
    def _load_camera_parameters(self):
        """
        Load camera parameters from config file
        
        Returns:
            dict: Camera parameters for stereo calculations
        """
        try:
            # Try to load from settings or config file
            config_path = 'src/config.json'
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            camera_params = config.get('camera_parameters', {})
            
            # Ensure we have all required parameters, add defaults if missing
            if 'baseline' not in camera_params:
                camera_params['baseline'] = 0.1  # 10cm between cameras
            
            if 'focal_length' not in camera_params:
                camera_params['focal_length'] = 1000  # Default focal length
            
            if 'principal_point' not in camera_params:
                camera_params['principal_point'] = (0, 0)
            
            self.logger.debug(f"Loaded camera parameters: {camera_params}")
            return camera_params
            
        except Exception as e:
            self.logger.error(f"Error loading camera parameters: {e}")
            # Use default parameters
            return {
                'baseline': 0.1,
                'focal_length': 1000,
                'principal_point': (0, 0)
            }
    
    def run(self):
        """Run the tennis ball detection thread"""
        self.logger.debug("Tennis ball detection thread started")
        
        prev_left_frame = None
        prev_right_frame = None
        prev_time = time.time()
        
        while not self.interrupt_flag.is_set():
            # Handle pause state
            if self.paused.is_set():
                time.sleep(0.1)
                continue
            
            # Measure FPS
            current_time = time.time()
            elapsed = current_time - prev_time
            fps = 1.0 / elapsed if elapsed > 0 else 0
            prev_time = current_time
            
            # Get current frame index
            frame_idx = self.app_state.current_frame
            if frame_idx < 0:
                time.sleep(0.1)
                continue
            
            # Get frames from both cameras
            left_frame = self.image_manager.get_frame('left', frame_idx)
            right_frame = self.image_manager.get_frame('right', frame_idx)
            
            if left_frame is None or right_frame is None:
                time.sleep(0.1)
                continue
            
            # Initialize previous frames if needed
            if prev_left_frame is None:
                prev_left_frame = left_frame
            if prev_right_frame is None:
                prev_right_frame = right_frame
            
            try:
                # Measure processing time
                start_process = time.time()
                
                # Detect tennis ball in both camera views
                left_detection = self._detect_tennis_ball(prev_left_frame, left_frame)
                right_detection = self._detect_tennis_ball(prev_right_frame, right_frame)
                
                # Calculate 3D position if we have detections from both cameras
                position_data = calculate_3d_position(
                    left_detection,
                    right_detection, 
                    self.camera_params
                )
                
                # Update previous frames
                prev_left_frame = left_frame
                prev_right_frame = right_frame
                
                # Prepare result dictionary
                result = {
                    'left': left_detection,
                    'right': right_detection,
                    'position': position_data,
                    'timestamp': time.time()
                }
                
                # Calculate processing time
                process_time = time.time() - start_process
                
                # Call callback if one was provided
                if self.callback:
                    self.callback(result, fps, process_time)
                
            except Exception as e:
                self.logger.error(f"Error in tennis ball detection: {e}")
            
            # Sleep briefly to avoid consuming too much CPU
            time.sleep(0.01)
    
    def _detect_tennis_ball(self, prev_frame, curr_frame):
        """
        Detect tennis ball using multiple methods
        
        Args:
            prev_frame: Previous frame
            curr_frame: Current frame
            
        Returns:
            dict: Detection results
        """
        # Start with color-based detection if enabled
        if self.use_color_detection:
            color_result = detect_tennis_ball_by_color(
                curr_frame,
                self.hsv_lower,
                self.hsv_upper
            )
            
            # If we get good detection with color, return it
            if color_result['detection_type'] != 'none':
                return color_result
        
        # Otherwise, fall back to frame differencing for motion detection
        # Convert frames to grayscale for processing
        if len(prev_frame.shape) == 3:
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        else:
            prev_gray = prev_frame
        
        if len(curr_frame.shape) == 3:
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        else:
            curr_gray = curr_frame
        
        # Frame differencing for motion detection
        diff = cv2.absdiff(curr_gray, prev_gray)
        _, thresh = cv2.threshold(diff, self.frame_diff_threshold, 255, cv2.THRESH_BINARY)
        
        # Find contours in the thresholded difference image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size to eliminate noise
        valid_contours = [c for c in contours if cv2.contourArea(c) > self.min_contour_area]
        
        # Prepare result dictionary
        result = {
            'detection_type': 'none',
            'candidate_centers': [],
            'circle_detections': [],
            'selected_center': None,
            'frame_shape': curr_frame.shape[:2]  # (height, width)
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
                    # Get bounding circle radius
                    (_, _), radius = cv2.minEnclosingCircle(contour)
                    
                    result['candidate_centers'].append({
                        'x': cx,
                        'y': cy,
                        'area': area,
                        'radius': radius
                    })
        
        # Optional: Use Hough Circle detection for verification if enabled
        if self.use_hough and len(curr_frame.shape) == 3:
            # Convert to grayscale for Hough Circle detection
            gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
            # Apply Gaussian blur to reduce noise
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detect circles using Hough Circle Transform
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
            
            if circles is not None:
                result['detection_type'] = 'hough'
                circles = np.uint16(np.around(circles[0]))
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
    
    def stop(self):
        """Stop the detection thread"""
        self.interrupt_flag.set()
        self.logger.debug("Tennis ball detection thread stopping")
    
    def pause(self):
        """Pause detection processing"""
        self.paused.set()
        self.logger.debug("Tennis ball detection thread paused")
    
    def resume(self):
        """Resume detection processing"""
        self.paused.clear()
        self.logger.debug("Tennis ball detection thread resumed")


class TennisBallDetectionController(metaclass=Singleton):
    """
    Controller for tennis ball detection.
    Manages detection settings, thread, and coordinates with UI.
    """
    
    def __init__(self):
        """Initialize the tennis ball detection controller"""
        # Get singleton instances
        self.logger = Logger.instance()
        self.app_state = AppState.instance()
        self.settings_manager = SettingsManager.instance()
        
        # Initialize thread
        self.detection_thread = None
        self.detection_active = False
        
        # Connect to state signals
        self._connect_signals()
        
        # Initialize the standard ball detection controller
        self.basic_detector = BallDetectionController()
        
        self.logger.debug("Tennis ball detection controller initialized")
    
    def _connect_signals(self):
        """Connect to app state signals"""
        self.app_state.playback_state_changed.connect(self._on_playback_state_changed)
        self.app_state.current_frame_changed.connect(self._on_current_frame_changed)
    
    def start_detection(self, callback=None):
        """
        Start tennis ball detection
        
        Args:
            callback: Function to call with detection results
        """
        if self.detection_thread and self.detection_thread.is_alive():
            self.logger.debug("Detection thread already running, stopping first")
            self.stop_detection()
        
        self.logger.debug("Starting tennis ball detection")
        self.detection_thread = TennisBallDetectionThread(callback)
        self.detection_thread.start()
        self.detection_active = True
    
    def stop_detection(self):
        """Stop tennis ball detection"""
        if self.detection_thread:
            self.logger.debug("Stopping tennis ball detection")
            self.detection_thread.stop()
            self.detection_thread = None
            self.detection_active = False
    
    def pause_detection(self):
        """Pause tennis ball detection"""
        if self.detection_thread:
            self.logger.debug("Pausing tennis ball detection")
            self.detection_thread.pause()
    
    def resume_detection(self):
        """Resume tennis ball detection"""
        if self.detection_thread:
            self.logger.debug("Resuming tennis ball detection")
            self.detection_thread.resume()
    
    def toggle_detection(self, callback=None):
        """
        Toggle tennis ball detection on/off
        
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
    
    def update_detection_settings(self, settings):
        """
        Update detection settings
        
        Args:
            settings: Dictionary with new detection settings
        """
        # Save settings
        for key, value in settings.items():
            self.settings_manager.set(key, value)
        
        # Restart detection thread to apply new settings
        if self.detection_active:
            callback = None
            if self.detection_thread and hasattr(self.detection_thread, 'callback'):
                callback = self.detection_thread.callback
            
            self.stop_detection()
            self.start_detection(callback)
    
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