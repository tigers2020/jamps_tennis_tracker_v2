"""
Image Manager Module

This module defines a singleton class that manages images loaded from a folder
for the Tennis Ball Tracker application.
"""

import os
import json
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap, QImage

from src.models.singleton import qt_singleton
from src.models.image_cache import ImageCache
from src.controllers.frame_manager import FrameManager
from src.utils.file_utils import FileUtils
from src.utils.logger import Logger

@qt_singleton
class ImageManager(QObject):
    """
    Singleton class for managing images used in the application.
    
    This class provides functionality to:
    - Load images from a folder
    - Load and manage frames from JSON files
    - Navigate through images and frames
    - Access images efficiently with caching
    """
    
    # Camera types
    CAMERA_LEFT = "left"
    CAMERA_RIGHT = "right"
    
    # Signals for state changes
    images_loaded_changed = Signal(list)  # List of image paths
    current_image_changed = Signal(str)   # Current image path
    image_folder_changed = Signal(str)    # Image folder path
    frames_loaded = Signal(int)           # Number of frames loaded
    
    def __init__(self):
        # Call QObject constructor
        super(ImageManager, self).__init__()
        
        # Initialize internal state
        self._initialize_state()
        
        # Initialize components
        self._image_cache = ImageCache()
        self._frame_manager = FrameManager()
        
        # Logger
        self.logger = Logger.instance()
        
        # Additional state variables
        self._last_used_folder = ""
        self._last_file_path = ""
        self._load_last_used_folder()
    
    def _initialize_state(self):
        """Initialize or reset the internal state variables"""
        # Path variables
        self._image_folder = ""
        self._image_paths = []
        self._current_image_index = 0
        self._current_image_path = ""
    
    def _handle_load_error(self, error_msg, exception=None):
        """Handle loading errors with consistent logging
        
        Args:
            error_msg: Error message to log
            exception: Optional exception that was caught
            
        Returns:
            bool: Always returns False to indicate failure
        """
        if exception:
            self.logger.error(f"{error_msg}: {str(exception)}")
        else:
            self.logger.error(error_msg)
        return False
    
    #
    # Image folder loading methods
    #
    
    def load_folder(self, folder_path):
        """Load images from a specified folder.
        
        Args:
            folder_path (str): Path to the image folder
            
        Returns:
            bool: Success status
        """
        # Check if folder path is empty or doesn't exist
        if not folder_path or not os.path.exists(folder_path):
            self.logger.error(f"Invalid folder path: {folder_path}")
            self.image_folder_changed.emit(None)
            return False
        
        self.logger.info(f"Loading images from folder: {folder_path}")
        
        # Check for frames_info.json in the folder
        json_path = os.path.join(folder_path, "frames_info.json")
        if os.path.exists(json_path):
            self.logger.info(f"Found frames_info.json, loading frames from JSON")
            return self.load_images_from_json(json_path)
        
        # Look for resize folders with images
        resize_folder_left = os.path.join(folder_path, "LeftCamera", "resize")
        resize_folder_right = os.path.join(folder_path, "RightCamera", "resize")
        
        if os.path.exists(resize_folder_left) or os.path.exists(resize_folder_right):
            self.logger.info(f"Using resize folders for images")
            all_images = []
            
            # Get all image files from resize folders (any format)
            if os.path.exists(resize_folder_left):
                for file in os.listdir(resize_folder_left):
                    if file.lower().endswith(('.jpg', '.jpeg')):
                        file_path = os.path.join(resize_folder_left, file)
                        all_images.append(file_path)
            
            if os.path.exists(resize_folder_right):
                for file in os.listdir(resize_folder_right):
                    if file.lower().endswith(('.jpg', '.jpeg')):
                        file_path = os.path.join(resize_folder_right, file)
                        all_images.append(file_path)
            
            if not all_images:
                self.logger.error(f"No valid images found in resize folders")
                self.image_folder_changed.emit(None)
                return False
            
            # Organize images by camera type
            self.image_folder = folder_path
            self._organize_images_by_camera(all_images)
            
            if not self._left_images and not self._right_images:
                self.logger.error("No valid camera images found")
                self.image_folder_changed.emit(None)
                return False
            
            self.logger.info(f"Successfully loaded {len(self._left_images)} left camera images "
                           f"and {len(self._right_images)} right camera images")
            
            # Save last used folder
            self._save_last_used_folder(folder_path)
            self.image_folder_changed.emit(folder_path)
            
            # Set first image index
            self.set_current_frame(0)
            self.images_loaded_changed.emit(True)
            
            # Load all images to GPU at once
            self.load_to_gpu()
            
            return True
        
        # If we get here, we couldn't find any images
        self.logger.error(f"No valid image folders found in: {folder_path}")
        self.image_folder_changed.emit(None)
        return False
    
    def _organize_images_by_camera(self, images):
        """
        Organize loaded images by camera type (left/right)
        
        This method sorts images into left and right camera groups based on filename patterns.
        It populates _left_images and _right_images dictionaries where keys are frame numbers
        and values are image paths.
        """
        if not images:
            return
            
        # Initialize dictionaries for left and right camera images
        self._left_images = {}
        self._right_images = {}
        
        # Patterns to identify camera type from filename
        left_patterns = ['left', 'leftcamera', 'left_camera', 'lcam', 'camera1', 'cam1']
        right_patterns = ['right', 'rightcamera', 'right_camera', 'rcam', 'camera2', 'cam2']
        
        # Keep track of frames without paired images
        unpaired_left = []
        unpaired_right = []
        
        # First pass: Try to match images based on filename patterns
        for image_path in images:
            basename = os.path.basename(image_path).lower()
            frame_num = None
            
            # Try to extract frame number from filename
            import re
            frame_match = re.search(r'(?:frame|frm)_?(\d+)', basename)
            if frame_match:
                frame_num = int(frame_match.group(1))
            
            # Determine camera type based on filename patterns
            is_left = any(pattern in basename.replace('_', '') for pattern in left_patterns)
            is_right = any(pattern in basename.replace('_', '') for pattern in right_patterns)
            
            if is_left and frame_num is not None:
                self._left_images[frame_num] = image_path
                if frame_num not in self._right_images:
                    unpaired_left.append(frame_num)
            elif is_right and frame_num is not None:
                self._right_images[frame_num] = image_path
                if frame_num not in self._left_images:
                    unpaired_right.append(frame_num)
            else:
                # If we can't determine the camera type or frame number, 
                # just add to left images with an arbitrary frame number
                if not self._left_images:
                    self._left_images[1] = image_path
                    unpaired_left.append(1)
                else:
                    max_frame = max(self._left_images.keys()) if self._left_images else 0
                    self._left_images[max_frame + 1] = image_path
                    unpaired_left.append(max_frame + 1)
        
        # Second pass: Try to pair unpaired images
        if unpaired_left and unpaired_right:
            self.logger.debug(f"Found {len(unpaired_left)} unpaired left images and {len(unpaired_right)} unpaired right images")
            
            # Sort unpaired frames
            unpaired_left.sort()
            unpaired_right.sort()
            
            # Try to pair as many as possible
            for i in range(min(len(unpaired_left), len(unpaired_right))):
                left_frame = unpaired_left[i]
                right_frame = unpaired_right[i]
                
                # If left frame doesn't have a matching right frame, assign one
                if left_frame not in self._right_images:
                    self._right_images[left_frame] = self._right_images[right_frame]
                    del self._right_images[right_frame]
                    unpaired_right.remove(right_frame)
        
        # If we have left images without matching right images, duplicate left as right
        for frame_num in self._left_images.keys():
            if frame_num not in self._right_images:
                self._right_images[frame_num] = self._left_images[frame_num]
                self.logger.debug(f"No right camera image for frame {frame_num}, using left camera image")
        
        # If we have right images without matching left images, duplicate right as left
        for frame_num in self._right_images.keys():
            if frame_num not in self._left_images:
                self._left_images[frame_num] = self._right_images[frame_num]
                self.logger.debug(f"No left camera image for frame {frame_num}, using right camera image")
        
        # Log the results
        self.logger.debug(f"Organized {len(self._left_images)} left camera images and {len(self._right_images)} right camera images")

    def _reset_state(self):
        """Reset the state variables and clear cache"""
        self._initialize_state()
        if hasattr(self, '_image_cache'):
            self._image_cache.clear()
    
    def _preload_images(self, max_preload=50):
        """
        Preload images into cache.
        
        Args:
            max_preload: Maximum number of images to preload
        """
        if not self._image_paths:
            return
        
        # Clear cache if too large
        if len(self._image_cache) > 1000:
            self.logger.debug("Clearing cache due to size limit")
            self._image_cache.clear()
        
        # Only preload images before and after current frame
        current_index = self._current_image_index
        start_index = max(0, current_index - max_preload // 2)
        end_index = min(len(self._image_paths), current_index + max_preload // 2)
        
        # Log preload operation
        self.logger.debug(f"Preloading images...")
        self.logger.debug(f"Starting image preloading: indexes {start_index} to {end_index}")
        
        # Execute preload
        loaded_count = 0
        for path in self._image_paths[start_index:end_index]:
            # Skip PNG files
            if path.lower().endswith('.png'):
                self.logger.debug(f"Skipping PNG file during preload: {path}")
                continue
            
            if path not in self._image_cache:
                if self._image_cache.get_image(path) is not None:
                    loaded_count += 1
                    self.logger.debug(f"Image preloading successful: {path}")
        
        if loaded_count > 0:
            self.logger.debug(f"Preloaded {loaded_count} new images into cache")
    
    #
    # Frame loading methods
    #
    
    def load_frames_info(self, frames_info):
        """
        JSON에서 프레임 정보를 로드합니다.
        
        Args:
            frames_info: 프레임 정보가 있는 JSON 데이터
            
        Returns:
            bool: 성공 여부
        """
        try:
            if not frames_info:
                self.logger.warning("No frames info provided")
                return False
                
            # json_frames를 dict 형태로 변환
            self.frames = {}
            for frame in frames_info:
                frame_number = int(frame.get('frame_number', 0))
                self.frames[frame_number] = frame
                
            # 사용 가능한 프레임을 정렬
            self.available_frames = sorted(list(self.frames.keys()))
            
            # 사용 가능한 프레임이 없는 경우
            if not self.available_frames:
                self.logger.warning("No frames available after loading frames info")
                return False
                
            self.logger.info(f"Successfully loaded {len(self.available_frames)} frames")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading frames info: {str(e)}")
            return False
    
    def load_images_from_json(self, json_file_path):
        """
        Load images from a JSON file path. This is the preferred method.
        
        Args:
            json_file_path: Path to the frames_info.json file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prevent duplicate loading
            base_path = os.path.dirname(json_file_path)
            if self._image_folder == base_path and self._image_paths and self._frame_manager.is_loaded():
                self.logger.debug(f"JSON file already loaded: {json_file_path}")
                return True
            
            # Reset state before loading new frames
            self._reset_state()
            
            # Load frames info
            if not self._frame_manager.load_from_json(json_file_path):
                return self._handle_load_error("Failed to load frames info from JSON")
            
            # Set base path
            self._image_folder = self._frame_manager.get_base_path()
            
            # Get paths for left camera frames
            self._image_paths = self._frame_manager.get_frame_paths(camera=self.CAMERA_LEFT)
            
            # If we found any images, set the current image to the first one
            if self._image_paths:
                self._current_image_path = self._image_paths[0]
            
            # Emit signals
            total_frames = self._frame_manager.get_total_frames()
            self._emit_state_changes(total_frames)
            
            # Load all images to GPU at once
            self.load_to_gpu()
            
            self.logger.info(f"Successfully loaded {total_frames} frames from {json_file_path}")
            return True
            
        except Exception as e:
            return self._handle_load_error("Error loading images from JSON", e)
    
    def load_to_gpu(self, max_frames=None):
        """
        Load all images to GPU memory at once.
        This is the only method for loading images to GPU.
        
        Args:
            max_frames: Maximum number of frames to load (None for all)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info("Loading all images to GPU memory...")
            
            # Determine image paths to load based on camera type
            left_paths = []
            right_paths = []
            
            # Get total number of frames
            total_frames = self.get_total_images()
            if total_frames == 0:
                return self._handle_load_error("No images available to load to GPU")
                
            frames_to_load = total_frames if max_frames is None else min(max_frames, total_frames)
            
            # Collect all image paths
            for frame_number in range(1, frames_to_load + 1):
                left_path = self.get_frame_path(frame_number, self.CAMERA_LEFT)
                if left_path and not left_path.lower().endswith('.png'):
                    left_paths.append(left_path)
                
                right_path = self.get_frame_path(frame_number, self.CAMERA_RIGHT)
                if right_path and not right_path.lower().endswith('.png'):
                    right_paths.append(right_path)
            
            self.logger.info(f"Found {len(left_paths)} left and {len(right_paths)} right camera images")
            
            # Load all images at once using the optimized method
            left_loaded = self._image_cache.load_all_images(left_paths)
            right_loaded = self._image_cache.load_all_images(right_paths)
            
            total_loaded = left_loaded + right_loaded
            self.logger.info(f"Successfully loaded all {total_loaded} images to GPU memory")
            return True
            
        except Exception as e:
            return self._handle_load_error("Error loading images to GPU", e)
    
    #
    # Signal emission
    #
    
    def _emit_state_changes(self, total_frames=None):
        """
        Emit signals to notify of state changes
        
        Args:
            total_frames: Optional total number of frames to emit
        """
        self.images_loaded_changed.emit(self._image_paths)
        self.image_folder_changed.emit(self._image_folder)
        
        if self._current_image_path:
            self.current_image_changed.emit(self._current_image_path)
        
        if total_frames is not None:
            self.frames_loaded.emit(total_frames)
    
    #
    # Image access methods (consolidated)
    #
    
    def get_images(self, frame_number=None):
        """
        Get both left and right camera images for a frame
        
        Args:
            frame_number: Frame number to get (if None, use current index)
        
        Returns:
            tuple: (left_image, right_image) as QPixmap objects, may be None if not found
        """
        left_image, right_image = None, None
        try:
            # Get left camera path and image
            left_path = self.get_frame_path(frame_number, self.CAMERA_LEFT)
            if left_path:
                left_image = self._image_cache.get_image(left_path)
            
            # Get right camera path and image
            right_path = self.get_frame_path(frame_number, self.CAMERA_RIGHT)
            if right_path:
                right_image = self._image_cache.get_image(right_path)
            
            return left_image, right_image
            
        except Exception as e:
            self.logger.error(f"Error getting images: {str(e)}")
            return None, None

    def get_frame_path(self, frame_number=None, camera="left"):
        """
        Unified method to get an image path by frame number or index
        
        Args:
            frame_number: Frame number or index (if None, use current index)
            camera: Camera type ('left' or 'right')
        
        Returns:
            str: The image path or empty string if not found
        """
        # Handle frame-based access (when using frame_manager)
        if self._frame_manager.get_frames_info():
            if frame_number is None:
                frame_number = self._current_image_index + 1
            
            path = self._frame_manager.get_frame_path(frame_number, camera)
            return path if path else ""
        
        # Handle index-based access for regular image folder
        if not self._image_paths:
            return ""
        
        # Convert index to frame number if needed
        if frame_number is None:
            frame_number = self._current_image_index + 1
        else:
            # Handle zero-based index
            if frame_number == 0:
                frame_number = 1
        
        # Use organized camera images if available
        if hasattr(self, '_left_images') and hasattr(self, '_right_images'):
            if camera.lower() == self.CAMERA_LEFT:
                # Get frame from left camera dictionary
                if frame_number in self._left_images:
                    return self._left_images[frame_number]
                # Try to adjust frame number - it might be an index
                elif frame_number <= len(self._left_images):
                    sorted_keys = sorted(self._left_images.keys())
                    if 0 <= frame_number - 1 < len(sorted_keys):
                        return self._left_images[sorted_keys[frame_number - 1]]
            else:
                # Get frame from right camera dictionary
                if frame_number in self._right_images:
                    return self._right_images[frame_number]
                # Try to adjust frame number - it might be an index
                elif frame_number <= len(self._right_images):
                    sorted_keys = sorted(self._right_images.keys())
                    if 0 <= frame_number - 1 < len(sorted_keys):
                        return self._right_images[sorted_keys[frame_number - 1]]
        
        # Fallback to simple index-based access
        idx = frame_number - 1
        if 0 <= idx < len(self._image_paths):
            # If only one list exists, assume it's the left camera
            return self._image_paths[idx]
        
        return ""
    
    #
    # Navigation methods
    #
    
    def set_current_index(self, index):
        """
        Set the current image index
        
        Args:
            index: The new image index
        
        Returns:
            bool: True if successful, False otherwise
        """
        total_images = self.get_total_images()
        if total_images == 0:
            return False
        
        if not (0 <= index < total_images):
            # Allow wrapping around
            index = index % total_images
            
        self._current_image_index = index
        # Update path based on index, primarily using left path for compatibility
        self._current_image_path = self.get_frame_path(index + 1, self.CAMERA_LEFT)
        self.current_image_changed.emit(self._current_image_path)
        return True
    
    def next_image(self):
        """
        Move to the next image
        
        Returns:
            bool: True if successful, False otherwise
        """
        total_images = self.get_total_images()
        if total_images == 0:
            return False
        
        next_index = (self._current_image_index + 1) % total_images
        return self.set_current_index(next_index)
    
    def previous_image(self):
        """
        Move to the previous image
        
        Returns:
            bool: True if successful, False otherwise
        """
        total_images = self.get_total_images()
        if total_images == 0:
            return False
        
        prev_index = (self._current_image_index - 1 + total_images) % total_images
        return self.set_current_index(prev_index)
    
    #
    # Information methods (consolidated)
    #
    
    def get_total_images(self):
        """
        Get the total number of loaded images/frames
        
        Returns:
            int: Total number of images/frames
        """
        if self._frame_manager.get_frames_info():
            return self._frame_manager.get_total_frames()
        # Use the length of the organized left images if available, else the raw paths
        if hasattr(self, '_left_images') and self._left_images:
            return len(self._left_images)
        return len(self._image_paths)
    
    def get_current_index(self):
        """
        Get the current image index
        
        Returns:
            int: Current image index
        """
        return self._current_image_index
    
    def get_folder_path(self):
        """
        Get the current image folder path
        
        Returns:
            str: Folder path
        """
        return self._image_folder
    
    def get_loaded_frames(self):
        """
        Get all loaded frames information
        
        Returns:
            list: List of dictionaries containing frame information
                 Each dictionary contains 'frame_num', 'camera_type', and 'image_path'
        """
        result = []
        total_frames = self.get_total_images()
        
        if total_frames == 0:
            return []
            
        # Extract frame information for both cameras
        for frame_num in range(1, total_frames + 1):
            left_path = self.get_frame_path(frame_num, self.CAMERA_LEFT)
            right_path = self.get_frame_path(frame_num, self.CAMERA_RIGHT)
            
            if left_path:
                result.append({
                    'frame_num': frame_num,
                    'camera_type': self.CAMERA_LEFT,
                    'image_path': left_path
                })
            if right_path and right_path != left_path: # Avoid duplicate if right falls back to left
                result.append({
                    'frame_num': frame_num,
                    'camera_type': self.CAMERA_RIGHT,
                    'image_path': right_path
                })
        
        return result
    
    def clear(self):
        """Clear all loaded images and reset state"""
        self._reset_state()
        self._emit_state_changes(0)

    def set_base_path(self, base_path):
        """Set the base path in the frame manager and update image folder"""
        self._frame_manager.set_base_path(base_path)
        self._image_folder = base_path 

    def _load_last_used_folder(self):
        """Load last used folder information but don't automatically load images"""
        try:
            # Get settings path
            settings_path = os.path.join(os.path.expanduser("~"), ".tennis_tracker", "settings.json")
            self.logger.debug(f"Loading settings from: {settings_path}")
            
            if not os.path.exists(settings_path):
                self.logger.warning("Settings file does not exist")
                return
            
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                
                # If we have a JSON file path, use that instead of folder path
                if 'last_file_path' in settings and os.path.exists(settings['last_file_path']):
                    json_path = settings['last_file_path']
                    self.logger.info(f"Found last used JSON file: {json_path}")
                    # Store but don't load - will be loaded when needed
                    self._last_file_path = json_path
                    return
                
                # Store folder path but don't load images yet
                if 'last_folder_path' in settings:
                    self._last_used_folder = settings['last_folder_path']
                    self.logger.debug(f"Found last used folder: {self._last_used_folder}")
                else:
                    self.logger.warning("No last used folder found in settings")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid settings file format: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error loading last used folder: {str(e)}")
            self.logger.error(f"Error details: {type(e).__name__}")

    def _save_last_used_folder(self, folder_path):
        """마지막으로 사용한 이미지 폴더를 저장합니다."""
        try:
            settings_dir = os.path.join(os.path.expanduser("~"), ".tennis_tracker")
            os.makedirs(settings_dir, exist_ok=True)
            
            settings_path = os.path.join(settings_dir, "settings.json")
            self.logger.debug(f"Saving settings to: {settings_path}")
            
            settings = {}
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, 'r') as f:
                        settings = json.load(f)
                except json.JSONDecodeError:
                    self.logger.warning("설정 파일이 손상되었습니다. 새로 생성합니다.")
            
            settings['last_folder_path'] = folder_path
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
            
            self.logger.debug(f"Successfully saved last used folder: {folder_path}")
            
        except Exception as e:
            self.logger.error(f"마지막 사용 폴더 저장 중 오류 발생: {str(e)}")
            self.logger.error(f"오류 상세 정보: {type(e).__name__}") 