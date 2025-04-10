"""
Calibration Point Manager
========================

Manages the selection, organization, and processing of calibration key points.
"""

import logging
import numpy as np
from typing import List, Tuple, Optional, Dict, Any, Union
from PySide6.QtCore import QObject, Signal, QPoint

from src.utils.math.vector import Vector2D


class CalibrationPointManager(QObject):
    """
    Manages the calibration key points for tennis court calibration.
    
    This class provides methods for adding, updating, organizing, and 
    processing points for both left and right cameras.
    """
    
    # Signal emitted when points are changed
    points_changed = Signal(str)  # camera parameter
    
    def __init__(self, total_points: int = 12):
        """Initialize the point manager with default state"""
        super().__init__()
        
        # Camera key points
        self.left_key_points: List[Vector2D] = []
        self.right_key_points: List[Vector2D] = []
        
        # Selected point indices
        self.left_selected_point_idx: int = -1
        self.right_selected_point_idx: int = -1
        
        # Current active camera
        self.active_camera: str = "left"
        
        # Total points to select per camera
        self.total_points: int = total_points
        
        # Logger setup
        self.logger = logging.getLogger(__name__)
    
    @property
    def key_points(self) -> List[Vector2D]:
        """Get key points for the current active camera"""
        return self.left_key_points if self.active_camera == "left" else self.right_key_points
    
    @key_points.setter
    def key_points(self, points: Union[List[Vector2D], List[Tuple[int, int]]]):
        """
        Set key points for the current active camera.
        Accepts either Vector2D objects or (x, y) tuples.
        """
        # Convert tuples to Vector2D if necessary
        vector_points = []
        for p in points:
            if isinstance(p, tuple) and len(p) == 2:
                vector_points.append(Vector2D(p[0], p[1]))
            elif isinstance(p, Vector2D):
                vector_points.append(p)
            else:
                raise ValueError(f"Invalid point format: {p}")
                
        if self.active_camera == "left":
            self.left_key_points = vector_points
        else:
            self.right_key_points = vector_points
    
    @property
    def selected_point_idx(self) -> int:
        """Get selected point index for the current active camera"""
        return self.left_selected_point_idx if self.active_camera == "left" else self.right_selected_point_idx
    
    @selected_point_idx.setter
    def selected_point_idx(self, idx: int):
        """Set selected point index for the current active camera"""
        if self.active_camera == "left":
            self.left_selected_point_idx = idx
        else:
            self.right_selected_point_idx = idx
    
    def set_active_camera(self, camera_type: str):
        """Set the active camera type ('left' or 'right')"""
        self.active_camera = camera_type
        self.points_changed.emit(camera_type)
    
    def add_point(self, x: int, y: int) -> bool:
        """Add a new point at the specified coordinates"""
        # Early return if already at max points
        if len(self.key_points) >= self.total_points:
            return False
            
        # Add the point to the current camera's list
        self._get_points_for_current_camera().append(Vector2D(x, y))
        self.selected_point_idx = len(self.key_points) - 1
        
        # Signal that points have changed
        self.points_changed.emit(self.active_camera)
        return True
    
    def update_point(self, idx: int, x: int, y: int) -> bool:
        """Update the point at the specified index"""
        points = self._get_points_for_current_camera()
        
        # Early return if index is invalid
        if idx < 0 or idx >= len(points):
            return False
            
        # Update the point coordinates
        points[idx] = Vector2D(x, y)
        self.selected_point_idx = idx
        
        # Signal that points have changed
        self.points_changed.emit(self.active_camera)
        return True
    
    def delete_point(self, idx: int) -> bool:
        """Delete the point at the specified index"""
        points = self._get_points_for_current_camera()
        
        # Early return if index is invalid
        if idx < 0 or idx >= len(points):
            return False
            
        # Remove the point
        points.pop(idx)
        
        # Update selected index if needed
        if self.selected_point_idx >= len(points):
            self.selected_point_idx = len(points) - 1
        
        # Signal that points have changed
        self.points_changed.emit(self.active_camera)
        return True
    
    def reset_points(self):
        """Reset all points for the current active camera"""
        if self.active_camera == "left":
            self.left_key_points = []
            self.left_selected_point_idx = -1
        else:
            self.right_key_points = []
            self.right_selected_point_idx = -1
        
        # Signal that points have changed
        self.points_changed.emit(self.active_camera)
    
    def find_nearest_point(self, pos: Union[QPoint, Vector2D], threshold: int = 15) -> int:
        """
        Find the index of the point nearest to the specified position.
        
        Args:
            pos: Position to find nearest point to (QPoint or Vector2D)
            threshold: Maximum distance to consider a point as "nearby"
            
        Returns:
            Index of the nearest point, or -1 if no point is within threshold
        """
        points = self._get_points_for_current_camera()
        
        # Early return if no points
        if not points:
            return -1
        
        # Convert QPoint to Vector2D if necessary
        if isinstance(pos, QPoint):
            pos_vector = Vector2D(pos.x(), pos.y())
        else:
            pos_vector = pos
            
        nearest_idx = -1
        min_distance = float('inf')
        
        # Find nearest point
        for i, point in enumerate(points):
            distance = point.distance_to(pos_vector)
            
            if distance < min_distance:
                min_distance = distance
                nearest_idx = i
        
        # Only return the index if the point is within the threshold
        return nearest_idx if min_distance < threshold else -1
    
    def is_complete(self, camera: Optional[str] = None) -> bool:
        """Check if all points have been selected for the specified camera"""
        if camera == "left" or (camera is None and self.active_camera == "left"):
            return len(self.left_key_points) == self.total_points
        elif camera == "right" or (camera is None and self.active_camera == "right"):
            return len(self.right_key_points) == self.total_points
        else:
            return False
    
    def process_points(self) -> bool:
        """Process the key points to improve alignments"""
        # Early return if not enough points
        if len(self.key_points) != self.total_points:
            return False
            
        try:
            # Backup original points
            original_points = self.key_points.copy()
            
            self.logger.info(f"Processing {self.active_camera} camera points...")
            
            # Convert Vector2D points to numpy array
            points_array = np.array([(p.x, p.y) for p in self.key_points])
            
            # Group points into 3 lines using K-means clustering
            k = 3  # Number of clusters (lines)
            
            # Initialize centroids (based on y-coordinate)
            y_coords = points_array[:, 1]
            y_min, y_max = np.min(y_coords), np.max(y_coords)
            
            # Calculate 3 evenly spaced centroids
            centroids = np.array([
                [np.mean(points_array[:, 0]), y_min + (y_max - y_min) * 0.25],  # Top line
                [np.mean(points_array[:, 0]), y_min + (y_max - y_min) * 0.5],   # Middle line
                [np.mean(points_array[:, 0]), y_min + (y_max - y_min) * 0.75]   # Bottom line
            ])
            
            # Sort points into clusters
            clusters, cluster_indices = self._cluster_points(points_array, centroids)
            
            # Expected number of points per line
            expected_counts = [5, 3, 4]  # First line: 5, Second line: 3, Third line: 4
            
            # Organize clusters by y-coordinate (top to bottom)
            sorted_clusters, sorted_indices = self._sort_clusters(clusters, cluster_indices)
            
            # Adjust clusters to match expected point counts
            self._adjust_cluster_sizes(sorted_clusters, sorted_indices, expected_counts)
            
            # Sort points within each cluster by x-coordinate (left to right)
            new_points_array = self._sort_points_within_clusters(sorted_clusters)
            
            # Convert numpy array back to Vector2D objects
            new_points = [Vector2D(int(p[0]), int(p[1])) for p in new_points_array]
            
            # Update with sorted points
            self.key_points = new_points
            
            # Apply additional alignments for better visual results
            self._apply_alignments(original_points)
            
            # Signal that points have changed
            self.points_changed.emit(self.active_camera)
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing points: {str(e)}")
            return False
    
    def _get_points_for_current_camera(self) -> List[Vector2D]:
        """Get the points list for the current active camera"""
        return self.left_key_points if self.active_camera == "left" else self.right_key_points
    
    def _cluster_points(self, points_array, initial_centroids):
        """Cluster points using K-means"""
        k = len(initial_centroids)
        max_iterations = 100
        centroids = initial_centroids.copy()
        
        # Iterate until convergence
        for _ in range(max_iterations):
            # Assign each point to closest centroid
            clusters = [[] for _ in range(k)]
            cluster_indices = [[] for _ in range(k)]
            
            for i, point in enumerate(points_array):
                distances = [np.linalg.norm(point - centroid) for centroid in centroids]
                closest_cluster = np.argmin(distances)
                clusters[closest_cluster].append(point)
                cluster_indices[closest_cluster].append(i)
            
            # Calculate new centroids
            new_centroids = []
            for cluster in clusters:
                if cluster:
                    new_centroids.append(np.mean(cluster, axis=0))
                else:
                    # If cluster is empty, use previous centroid
                    idx = len(new_centroids)
                    if idx < len(centroids):
                        new_centroids.append(centroids[idx])
            
            # Check convergence
            if np.allclose(centroids, new_centroids):
                break
                
            centroids = np.array(new_centroids)
        
        return clusters, cluster_indices
    
    def _sort_clusters(self, clusters, cluster_indices):
        """Sort clusters by y-coordinate (top to bottom)"""
        k = len(clusters)
        # Calculate average y-coordinate for each cluster
        avg_y = [np.mean(clusters[i], axis=0)[1] if clusters[i] else float('inf') for i in range(k)]
        # Get sorted indices
        sorted_idx = np.argsort(avg_y)
        # Return sorted clusters and indices
        return [clusters[i] for i in sorted_idx], [cluster_indices[i] for i in sorted_idx]
    
    def _adjust_cluster_sizes(self, clusters, cluster_indices, expected_counts):
        """Adjust cluster sizes to match expected counts"""
        k = len(clusters)
        
        # Adjust cluster sizes
        for i in range(k):
            while len(clusters[i]) > expected_counts[i]:
                # Find furthest point from centroid
                centroid = np.mean(clusters[i], axis=0)
                distances = [np.linalg.norm(p - centroid) for p in clusters[i]]
                furthest_idx = np.argmax(distances)
                
                # Find destination cluster (nearest other centroid that needs points)
                point = clusters[i][furthest_idx]
                other_centroids = [np.mean(clusters[j], axis=0) for j in range(k) 
                                  if j != i and len(clusters[j]) < expected_counts[j]]
                
                if other_centroids:
                    other_distances = [np.linalg.norm(point - centroid) for centroid in other_centroids]
                    closest_other = np.argmin(other_distances)
                    target_clusters = [j for j in range(k) if j != i and len(clusters[j]) < expected_counts[j]]
                    target_idx = target_clusters[closest_other]
                    
                    # Move point
                    point_idx = cluster_indices[i][furthest_idx]
                    clusters[target_idx].append(clusters[i][furthest_idx])
                    cluster_indices[target_idx].append(point_idx)
                    
                    # Remove from original cluster
                    clusters[i].pop(furthest_idx)
                    cluster_indices[i].pop(furthest_idx)
                else:
                    break
    
    def _sort_points_within_clusters(self, clusters):
        """Sort points within each cluster by x-coordinate"""
        new_points = []
        
        # Sort each cluster
        for cluster in clusters:
            if not cluster:
                continue
                
            # Sort by x-coordinate
            sorted_cluster = sorted(cluster, key=lambda p: p[0])
            new_points.extend(sorted_cluster)
        
        return new_points
    
    def _apply_alignments(self, original_points):
        """Apply additional alignments to improve visual quality"""
        # Point indices for each line
        p1_idx, p2_idx, p3_idx, p4_idx, p5_idx = 0, 1, 2, 3, 4  # First line
        p6_idx, p7_idx, p8_idx = 5, 6, 7                      # Second line
        p9_idx, p10_idx, p11_idx, p12_idx = 8, 9, 10, 11      # Third line
        
        # Align first line (points 1-5) horizontally with partial adjustment
        self._align_line_horizontally(
            [p1_idx, p2_idx, p3_idx, p4_idx, p5_idx], 
            original_points, 
            adjustment_factor=0.3
        )
        
        # Align middle line (points 6-8) horizontally with partial adjustment
        self._align_line_horizontally(
            [p6_idx, p7_idx, p8_idx], 
            original_points, 
            adjustment_factor=0.3
        )
        
        # Align third line (points 9-12) horizontally with partial adjustment
        self._align_line_horizontally(
            [p9_idx, p10_idx, p11_idx, p12_idx], 
            original_points, 
            adjustment_factor=0.3
        )
        
        # Apply vertical alignments
        self._align_points_vertically(
            p2_idx, p6_idx, p10_idx, 
            original_points, 
            adjustment_factor=0.2
        )
        
        self._align_points_vertically(
            p4_idx, p8_idx, p11_idx, 
            original_points, 
            adjustment_factor=0.2
        )
    
    def _align_line_horizontally(self, indices, original_points, adjustment_factor=0.3):
        """Align points horizontally with partial adjustment"""
        # Get original y values
        y_values = [original_points[i].y for i in indices]
        # Calculate median y value
        median_y = np.median(y_values)
        
        # Adjust each point
        for idx in indices:
            original_point = original_points[idx]
            # Adjust y-coordinate (partial adjustment to preserve original position)
            new_y = original_point.y * (1 - adjustment_factor) + median_y * adjustment_factor
            # Update point
            current_point = self.key_points[idx]
            self.key_points[idx] = Vector2D(current_point.x, int(new_y))
    
    def _align_points_vertically(self, top_idx, mid_idx, bottom_idx, original_points, adjustment_factor=0.2):
        """Align points vertically with partial adjustment"""
        # Get current points
        top_point = self.key_points[top_idx]
        mid_point = self.key_points[mid_idx]
        bottom_point = self.key_points[bottom_idx]
        
        # Get original top point for partial adjustment
        original_top = original_points[top_idx]
        
        # Calculate vertical alignment
        if abs(bottom_point.y - mid_point.y) > 0.001:  # Avoid division by zero
            # Calculate slope of line between mid and bottom points
            slope = (bottom_point.x - mid_point.x) / (bottom_point.y - mid_point.y)
            # Calculate ideal x-coordinate at top point's y-coordinate
            ideal_x = mid_point.x + slope * (top_point.y - mid_point.y)
            
            # Apply partial adjustment
            new_x = original_top.x * (1 - adjustment_factor) + ideal_x * adjustment_factor
            
            # Update top point
            self.key_points[top_idx] = Vector2D(int(new_x), top_point.y)
    
    def find_white_center(self, point_idx, image):
        """
        Find the center of white pixels around a selected point.
        
        This method analyzes the surrounding area of a point to find the center
        of white (bright) pixels, which usually represent court lines, and adjusts
        the point position accordingly.
        
        Args:
            point_idx: Index of the point to refine
            image: QImage containing the court image
            
        Returns:
            Vector2D: Coordinates of the refined point position, or None if not possible
        """
        if point_idx < 0 or point_idx >= len(self.key_points):
            return None
            
        # Get current point position
        current_point = self.key_points[point_idx]
        
        # Calculate window size based on image resolution
        # For higher resolution images, we need a larger window
        image_size = max(image.width(), image.height())
        # Base window size for 640x480 resolution
        base_size = 11
        # Scale factor based on resolution
        scale_factor = max(1.0, image_size / 640.0)
        # Calculate adjusted window size (always odd)
        window_size = int(base_size * scale_factor)
        if window_size % 2 == 0:
            window_size += 1  # Ensure odd size
        
        half_window = window_size // 2
        
        self.logger.debug(f"Using window size {window_size}x{window_size} for point {point_idx+1}")
        
        # Check if the point is too close to the image edge
        if (current_point.x < half_window or current_point.y < half_window or 
            current_point.x + half_window >= image.width() or 
            current_point.y + half_window >= image.height()):
            self.logger.warning(f"Point {point_idx+1} is too close to the image edge for refinement")
            return None
        
        # Try advanced line detection first
        intersection_point = self._find_line_intersection(current_point, image, window_size)
        if intersection_point is not None:
            # Found intersection point
            return intersection_point
        
        # Fallback to simpler weighted center method if intersection detection fails
        self.logger.debug(f"Falling back to simple weighted center for point {point_idx+1}")
            
        # Extract the window around the point
        weighted_x_sum = 0
        weighted_y_sum = 0
        weight_sum = 0
        
        # Brightness threshold (0-255, higher means stricter white detection)
        brightness_threshold = 180
        
        # Analyze the surrounding pixels
        for y in range(int(current_point.y) - half_window, int(current_point.y) + half_window + 1):
            for x in range(int(current_point.x) - half_window, int(current_point.x) + half_window + 1):
                # Get pixel color
                pixel = image.pixel(x, y)
                # Convert to RGB
                r = (pixel >> 16) & 0xff
                g = (pixel >> 8) & 0xff
                b = pixel & 0xff
                
                # Calculate brightness (simple average)
                brightness = (r + g + b) / 3
                
                # Only consider pixels above threshold
                if brightness > brightness_threshold:
                    # Weight is the brightness value
                    weight = brightness
                    weighted_x_sum += x * weight
                    weighted_y_sum += y * weight
                    weight_sum += weight
        
        # If no bright pixels found, return the original position
        if weight_sum == 0:
            self.logger.warning(f"No bright pixels found around point {point_idx+1}")
            return None
            
        # Calculate the weighted center
        refined_x = int(weighted_x_sum / weight_sum)
        refined_y = int(weighted_y_sum / weight_sum)
        refined_pos = Vector2D(refined_x, refined_y)
        
        # Limit maximum adjustment distance to prevent jumping to wrong lines
        max_adjustment = 10
        distance = current_point.distance_to(refined_pos)
        
        if distance > max_adjustment:
            self.logger.warning(f"Point {point_idx+1} refinement distance too large ({distance:.1f}px), limiting")
            # Calculate direction vector
            direction = (refined_pos - current_point).normalized()
            # Limit distance
            limited_pos = current_point + (direction * max_adjustment)
            return Vector2D(int(limited_pos.x), int(limited_pos.y))
        
        return refined_pos
    
    def _find_line_intersection(self, point, image, window_size):
        """
        Find the intersection of lines around a point using computer vision techniques.
        
        This method extracts white lines from a window around the point, detects their
        directions, and calculates the intersection point. It's more accurate than the
        simple weighted center method for points that are at line intersections.
        
        Args:
            point: Current point position (Vector2D)
            image: QImage containing the court image
            window_size: Size of the window to analyze
            
        Returns:
            Vector2D: Coordinates of the intersection point, or None if not detected
        """
        import numpy as np
        half_window = window_size // 2
        
        # Extract window as numpy array
        window = np.zeros((window_size, window_size), dtype=np.uint8)
        
        # Fill the window with brightness values
        for y in range(window_size):
            for x in range(window_size):
                image_x = int(point.x) - half_window + x
                image_y = int(point.y) - half_window + y
                
                if (0 <= image_x < image.width() and 0 <= image_y < image.height()):
                    pixel = image.pixel(image_x, image_y)
                    r = (pixel >> 16) & 0xff
                    g = (pixel >> 8) & 0xff
                    b = pixel & 0xff
                    brightness = (r + g + b) / 3
                    window[y, x] = min(int(brightness), 255)
        
        # Threshold the window to get white pixels
        brightness_threshold = 180
        binary = (window > brightness_threshold).astype(np.uint8) * 255
        
        # Check if we have enough white pixels
        if np.sum(binary) / 255 < window_size:
            self.logger.debug(f"Not enough white pixels for line detection")
            return None
        
        # Detect line directions using gradient analysis
        # Compute x and y gradients
        grad_x = np.zeros_like(binary, dtype=np.float32)
        grad_y = np.zeros_like(binary, dtype=np.float32)
        
        # Simple gradient calculation
        for y in range(1, window_size-1):
            for x in range(1, window_size-1):
                if binary[y, x] > 0:
                    grad_x[y, x] = int(binary[y, x+1]) - int(binary[y, x-1])
                    grad_y[y, x] = int(binary[y+1, x]) - int(binary[y-1, x])
        
        # Find gradient magnitudes
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        
        # Create binary masks for horizontal and vertical lines
        horizontal_mask = np.abs(grad_y) > np.abs(grad_x) * 2
        vertical_mask = np.abs(grad_x) > np.abs(grad_y) * 2
        
        # Check if we have both horizontal and vertical lines
        horizontal_count = np.sum(horizontal_mask & (grad_mag > 0))
        vertical_count = np.sum(vertical_mask & (grad_mag > 0))
        
        self.logger.debug(f"Horizontal pixels: {horizontal_count}, Vertical pixels: {vertical_count}")
        
        if horizontal_count < window_size / 2 or vertical_count < window_size / 2:
            self.logger.debug(f"Not enough horizontal/vertical line pixels")
            return None
        
        # Find center of horizontal and vertical lines
        h_points = np.where(horizontal_mask & (grad_mag > 0))
        v_points = np.where(vertical_mask & (grad_mag > 0))
        
        if len(h_points[0]) == 0 or len(v_points[0]) == 0:
            return None
        
        # Calculate average position of horizontal and vertical lines
        h_center_y = np.mean(h_points[0])
        h_center_x = np.mean(h_points[1])
        v_center_y = np.mean(v_points[0])
        v_center_x = np.mean(v_points[1])
        
        # Convert back to image coordinates
        intersection_x = int(point.x) - half_window + int(v_center_x)
        intersection_y = int(point.y) - half_window + int(h_center_y)
        
        # Create Vector2D for the intersection point
        intersection = Vector2D(intersection_x, intersection_y)
        
        # Limit maximum adjustment distance to prevent jumping to wrong lines
        max_adjustment = 15  # Allow slightly more movement for intersection detection
        distance = point.distance_to(intersection)
        
        if distance > max_adjustment:
            self.logger.warning(f"Line intersection distance too large ({distance:.1f}px), limiting")
            # Calculate direction vector
            direction = (intersection - point).normalized()
            # Limit distance
            limited_pos = point + (direction * max_adjustment)
            return Vector2D(int(limited_pos.x), int(limited_pos.y))
        
        self.logger.info(f"Found line intersection at ({intersection_x}, {intersection_y})")
        return intersection
    
    def refine_point_positions(self, left_image=None, right_image=None, iterations=1, convergence_threshold=2.0):
        """
        Refine all points by finding the center of white lines.
        
        This method iterates through all points and attempts to refine their positions
        by locating nearby white pixels (court lines) and centering the points on them.
        The process can be repeated multiple times to achieve higher precision.
        
        Args:
            left_image: QImage for the left camera (optional)
            right_image: QImage for the right camera (optional)
            iterations: Number of refinement iterations (default: 1)
            convergence_threshold: Stop iterating if average movement falls below this value in pixels (default: 2.0)
            
        Returns:
            tuple: (left_refined_count, right_refined_count) The number of points refined
        """
        left_refined = 0
        right_refined = 0
        
        # Process left camera points
        if left_image and left_image.width() > 0 and left_image.height() > 0:
            original_active = self.active_camera
            self.active_camera = "left"
            
            iteration_results = []
            
            # Start iteration loop
            for iteration in range(iterations):
                self.logger.info(f"Left camera refinement iteration {iteration+1}/{iterations}")
                
                iteration_movement = 0.0
                iteration_refined = 0
                
                # Process each point
                for i in range(len(self.left_key_points)):
                    current_pos = self.left_key_points[i]
                    refined_pos = self.find_white_center(i, left_image)
                    
                    if refined_pos:
                        # Calculate movement distance
                        movement = current_pos.distance_to(refined_pos)
                        iteration_movement += movement
                        
                        # Update point position
                        self.update_point(i, int(refined_pos.x), int(refined_pos.y))
                        iteration_refined += 1
                        
                        # Count as refined only on first iteration for return value
                        if iteration == 0:
                            left_refined += 1
                
                # Calculate average movement for this iteration
                avg_movement = iteration_movement / max(iteration_refined, 1)
                iteration_results.append((iteration_refined, avg_movement))
                
                self.logger.info(f"Iteration {iteration+1}: Refined {iteration_refined} points with avg movement of {avg_movement:.2f}px")
                
                # Check convergence - stop if average movement is below threshold
                if avg_movement < convergence_threshold:
                    self.logger.info(f"Convergence reached at iteration {iteration+1} (avg movement: {avg_movement:.2f}px)")
                    break
            
            # Restore original active camera
            self.active_camera = original_active
            
        # Process right camera points
        if right_image and right_image.width() > 0 and right_image.height() > 0:
            original_active = self.active_camera
            self.active_camera = "right"
            
            iteration_results = []
            
            # Start iteration loop
            for iteration in range(iterations):
                self.logger.info(f"Right camera refinement iteration {iteration+1}/{iterations}")
                
                iteration_movement = 0.0
                iteration_refined = 0
                
                # Process each point
                for i in range(len(self.right_key_points)):
                    current_pos = self.right_key_points[i]
                    refined_pos = self.find_white_center(i, right_image)
                    
                    if refined_pos:
                        # Calculate movement distance
                        movement = current_pos.distance_to(refined_pos)
                        iteration_movement += movement
                        
                        # Update point position
                        self.update_point(i, int(refined_pos.x), int(refined_pos.y))
                        iteration_refined += 1
                        
                        # Count as refined only on first iteration for return value
                        if iteration == 0:
                            right_refined += 1
                
                # Calculate average movement for this iteration
                avg_movement = iteration_movement / max(iteration_refined, 1)
                iteration_results.append((iteration_refined, avg_movement))
                
                self.logger.info(f"Iteration {iteration+1}: Refined {iteration_refined} points with avg movement of {avg_movement:.2f}px")
                
                # Check convergence - stop if average movement is below threshold
                if avg_movement < convergence_threshold:
                    self.logger.info(f"Convergence reached at iteration {iteration+1} (avg movement: {avg_movement:.2f}px)")
                    break
            
            # Restore original active camera
            self.active_camera = original_active
            
        self.logger.info(f"Refined {left_refined} left points and {right_refined} right points")
        return (left_refined, right_refined) 