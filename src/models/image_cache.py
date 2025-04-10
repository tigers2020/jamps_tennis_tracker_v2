"""
Image Cache Module

This module provides a class for efficiently caching and retrieving images
to improve performance in the Tennis Ball Tracker application.
"""

import os
from PySide6.QtGui import QPixmap, QImage
from src.utils.logger import Logger
from PySide6.QtCore import Qt
import time

class ImageCache:
    """
    Manages a cache of loaded images to improve performance.
    
    This class handles:
    - Loading images directly to GPU memory
    - Caching loaded images for faster access
    - Retrieving cached images
    """
    
    def __init__(self):
        """Initialize the image cache"""
        self._cache = {}
        self._max_size = 2000  # Increased maximum cache size for full loading
        self.logger = Logger.instance()
        self.cache_hits = 0
        self.cache_misses = 0
        self.last_access = {}
    
    def __len__(self):
        """Return the number of cached images"""
        return len(self._cache)
    
    def __iter__(self):
        """Return iterator of cached image paths"""
        return iter(self._cache.keys())
    
    def clear(self):
        """Clear the cache"""
        self._cache.clear()
        self.last_access.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        self.logger.debug("Image cache cleared")
    
    def get_image(self, image_path):
        """
        Get an image from the cache or load it directly to GPU.
        This is the primary method for image loading and GPU caching.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            QPixmap: Loaded image in GPU memory or None if failed
        """
        try:
            # Check for empty path
            if not image_path:
                self.logger.warning("Empty image path provided")
                return None
            
            # Skip PNG files
            if image_path.lower().endswith('.png'):
                self.logger.debug(f"Skipping PNG file: {image_path}")
                return None
                
            # Return from cache if already loaded
            if image_path in self._cache:
                cached_pixmap = self._cache[image_path]
                self.cache_hits += 1
                self.last_access[image_path] = time.time()
                return cached_pixmap
                
            # Check if file exists
            if not os.path.exists(image_path):
                self.logger.error(f"Image file does not exist: {image_path}")
                return None
                
            # Load image from file directly to GPU memory
            try:
                # QPixmap loads directly to GPU memory
                pixmap = QPixmap(image_path)
                
                if not pixmap.isNull():
                    # Store in cache
                    self._cache[image_path] = pixmap
                    self.last_access[image_path] = time.time()
                    self.cache_misses += 1
                    self.logger.debug(f"Image loaded to GPU memory: {image_path}")
                    return pixmap
                
                # If QPixmap loading fails, try QImage as fallback
                image = QImage(image_path)
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    self._cache[image_path] = pixmap
                    self.last_access[image_path] = time.time()
                    self.cache_misses += 1
                    self.logger.debug(f"Image loaded to GPU via QImage: {image_path}")
                    return pixmap
                
                self.logger.error(f"Failed to load image: {image_path}")
                return None
                
            except Exception as e:
                self.logger.error(f"Error loading image: {str(e)}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error in image cache: {str(e)}")
            return None
    
    def load_all_images(self, image_paths):
        """
        Load all images from a list of paths directly to GPU memory.
        
        Args:
            image_paths: List of image paths to load
            
        Returns:
            int: Number of successfully loaded images
        """
        if not image_paths:
            return 0
            
        # Clear cache if needed before bulk loading
        if len(self._cache) > self._max_size // 2:
            self.logger.info("Clearing cache before full image loading")
            self.clear()
        
        self.logger.info(f"Loading all {len(image_paths)} images to GPU memory")
        loaded_count = 0
        
        # Load all images in sequence
        for path in image_paths:
            # Skip PNG files and already cached images
            if path.lower().endswith('.png') or path in self._cache:
                continue
                
            if self.get_image(path) is not None:
                loaded_count += 1
        
        self.logger.info(f"Successfully loaded {loaded_count} images to GPU")
        return loaded_count
    
    def is_cached(self, path):
        """
        Check if an image is already in the cache/GPU memory
        
        Args:
            path: Path to the image
            
        Returns:
            bool: True if the image is in the cache, False otherwise
        """
        return path in self._cache
    
    def get_cache_size(self):
        """
        Get the number of images in the cache
        
        Returns:
            int: Number of images in the cache
        """
        return len(self._cache)
    
    def get_cached_paths(self):
        """
        Get a list of cached image paths
        
        Returns:
            list: List of cached image paths
        """
        return list(self._cache.keys()) 