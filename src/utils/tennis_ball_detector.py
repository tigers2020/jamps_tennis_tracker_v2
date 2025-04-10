"""
Tennis Ball Detector Utility Module

This module provides utility functions for tennis ball detection, including:
- HSV color-based detection for tennis balls
- 2D to 3D coordinate conversion
- Stereo correspondence
"""

import cv2
import numpy as np


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
        hsv_lower = np.array([25, 50, 50])
    if hsv_upper is None:
        hsv_upper = np.array([65, 255, 255])
    
    # Convert frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create a mask using the specified HSV range
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    
    # Apply morphological operations to remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    result = {
        'detection_type': 'none',
        'candidate_centers': [],
        'selected_center': None,
        'frame_shape': frame.shape[:2]  # (height, width)
    }
    
    # Process contours to find candidate centers
    if contours:
        result['detection_type'] = 'color'
        for contour in contours:
            # Calculate area to filter out small noise
            area = cv2.contourArea(contour)
            if area < 50:  # Minimum contour area threshold
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
    
    # Select best candidate (largest contour)
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
    baseline = camera_params.get('baseline', 0.1)  # 10cm default
    focal_length = camera_params.get('focal_length', 1000)  # 1000px default
    cx = camera_params.get('principal_point', (0, 0))[0]
    cy = camera_params.get('principal_point', (0, 0))[1]
    
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


def calculate_3d_position(left_detection, right_detection, camera_params):
    """
    Calculate 3D position from left and right camera detections.
    
    Args:
        left_detection: Detection result from left camera
        right_detection: Detection result from right camera
        camera_params: Camera parameters for stereo calculation
        
    Returns:
        Dictionary with 3D position information
    """
    result = {
        'has_position': False,
        'position': None,
        'confidence': 0.0
    }
    
    # Check if we have valid detections from both cameras
    if (left_detection and left_detection.get('selected_center') and 
        right_detection and right_detection.get('selected_center')):
        
        # Get point coordinates
        left_point = (
            left_detection['selected_center']['x'],
            left_detection['selected_center']['y']
        )
        right_point = (
            right_detection['selected_center']['x'],
            right_detection['selected_center']['y']
        )
        
        # Calculate 3D position
        position_3d = stereo_correspondence(left_point, right_point, camera_params)
        
        if position_3d:
            result['has_position'] = True
            result['position'] = position_3d
            
            # Calculate confidence based on detection areas
            left_area = left_detection['selected_center'].get('area', 0)
            right_area = right_detection['selected_center'].get('area', 0)
            
            # Simple confidence metric: normalized product of areas
            max_expected_area = 2000  # Expected maximum area of a tennis ball
            area_product = left_area * right_area
            confidence = min(1.0, area_product / (max_expected_area ** 2))
            
            result['confidence'] = confidence
    
    return result


def draw_detection_overlay(frame, detection_result, color=(0, 255, 0), thickness=2):
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
    
    # Draw all candidate centers (if any)
    for candidate in detection_result.get('candidate_centers', []):
        center = (int(candidate['x']), int(candidate['y']))
        # Draw a small circle for each candidate
        cv2.circle(overlay, center, 5, (0, 165, 255), -1)  # Orange filled circle
    
    # Draw circle detections from Hough (if any)
    for circle in detection_result.get('circle_detections', []):
        center = (int(circle['x']), int(circle['y']))
        radius = int(circle['radius'])
        # Draw circle outline
        cv2.circle(overlay, center, radius, (255, 0, 0), 2)  # Blue circle
    
    # Draw the selected detection (if any)
    selected = detection_result.get('selected_center')
    if selected:
        center = (int(selected['x']), int(selected['y']))
        
        # If radius is available, use it; otherwise default to 10
        radius = int(selected.get('radius', 10))
        
        # Draw center point
        cv2.circle(overlay, center, 5, color, -1)  # Filled circle for center
        
        # Draw circle around the ball
        cv2.circle(overlay, center, radius, color, thickness)
        
        # Add label with coordinates
        label = f"({center[0]}, {center[1]})"
        cv2.putText(overlay, label, (center[0] + 10, center[1] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return overlay


def draw_3d_position(frame, position_3d, color=(0, 255, 0), thickness=2):
    """
    Draw 3D position information on a frame.
    
    Args:
        frame: Input frame to draw on
        position_3d: (x, y, z) 3D position tuple
        color: BGR color tuple for drawing
        thickness: Line thickness
        
    Returns:
        Frame with 3D position overlay
    """
    if position_3d is None:
        return frame
    
    # Create a copy of the frame to draw on
    overlay = frame.copy()
    
    # Extract 3D coordinates
    x, y, z = position_3d
    
    # Draw 3D position label
    label = f"3D: ({x:.2f}, {y:.2f}, {z:.2f})"
    cv2.putText(overlay, label, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, color, thickness)
    
    return overlay 