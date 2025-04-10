"""
File Utilities Module

This module provides utility functions for file operations
used in the Tennis Ball Tracker application.
"""

import os
import json
from pathlib import Path
from src.utils.logger import Logger

class FileUtils:
    """
    Utility class for file system operations
    
    This class provides methods for:
    - Checking if files exist
    - Loading JSON files
    - Identifying image files
    - Listing files in directories
    """
    
    # Supported image extensions
    IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
    
    @staticmethod
    def is_image_file(file_path):
        """
        Check if a file is an image file based on its extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if it's an image file, False otherwise
        """
        if not file_path:
            return False
            
        ext = os.path.splitext(file_path)[1].lower()
        return ext in FileUtils.IMAGE_EXTENSIONS
    
    @staticmethod
    def load_json_file(file_path):
        """
        Load JSON data from a file
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            dict: JSON data or None if loading failed
        """
        logger = Logger.instance()
        
        if not file_path or not os.path.exists(file_path):
            logger.error(f"JSON file does not exist: {file_path}")
            return None
            
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON file: {str(e)}")
            return None
    
    @staticmethod
    def get_image_files_in_directory(directory):
        """
        Get all image files in the specified directory
        
        Args:
            directory: Directory path to search for images
            
        Returns:
            list: List of image file paths
        """
        try:
            # Normalize path
            directory = os.path.normpath(directory)
            
            # Check if directory exists
            if not os.path.exists(directory):
                Logger.instance().error(f"Directory does not exist: {directory}")
                return []
            
            if not os.path.isdir(directory):
                Logger.instance().error(f"Path is not a directory: {directory}")
                return []
            
            # Get all files in directory
            files = os.listdir(directory)
            
            # Filter for image files
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
            image_files = []
            
            for file in files:
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in image_extensions:
                        image_files.append(file_path)
            
            # Sort files by name
            image_files.sort()
            
            Logger.instance().debug(f"Found {len(image_files)} image files in {directory}")
            return image_files
            
        except Exception as e:
            Logger.instance().error(f"Error getting image files from {directory}: {str(e)}")
            return []
    
    @staticmethod
    def ensure_directory_exists(path):
        """
        Ensure the directory for a file path exists
        
        Args:
            path: File path
            
        Returns:
            bool: True if directory exists or was created, False otherwise
        """
        logger = Logger.instance()
        
        try:
            # Get directory from file path
            directory = os.path.dirname(path)
            
            # If no directory specified or directory already exists, return True
            if not directory or os.path.exists(directory):
                return True
                
            # Create directory
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creating directory: {str(e)}")
            return False

    @classmethod
    def list_directory(cls, directory, pattern=None, recursive=False):
        """
        List files in a directory, optionally filtered by pattern
        
        Args:
            directory (str): Directory path to list
            pattern (str, optional): File pattern to match (e.g., "*.jpg")
            recursive (bool): Whether to list files recursively
            
        Returns:
            list: List of file paths
        """
        logger = Logger.instance()
        
        try:
            if not os.path.exists(directory):
                logger.error(f"Directory does not exist: {directory}")
                return []
                
            if not os.path.isdir(directory):
                logger.error(f"Path is not a directory: {directory}")
                return []
                
            result = []
            
            # Function to check if file matches pattern
            def match_pattern(filename):
                if not pattern:
                    return True
                    
                import fnmatch
                return fnmatch.fnmatch(filename, pattern)
            
            if recursive:
                # Walk the directory tree
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if match_pattern(file):
                            result.append(os.path.join(root, file))
            else:
                # Just list the files in the specified directory
                for item in os.listdir(directory):
                    full_path = os.path.join(directory, item)
                    if os.path.isfile(full_path) and match_pattern(item):
                        result.append(full_path)
            
            logger.info(f"Found {len(result)} files in directory: {directory}")
            return result
            
        except Exception as e:
            logger.error(f"Error listing directory {directory}: {str(e)}")
            return [] 