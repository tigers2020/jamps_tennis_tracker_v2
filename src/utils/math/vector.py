"""
Vector2D Module
==============

Provides a 2D vector class for mathematical operations and position representation.
This module defines the Vector2D class that supports standard vector operations
and is used throughout the application for point and position representations.
"""

import math
from typing import Union, Tuple


class Vector2D:
    """
    A 2D vector class for representing points and vectors.
    
    This class provides all common vector operations and simplifies
    working with point coordinates throughout the application.
    """
    
    def __init__(self, x: Union[int, float] = 0, y: Union[int, float] = 0):
        """
        Initialize a 2D vector with x and y components.
        
        Args:
            x: The x component
            y: The y component
        """
        self.x = float(x)
        self.y = float(y)
        
    def __str__(self) -> str:
        """Return human-readable string representation"""
        return f"Vector2D({self.x:.1f}, {self.y:.1f})"
        
    def __repr__(self) -> str:
        """Return string representation for debugging"""
        return f"Vector2D({self.x}, {self.y})"
        
    def __eq__(self, other) -> bool:
        """
        Check if two vectors are equal.
        
        Args:
            other: Another Vector2D object
            
        Returns:
            bool: True if vectors are equal
        """
        if not isinstance(other, Vector2D):
            return False
        return abs(self.x - other.x) < 1e-6 and abs(self.y - other.y) < 1e-6
        
    def __add__(self, other) -> 'Vector2D':
        """
        Add two vectors.
        
        Args:
            other: Another Vector2D object
            
        Returns:
            Vector2D: Result of addition
        """
        if not isinstance(other, Vector2D):
            raise TypeError("Can only add Vector2D objects")
        return Vector2D(self.x + other.x, self.y + other.y)
        
    def __sub__(self, other) -> 'Vector2D':
        """
        Subtract another vector from this one.
        
        Args:
            other: Another Vector2D object
            
        Returns:
            Vector2D: Result of subtraction
        """
        if not isinstance(other, Vector2D):
            raise TypeError("Can only subtract Vector2D objects")
        return Vector2D(self.x - other.x, self.y - other.y)
        
    def __mul__(self, scalar: Union[int, float]) -> 'Vector2D':
        """
        Multiply vector by a scalar.
        
        Args:
            scalar: A number to multiply vector components by
            
        Returns:
            Vector2D: Result of multiplication
        """
        return Vector2D(self.x * scalar, self.y * scalar)
        
    def __rmul__(self, scalar: Union[int, float]) -> 'Vector2D':
        """Right multiplication for scalar * vector"""
        return self.__mul__(scalar)
        
    def __truediv__(self, scalar: Union[int, float]) -> 'Vector2D':
        """
        Divide vector by a scalar.
        
        Args:
            scalar: A number to divide vector components by
            
        Returns:
            Vector2D: Result of division
        """
        if abs(scalar) < 1e-6:
            raise ZeroDivisionError("Division by near-zero value")
        return Vector2D(self.x / scalar, self.y / scalar)
        
    def length(self) -> float:
        """
        Calculate the length (magnitude) of the vector.
        
        Returns:
            float: The length of the vector
        """
        return math.sqrt(self.x * self.x + self.y * self.y)
        
    def distance_to(self, other: 'Vector2D') -> float:
        """
        Calculate the Euclidean distance to another vector.
        
        Args:
            other: Another Vector2D object
            
        Returns:
            float: The distance between the two vectors
        """
        return (other - self).length()
        
    def normalized(self) -> 'Vector2D':
        """
        Get a normalized version of this vector.
        
        Returns:
            Vector2D: A vector with the same direction but length 1
        """
        length = self.length()
        if length < 1e-6:
            return Vector2D(0, 0)
        return self / length
        
    def dot(self, other: 'Vector2D') -> float:
        """
        Calculate the dot product with another vector.
        
        Args:
            other: Another Vector2D object
            
        Returns:
            float: The dot product
        """
        return self.x * other.x + self.y * other.y
        
    def to_tuple(self) -> Tuple[float, float]:
        """
        Convert vector to a tuple.
        
        Returns:
            tuple: A tuple of (x, y) components
        """
        return (self.x, self.y)
        
    def to_int_tuple(self) -> Tuple[int, int]:
        """
        Convert vector to an integer tuple.
        
        Returns:
            tuple: A tuple of (int(x), int(y)) components
        """
        return (int(self.x), int(self.y))
        
    @staticmethod
    def from_tuple(tuple_value: Tuple[Union[int, float], Union[int, float]]) -> 'Vector2D':
        """
        Create a Vector2D from a tuple.
        
        Args:
            tuple_value: A tuple of (x, y) values
            
        Returns:
            Vector2D: A new Vector2D object
        """
        return Vector2D(tuple_value[0], tuple_value[1])
        
    @staticmethod
    def from_normalized(norm_x: float, norm_y: float, width: int, height: int) -> 'Vector2D':
        """
        Create a Vector2D from normalized coordinates (0.0 to 1.0) and image dimensions.
        
        Args:
            norm_x: Normalized x coordinate (0.0 to 1.0)
            norm_y: Normalized y coordinate (0.0 to 1.0)
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Vector2D: A new Vector2D object with pixel coordinates
        """
        return Vector2D(norm_x * width, norm_y * height)
    
    def to_normalized(self, width: int, height: int) -> Tuple[float, float]:
        """
        Convert pixel coordinates to normalized coordinates (0.0 to 1.0).
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            tuple: (normalized_x, normalized_y) coordinates
        """
        return (self.x / width, self.y / height)
    
    def scale_to_resolution(self, src_width: int, src_height: int, 
                            dst_width: int, dst_height: int) -> 'Vector2D':
        """
        Scale a point from one resolution to another.
        
        Args:
            src_width: Source image width
            src_height: Source image height
            dst_width: Destination image width
            dst_height: Destination image height
            
        Returns:
            Vector2D: A new Vector2D scaled to the destination resolution
        """
        # Convert to normalized coordinates
        norm_x, norm_y = self.to_normalized(src_width, src_height)
        
        # Convert from normalized to destination resolution
        return Vector2D.from_normalized(norm_x, norm_y, dst_width, dst_height) 