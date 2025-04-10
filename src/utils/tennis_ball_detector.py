"""
Tennis Ball Detector Utility Module

This module provides utility functions for tennis ball detection, including:
- HSV color-based detection for tennis balls
- 2D to 3D coordinate conversion
- Stereo correspondence
"""

import cv2
import numpy as np
from src.constants.ui_constants import (
    TENNIS_BALL_HSV_LOWER, TENNIS_BALL_HSV_UPPER,
    TENNIS_BALL_MIN_CONTOUR_AREA, TENNIS_BALL_MAX_EXPECTED_AREA,
    DETECTION_GREEN, DETECTION_ORANGE, DETECTION_BLUE,
    TENNIS_BALL_KERNEL_SIZE, TENNIS_BALL_ERODE_ITERATIONS, TENNIS_BALL_DILATE_ITERATIONS,
    TENNIS_BALL_CENTER_RADIUS, TENNIS_BALL_CIRCLE_THICKNESS, TENNIS_BALL_DEFAULT_RADIUS,
    TENNIS_BALL_TEXT_OFFSET_X, TENNIS_BALL_TEXT_OFFSET_Y, TENNIS_BALL_FONT_SCALE, TENNIS_BALL_TEXT_THICKNESS,
    TENNIS_BALL_POSITION_TEXT_X, TENNIS_BALL_POSITION_TEXT_Y, TENNIS_BALL_POSITION_FONT_SCALE,
    CAMERA_BASELINE_DEFAULT, CAMERA_FOCAL_LENGTH_DEFAULT, CAMERA_PRINCIPAL_POINT_DEFAULT,
    OPENCV_GREEN
)


def detect_tennis_ball_by_color(frame, hsv_lower=None, hsv_upper=None):
    """
    Detect a tennis ball in a single frame using HSV color filtering.
    
    Args:
        frame: BGR input frame
        hsv_lower: Lower HSV range for tennis ball color (default: yellow-green)
        hsv_upper: Upper HSV range for tennis ball color
        
    Returns:
        Dictionary with detection results
    """
    # Default tennis ball color range (yellow-green)
    if hsv_lower is None:
        hsv_lower = np.array(TENNIS_BALL_HSV_LOWER)
    if hsv_upper is None:
        hsv_upper = np.array(TENNIS_BALL_HSV_UPPER)
    
    # Convert frame to HSV for color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create mask and filter by color
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    
    # Apply morphological operations to reduce noise
    kernel = np.ones((TENNIS_BALL_KERNEL_SIZE, TENNIS_BALL_KERNEL_SIZE), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=TENNIS_BALL_ERODE_ITERATIONS)
    mask = cv2.dilate(mask, kernel, iterations=TENNIS_BALL_DILATE_ITERATIONS)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Prepare result dictionary
    result = {
        'detection_type': 'none',
        'candidate_centers': [],
        'circle_detections': [],
        'selected_center': None,
        'frame_shape': frame.shape[:2]  # (height, width)
    }
    
    # Process contours to find candidate centers
    if contours:
        result['detection_type'] = 'color'
        for contour in contours:
            # Calculate area to filter out small noise
            area = cv2.contourArea(contour)
            if area < TENNIS_BALL_MIN_CONTOUR_AREA:  # Minimum contour area threshold
                continue
                
            # Calculate center using moments
            M = cv2.moments(contour)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Get bounding circle radius
                (_, _), radius = cv2.minEnclosingCircle(contour)
                
                result['candidate_centers'].append({
                    'x': cx,
                    'y': cy,
                    'area': area,
                    'radius': radius
                })
    
    # Select best candidate (if any)
    if result['candidate_centers']:
        # Sort by area (descending)
        candidates_sorted = sorted(result['candidate_centers'], key=lambda c: c['area'], reverse=True)
        result['selected_center'] = candidates_sorted[0]
    
    return result


def stereo_correspondence(left_point, right_point, camera_params):
    """
    Calculate 3D coordinates from stereo correspondence.
    
    Args:
        left_point: (x, y) coordinate in left image
        right_point: (x, y) coordinate in right image
        camera_params: Dictionary with camera parameters
            - baseline: Distance between cameras
            - focal_length: Focal length in pixels
            - principal_point: Principal point (cx, cy)
            - rotation_matrix: Camera rotation matrix
            - translation_vector: Camera translation vector
            
    Returns:
        (x, y, z) 3D coordinate in world space
    """
    if left_point is None or right_point is None:
        return None
    
    # Extract parameters
    baseline = camera_params.get('baseline', CAMERA_BASELINE_DEFAULT)  # 10cm default
    focal_length = camera_params.get('focal_length', CAMERA_FOCAL_LENGTH_DEFAULT)  # 1000px default
    cx = camera_params.get('principal_point', CAMERA_PRINCIPAL_POINT_DEFAULT)[0]
    cy = camera_params.get('principal_point', CAMERA_PRINCIPAL_POINT_DEFAULT)[1]
    
    # Calculate disparity (difference in x-coordinates)
    disparity = left_point[0] - right_point[0]
    
    # Avoid division by zero
    if disparity == 0:
        return None
    
    # Calculate depth (Z) using disparity
    z = (baseline * focal_length) / disparity
    
    # Calculate world X and Y coordinates
    x = (left_point[0] - cx) * z / focal_length
    y = (left_point[1] - cy) * z / focal_length
    
    # Optional: Apply rotation and translation if provided
    if 'rotation_matrix' in camera_params and 'translation_vector' in camera_params:
        point_3d = np.array([x, y, z])
        R = camera_params['rotation_matrix']
        T = camera_params['translation_vector']
        
        # Transform to world coordinates
        point_3d = np.matmul(R, point_3d) + T
        x, y, z = point_3d
    
    return (x, y, z)


def calculate_3d_position(left_detection, right_detection, camera_params=None):
    """
    Calculate 3D position of a tennis ball using stereo correspondence
    
    Args:
        left_detection: Detection results from left camera
        right_detection: Detection results from right camera
        camera_params: Camera parameters for stereo calculation
        
    Returns:
        Dictionary with 3D position information
    """
    # Default camera parameters if none provided
    if camera_params is None:
        camera_params = {}
    
    result = {'has_position': False, 'position': None, 'confidence': 0.0}
    
    # Check if we have valid detections from both cameras
    if (left_detection and right_detection and 
        left_detection.get('selected_center') and right_detection.get('selected_center')):
        
        # Get points from both cameras
        left_point = (left_detection['selected_center']['x'], left_detection['selected_center']['y'])
        right_point = (right_detection['selected_center']['x'], right_detection['selected_center']['y'])
        
        # Get 3D position using stereo correspondence
        position_3d = stereo_correspondence(left_point, right_point, camera_params)
        
        if position_3d:
            result['has_position'] = True
            result['position'] = position_3d
            
            # Calculate confidence based on detection areas
            left_area = left_detection['selected_center'].get('area', 0)
            right_area = right_detection['selected_center'].get('area', 0)
            
            # Simple confidence metric: normalized product of areas
            max_expected_area = TENNIS_BALL_MAX_EXPECTED_AREA  # Expected maximum area of a tennis ball
            area_product = left_area * right_area
            confidence = min(1.0, area_product / (max_expected_area ** 2))
            
            result['confidence'] = confidence
    
    return result


def draw_detection_overlay(frame, detection_result, color=None, thickness=TENNIS_BALL_CIRCLE_THICKNESS):
    """
    Draw detection overlay on a frame.
    
    Args:
        frame: Input frame to draw on
        detection_result: Detection result dictionary
        color: BGR color tuple for drawing
        thickness: Line thickness
        
    Returns:
        Frame with detection overlay
    """
    # Create a copy of the frame to draw on
    overlay = frame.copy()
    
    # Default color if none provided
    if color is None:
        color = (DETECTION_GREEN.blue(), DETECTION_GREEN.green(), DETECTION_GREEN.red())
    
    # Draw all candidate centers (if any)
    for candidate in detection_result.get('candidate_centers', []):
        center = (int(candidate['x']), int(candidate['y']))
        # Draw a small circle for each candidate
        orange_color = (DETECTION_ORANGE.blue(), DETECTION_ORANGE.green(), DETECTION_ORANGE.red())  # OpenCV uses BGR
        cv2.circle(overlay, center, TENNIS_BALL_CENTER_RADIUS, orange_color, -1)  # Orange filled circle
    
    # Draw circle detections from Hough (if any)
    for circle in detection_result.get('circle_detections', []):
        center = (int(circle['x']), int(circle['y']))
        radius = int(circle['radius'])
        # Draw circle outline
        blue_color = (DETECTION_BLUE.blue(), DETECTION_BLUE.green(), DETECTION_BLUE.red())  # OpenCV uses BGR
        cv2.circle(overlay, center, radius, blue_color, thickness)  # Blue circle
    
    # Draw the selected detection (if any)
    selected = detection_result.get('selected_center')
    if selected:
        center = (int(selected['x']), int(selected['y']))
        # If radius is available, use it; otherwise default to 10
        radius = int(selected.get('radius', TENNIS_BALL_DEFAULT_RADIUS))
        
        # Draw center point
        cv2.circle(overlay, center, TENNIS_BALL_CENTER_RADIUS, color, -1)  # Filled circle for center
        
        # Draw detection circle
        cv2.circle(overlay, center, radius, color, thickness)
        
        # Draw coordinates as text
        label = f"({center[0]}, {center[1]})"
        cv2.putText(overlay, label, 
                  (center[0] + TENNIS_BALL_TEXT_OFFSET_X, center[1] - TENNIS_BALL_TEXT_OFFSET_Y),
                  cv2.FONT_HERSHEY_SIMPLEX, TENNIS_BALL_FONT_SCALE, color, TENNIS_BALL_TEXT_THICKNESS)
    
    return overlay


def draw_3d_position(frame, position_3d, color=None, thickness=TENNIS_BALL_CIRCLE_THICKNESS):
    """
    Draw 3D position information on a frame.
    
    Args:
        frame: BGR input frame
        position_3d: (x, y, z) position
        color: BGR color tuple for drawing
        thickness: Line thickness
        
    Returns:
        Frame with 3D position overlay
    """
    if color is None:
        color = OPENCV_GREEN
        
    # Create a copy of the frame to draw on
    overlay = frame.copy()
    
    if position_3d:
        x, y, z = position_3d
        
        # Format position with 2 decimal places
        label = f"3D Position: X={x:.2f}, Y={y:.2f}, Z={z:.2f}"
        
        # Draw text on the frame
        cv2.putText(overlay, label, 
                   (TENNIS_BALL_POSITION_TEXT_X, TENNIS_BALL_POSITION_TEXT_Y), 
                   cv2.FONT_HERSHEY_SIMPLEX,
                   TENNIS_BALL_POSITION_FONT_SCALE, color, thickness)
    
    return overlay 