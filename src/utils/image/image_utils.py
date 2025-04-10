"""
Calibration Image Utilities
=========================

Utilities for working with calibration images, rendering points,
and coordinate transformations.
"""

from typing import List, Tuple, Optional, Union

from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont

from src.utils.math.vector import Vector2D


def scale_pos_to_original(pos: QPoint, label_size: Tuple[int, int], 
                         pixmap_size: Tuple[int, int], scaled_size: Tuple[int, int]) -> Vector2D:
    """
    Convert a position from QLabel coordinates to original image coordinates.
    
    Args:
        pos: Position in QLabel coordinates
        label_size: Size of the QLabel (width, height)
        pixmap_size: Size of the original pixmap (width, height)
        scaled_size: Size of the scaled pixmap (width, height)
        
    Returns:
        Position in original image coordinates as Vector2D
    """
    # Extract dimensions
    label_width, label_height = label_size
    original_width, original_height = pixmap_size
    scaled_width, scaled_height = scaled_size
    
    # Calculate offsets (image centered in label)
    x_offset = (label_width - scaled_width) // 2
    y_offset = (label_height - scaled_height) // 2
    
    # Remove offsets to get position relative to scaled image
    image_x = pos.x() - x_offset
    image_y = pos.y() - y_offset
    
    # Check if position is outside image bounds
    if image_x < 0 or image_x >= scaled_width or image_y < 0 or image_y >= scaled_height:
        return Vector2D(-1, -1)  # Invalid position
    
    # Scale position to original image size
    original_x = int(image_x * original_width / scaled_width)
    original_y = int(image_y * original_height / scaled_height)
    
    # Ensure coordinates are within original image bounds
    original_x = max(0, min(original_x, original_width - 1))
    original_y = max(0, min(original_y, original_height - 1))
    
    return Vector2D(original_x, original_y)


def draw_calibration_points(pixmap: QPixmap, points: List[Union[Vector2D, Tuple[int, int]]], 
                           selected_idx: int = -1, total_points: int = 12, 
                           is_monitoring_view: bool = False,
                           point_color: Optional[QColor] = None,
                           selected_color: Optional[QColor] = None) -> None:
    """
    Draw calibration points on a pixmap with proper styling.
    
    Args:
        pixmap: The pixmap to draw on
        points: List of Vector2D objects or (x, y) coordinate tuples
        selected_idx: Index of the currently selected point (-1 if none)
        total_points: Total expected number of points
        is_monitoring_view: If True, uses more prominent styling for monitoring view
        point_color: Optional custom color for points (overrides default line colors)
        selected_color: Optional custom color for selected point
        
    Note:
        This function modifies the pixmap in-place
    """
    # Initialize painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Calculate scale factor based on image dimensions
    # Base reference is 640x480 - scale relative to this size
    width, height = pixmap.width(), pixmap.height()
    size_scale = min(width / 640.0, height / 480.0)
    
    # Use larger sizes for monitoring view
    if is_monitoring_view:
        # Use much larger values for monitoring view
        base_line_width = max(3, int(5 * size_scale))  # 더 두꺼운 선
        base_point_size = max(14, int(18 * size_scale))  # 더 큰 점
        selected_point_size = max(18, int(22 * size_scale))  # 더 큰 선택된 점
        cross_size = max(10, int(14 * size_scale))  # 더 큰 십자선
        transparency = 255  # 완전 불투명
    else:
        # Standard sizes for calibration view
        base_line_width = max(1, int(1 * size_scale))
        base_point_size = max(6, int(6 * size_scale)) 
        selected_point_size = max(10, int(10 * size_scale))
        cross_size = max(5, int(5 * size_scale))
        transparency = 150  # Semi-transparent
    
    # Color settings
    line_colors = [
        QColor(255, 0, 0, transparency),    # Red
        QColor(0, 255, 0, transparency),    # Green
        QColor(0, 0, 255, transparency)     # Blue
    ]
    
    # Use custom colors if provided
    default_selected_color = QColor(255, 255, 0, transparency)  # Yellow
    if selected_color is None:
        selected_color = default_selected_color
    else:
        # Apply transparency to custom color
        custom_selected = QColor(selected_color)
        custom_selected.setAlpha(transparency)
        selected_color = custom_selected
    
    # Draw lines if all points are available
    draw_lines = len(points) == total_points
    
    if draw_lines:
        # Points per line
        line1_count = 5  # First line: points 1-5
        line2_count = 3  # Second line: points 6-8
        line3_count = 4  # Third line: points 9-12
        
        # Line ranges (start, end) - end is exclusive
        line_ranges = [
            (0, line1_count),
            (line1_count, line1_count + line2_count),
            (line1_count + line2_count, total_points)
        ]
        
        # Draw horizontal lines
        for line_idx, (start, end) in enumerate(line_ranges):
            if end - start < 2:  # Skip if less than 2 points
                continue
                
            # Extract and sort points for this line
            line_points = points[start:end]
            
            # Get x,y coordinates for sorting and drawing
            def get_point_coords(p):
                if isinstance(p, Vector2D):
                    return (p.x, p.y)
                return p
                
            # Sort points by x-coordinate
            sorted_line_points = sorted(line_points, key=lambda p: get_point_coords(p)[0] if isinstance(p, Vector2D) else p[0])
            
            # Set line style
            line_pen = QPen(line_colors[line_idx])
            line_pen.setWidth(base_line_width)  # Scale line width
            painter.setPen(line_pen)
            
            # Draw line segments
            for j in range(len(sorted_line_points) - 1):
                p1 = sorted_line_points[j]
                p2 = sorted_line_points[j+1]
                
                # Get coordinates for drawing
                p1_coords = (p1.x, p1.y) if isinstance(p1, Vector2D) else p1
                p2_coords = (p2.x, p2.y) if isinstance(p2, Vector2D) else p2
                
                painter.drawLine(int(p1_coords[0]), int(p1_coords[1]), 
                                int(p2_coords[0]), int(p2_coords[1]))
    
    # Draw vertical connections if all points are present
    if len(points) == total_points:
        # Connection groups (indices)
        connection_groups = [
            [(0, 8)],                 # 1-9
            [(1, 5), (5, 9)],         # 2-6-10
            [(2, 6)],                 # 3-7
            [(3, 7), (7, 10)],        # 4-8-11
            [(4, 11)]                 # 5-12
        ]
        
        # Connection style - dashed orange
        connection_pen = QPen(QColor(255, 165, 0, transparency))  # Orange
        connection_pen.setWidth(base_line_width)  # Scale line width
        connection_pen.setStyle(Qt.DashLine)  # Dashed line style
        painter.setPen(connection_pen)
        
        # Draw each connection
        for connections in connection_groups:
            for start_idx, end_idx in connections:
                if start_idx < len(points) and end_idx < len(points):
                    p1 = points[start_idx]
                    p2 = points[end_idx]
                    
                    # Get coordinates for drawing
                    p1_coords = (p1.x, p1.y) if isinstance(p1, Vector2D) else p1
                    p2_coords = (p2.x, p2.y) if isinstance(p2, Vector2D) else p2
                    
                    painter.drawLine(int(p1_coords[0]), int(p1_coords[1]), 
                                    int(p2_coords[0]), int(p2_coords[1]))
    
    # Draw individual points with background outline for better visibility
    for i, point in enumerate(points):
        # Get point coordinates
        point_coords = (point.x, point.y) if isinstance(point, Vector2D) else point
        
        # Determine line (for color)
        line_idx = 0
        if draw_lines:
            for j, (start, end) in enumerate(line_ranges):
                if start <= i < end:
                    line_idx = j
                    break
        
        # Check if this is the selected point
        is_selected = (i == selected_idx)
        
        # Draw black outline/background for better visibility
        if is_monitoring_view:
            outline_pen = QPen(QColor(0, 0, 0, 255))  # Black outline
            outline_pen.setWidth(base_line_width + 4)  # 더 두꺼운 테두리
            painter.setPen(outline_pen)
            
            # Draw crosshair outline
            painter.drawLine(int(point_coords[0])-cross_size-2, int(point_coords[1]), 
                            int(point_coords[0])+cross_size+2, int(point_coords[1]))
            painter.drawLine(int(point_coords[0]), int(point_coords[1])-cross_size-2, 
                            int(point_coords[0]), int(point_coords[1])+cross_size+2)
            
            # 원 외곽선 추가 (더 눈에 띄게)
            circle_size = selected_point_size if is_selected else base_point_size
            painter.drawEllipse(int(point_coords[0])-circle_size/2-2, int(point_coords[1])-circle_size/2-2, 
                               circle_size+4, circle_size+4)
        
        # Draw precise position crosshair
        cross_pen = QPen(QColor(255, 255, 255, 255))  # Fully opaque white
        cross_pen.setWidth(base_line_width)
        painter.setPen(cross_pen)
        
        painter.drawLine(int(point_coords[0])-cross_size, int(point_coords[1]), 
                        int(point_coords[0])+cross_size, int(point_coords[1]))
        painter.drawLine(int(point_coords[0]), int(point_coords[1])-cross_size, 
                        int(point_coords[0]), int(point_coords[1])+cross_size)
        
        # Determine point color - custom or default
        if is_selected:
            curr_color = selected_color
        elif point_color is not None:
            # Use provided custom color
            curr_color = QColor(point_color)
            curr_color.setAlpha(transparency)
        else:
            # Use default line color
            curr_color = line_colors[line_idx]
            
        # Set point style
        point_pen = QPen(curr_color)
        point_pen.setWidth(base_line_width)
        painter.setPen(point_pen)
        
        # Draw circle with scaled size
        circle_size = selected_point_size if is_selected else base_point_size
        
        # For monitoring view, make the fill color more opaque
        if is_monitoring_view:
            fill_color = QColor(curr_color)
            fill_color.setAlpha(255)  # 완전 불투명
        else:
            fill_color = QColor(curr_color)
            fill_color.setAlpha(120)  # More transparent
            
        painter.setBrush(fill_color)
        
        # Draw the point as a circle
        painter.drawEllipse(
            int(point_coords[0] - circle_size/2),
            int(point_coords[1] - circle_size/2),
            circle_size,
            circle_size
        )
        
        # Draw point number if monitoring view
        if is_monitoring_view:
            # Use an easy-to-read label style
            text_bg_color = QColor(0, 0, 0, 200)  # Semi-transparent black background
            text_color = QColor(255, 255, 255)  # White text
            
            font = painter.font()
            font.setBold(True)
            font.setPointSize(10)
            painter.setFont(font)
            
            # Draw text background
            text_rect = QRect(
                int(point_coords[0] + circle_size/2 + 2),
                int(point_coords[1] - 10),
                16, 
                20
            )
            
            painter.fillRect(text_rect, text_bg_color)
            
            # Draw text
            painter.setPen(text_color)
            painter.drawText(text_rect, Qt.AlignCenter, str(i+1))
    
    # End painting
    painter.end() 