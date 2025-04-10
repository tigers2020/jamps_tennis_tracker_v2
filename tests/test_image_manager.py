"""
Tests for the ImageManager class.
"""

import os
import pytest
import json
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

from src.controllers.image_manager import ImageManager
from src.models.image_cache import ImageCache
from src.controllers.frame_manager import FrameManager
from src.utils.logger import Logger

class TestImageManager:
    """Test the ImageManager singleton class."""
    
    @pytest.fixture
    def reset_image_manager(self):
        """Reset the ImageManager singleton between tests."""
        # Store the original instance
        original_instance = ImageManager._instance
        ImageManager._instance = None
        yield
        # Restore the original instance
        ImageManager._instance = original_instance
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock ImageManager dependencies."""
        with patch('src.controllers.image_manager.ImageCache') as MockImageCache, \
             patch.object(FrameManager, '__init__', return_value=None) as mock_frame_manager_init, \
             patch.object(Logger, 'instance') as mock_logger_instance:
            
            # Configure mocks
            mock_logger = MagicMock()
            mock_logger_instance.return_value = mock_logger
            
            # Create mock cache
            mock_cache = MagicMock(spec=ImageCache)
            MockImageCache.return_value = mock_cache
            
            yield {
                'cache': mock_cache,
                'logger': mock_logger
            }
    
    @pytest.fixture
    def image_manager(self, reset_image_manager, mock_dependencies):
        """Create a fresh ImageManager instance for each test."""
        return ImageManager.instance()
    
    def test_singleton_instance(self, reset_image_manager, mock_dependencies):
        """Test that ImageManager follows the singleton pattern."""
        # Create first instance
        manager1 = ImageManager.instance()
        
        # Create second instance
        manager2 = ImageManager.instance()
        
        # Verify both variables reference the same instance
        assert manager1 is manager2
    
    def test_initial_state(self, image_manager):
        """Test the initial state of the ImageManager."""
        assert image_manager._image_folder == ""
        assert image_manager._image_paths == []
        assert image_manager._current_image_index == 0
        assert image_manager._current_image_path == ""
    
    def test_load_images_from_json_success(self, image_manager, mock_dependencies):
        """Test loading images from JSON when successful."""
        # Mock frame manager
        with patch.object(FrameManager, 'load_from_json', return_value=True), \
             patch.object(FrameManager, 'get_base_path', return_value="/test/path"), \
             patch.object(FrameManager, 'get_frame_paths', return_value=["path1", "path2"]), \
             patch.object(FrameManager, 'get_total_frames', return_value=2), \
             patch.object(image_manager, '_preload_images'):
            
            # Call the method
            result = image_manager.load_images_from_json("/test/frames_info.json")
            
            # Verify result
            assert result is True
            
            # Verify state was updated
            assert image_manager._image_folder == "/test/path"
            assert image_manager._image_paths == ["path1", "path2"]
            assert image_manager._current_image_path == "path1"
    
    def test_load_images_from_json_failure(self, image_manager, mock_dependencies):
        """Test loading images from JSON when frame manager fails."""
        # Mock frame manager
        with patch.object(FrameManager, 'load_from_json', return_value=False):
            
            # Call the method
            result = image_manager.load_images_from_json("/test/frames_info.json")
            
            # Verify result
            assert result is False
            
            # Verify error was logged
            mock_dependencies['logger'].error.assert_called_once()
    
    def test_get_image(self, image_manager, mock_dependencies):
        """Test getting an image."""
        # Setup test data
        image_manager._image_paths = ["path1", "path2", "path3"]
        image_manager._current_image_index = 1
        
        # Mock cache
        mock_pixmap = MagicMock()
        mock_dependencies['cache'].get_image.return_value = mock_pixmap
        
        # Mock frame manager
        with patch.object(FrameManager, 'get_frames_info', return_value=None), \
             patch.object(image_manager, '_preload_images'):
            
            # Test getting current image (no params)
            result = image_manager.get_image()
            
            # Verify result
            assert result is mock_pixmap
            
            # Verify cache was queried with correct path
            mock_dependencies['cache'].get_image.assert_called_with("path2")
            
            # Reset mock
            mock_dependencies['cache'].get_image.reset_mock()
            
            # Test getting image by index
            result = image_manager.get_image(2)  # Frame 2 = index 1 (0-based)
            
            # Verify result
            assert result is mock_pixmap
            
            # Verify cache was queried with correct path
            mock_dependencies['cache'].get_image.assert_called_with("path2")
    
    def test_get_frame_path(self, image_manager):
        """Test getting a frame path."""
        # Setup test data
        image_manager._image_paths = ["path1", "path2", "path3"]
        image_manager._current_image_index = 1
        
        # Test with frame-based mode off
        with patch.object(FrameManager, 'get_frames_info', return_value=None):
            
            # Test getting current path (no params)
            result = image_manager.get_frame_path()
            
            # Verify result
            assert result == "path2"
            
            # Test getting path by frame number (converted to index)
            result = image_manager.get_frame_path(3)  # Frame 3 = index 2 (0-based)
            
            # Verify result
            assert result == "path3"
            
            # Test invalid frame number
            result = image_manager.get_frame_path(10)
            
            # Verify result for invalid index
            assert result == ""
    
    def test_set_current_index(self, image_manager):
        """Test setting the current image index."""
        # Setup test data
        image_manager._image_paths = ["path1", "path2", "path3"]
        
        # Create signal spy
        signal_received = False
        path_received = None
        
        def on_current_image_changed(path):
            nonlocal signal_received, path_received
            signal_received = True
            path_received = path
        
        image_manager.current_image_changed.connect(on_current_image_changed)
        
        # Test valid index
        result = image_manager.set_current_index(1)
        
        # Verify result
        assert result is True
        
        # Verify state was updated
        assert image_manager._current_image_index == 1
        assert image_manager._current_image_path == "path2"
        
        # Verify signal was emitted
        assert signal_received
        assert path_received == "path2"
        
        # Test invalid index
        signal_received = False
        result = image_manager.set_current_index(10)
        
        # Verify result
        assert result is False
        
        # Verify signal was not emitted
        assert signal_received is False
    
    def test_next_image(self, image_manager):
        """Test moving to the next image."""
        # Setup test data
        image_manager._image_paths = ["path1", "path2", "path3"]
        image_manager._current_image_index = 0
        
        # Mock set_current_index
        with patch.object(image_manager, 'set_current_index') as mock_set_index:
            mock_set_index.return_value = True
            
            # Call the method
            result = image_manager.next_image()
            
            # Verify result
            assert result is True
            
            # Verify set_current_index was called with the next index
            mock_set_index.assert_called_once_with(1)
    
    def test_previous_image(self, image_manager):
        """Test moving to the previous image."""
        # Setup test data
        image_manager._image_paths = ["path1", "path2", "path3"]
        image_manager._current_image_index = 1
        
        # Mock set_current_index
        with patch.object(image_manager, 'set_current_index') as mock_set_index:
            mock_set_index.return_value = True
            
            # Call the method
            result = image_manager.previous_image()
            
            # Verify result
            assert result is True
            
            # Verify set_current_index was called with the previous index
            mock_set_index.assert_called_once_with(0)
    
    def test_get_total_images(self, image_manager):
        """Test getting the total number of images."""
        # Setup test data
        image_manager._image_paths = ["path1", "path2", "path3"]
        
        # Test with frame-based mode off
        with patch.object(FrameManager, 'get_frames_info', return_value=None):
            
            # Call the method
            result = image_manager.get_total_images()
            
            # Verify result
            assert result == 3
        
        # Test with frame-based mode on
        with patch.object(FrameManager, 'get_frames_info', return_value={}), \
             patch.object(FrameManager, 'get_total_frames', return_value=5):
             
            # Call the method
            result = image_manager.get_total_images()
            
            # Verify result
            assert result == 5
    
    def test_clear(self, image_manager, mock_dependencies):
        """Test clearing the image manager."""
        # Setup test data
        image_manager._image_paths = ["path1", "path2", "path3"]
        image_manager._current_image_index = 1
        image_manager._image_folder = "/test/folder"
        image_manager._current_image_path = "path2"
        
        # Create signal spy for images_loaded_changed
        images_signal_received = False
        
        def on_images_loaded_changed(paths):
            nonlocal images_signal_received
            images_signal_received = True
            assert paths == []
        
        image_manager.images_loaded_changed.connect(on_images_loaded_changed)
        
        # Create signal spy for frames_loaded
        frames_signal_received = False
        
        def on_frames_loaded(count):
            nonlocal frames_signal_received
            frames_signal_received = True
            assert count == 0
        
        image_manager.frames_loaded.connect(on_frames_loaded)
        
        # Call the method
        image_manager.clear()
        
        # Verify state was reset
        assert image_manager._image_paths == []
        assert image_manager._current_image_index == 0
        assert image_manager._image_folder == ""
        assert image_manager._current_image_path == ""
        
        # Verify signals were emitted
        assert images_signal_received
        assert frames_signal_received
        
        # Verify cache was cleared
        mock_dependencies['cache'].clear.assert_called_once() 