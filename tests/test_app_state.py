"""
Tests for the AppState class.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QObject

from src.models.app_state import AppState

class TestAppState:
    """Test the AppState singleton class."""
    
    @pytest.fixture
    def reset_app_state(self):
        """Reset the AppState singleton between tests."""
        # Store the original instance
        original_instance = AppState._instance
        AppState._instance = None
        yield
        # Restore the original instance
        AppState._instance = original_instance
    
    @pytest.fixture
    def app_state(self, reset_app_state):
        """Create a fresh AppState instance for each test."""
        return AppState.instance()
    
    def test_singleton_instance(self, reset_app_state):
        """Test that AppState follows the singleton pattern."""
        # Create first instance
        app_state1 = AppState.instance()
        
        # Create second instance
        app_state2 = AppState.instance()
        
        # Verify both variables reference the same instance
        assert app_state1 is app_state2
    
    def test_initial_values(self, app_state):
        """Test initial state values."""
        assert app_state.speed == 1.0
        assert app_state.camera_position == (0.0, 0.0, 10.0)
        assert app_state.ball_position == (0.0, 0.0, 0.0)
        assert app_state.playback_state == 'stop'
        assert app_state.current_frame == 0
        assert app_state.total_frames == 0
        assert app_state.led_state == (True, 0.0)
        assert app_state.file_path == ""
        assert app_state.image_paths == []
        assert app_state.current_image == ""
        assert app_state.active_tab == "home"
    
    def test_speed_property(self, app_state, qapp):
        """Test speed property and signal emission."""
        # Connect to signal
        signal_received = False
        value_received = None
        
        def on_speed_changed(value):
            nonlocal signal_received, value_received
            signal_received = True
            value_received = value
        
        app_state.speed_changed.connect(on_speed_changed)
        
        # Set a new value
        test_value = 2.5
        app_state.speed = test_value
        
        # Verify value was updated
        assert app_state.speed == test_value
        
        # Verify signal was emitted with correct value
        assert signal_received
        assert value_received == test_value
        
        # Set same value again
        signal_received = False
        app_state.speed = test_value
        
        # Verify signal was not emitted for same value
        assert not signal_received
    
    def test_camera_position_property(self, app_state, qapp):
        """Test camera position property and signal emission."""
        # Connect to signal
        signal_received = False
        values_received = None
        
        def on_camera_position_changed(azimuth, elevation, distance):
            nonlocal signal_received, values_received
            signal_received = True
            values_received = (azimuth, elevation, distance)
        
        app_state.camera_position_changed.connect(on_camera_position_changed)
        
        # Set a new value
        test_value = (45.0, 30.0, 15.0)
        app_state.camera_position = test_value
        
        # Verify value was updated
        assert app_state.camera_position == test_value
        
        # Verify signal was emitted with correct values
        assert signal_received
        assert values_received == test_value
        
        # Set same value again
        signal_received = False
        app_state.camera_position = test_value
        
        # Verify signal was not emitted for same value
        assert not signal_received
    
    def test_ball_position_property(self, app_state, qapp):
        """Test ball position property and signal emission."""
        # Connect to signal
        signal_received = False
        values_received = None
        
        def on_ball_position_changed(x, y, z):
            nonlocal signal_received, values_received
            signal_received = True
            values_received = (x, y, z)
        
        app_state.ball_position_changed.connect(on_ball_position_changed)
        
        # Set a new value
        test_value = (10.0, 20.0, 30.0)
        app_state.ball_position = test_value
        
        # Verify value was updated
        assert app_state.ball_position == test_value
        
        # Verify signal was emitted with correct values
        assert signal_received
        assert values_received == test_value
        
        # Set same value again
        signal_received = False
        app_state.ball_position = test_value
        
        # Verify signal was not emitted for same value
        assert not signal_received
    
    def test_playback_state_property(self, app_state, qapp):
        """Test playback state property and signal emission."""
        # Connect to signal
        signal_received = False
        value_received = None
        
        def on_playback_state_changed(state):
            nonlocal signal_received, value_received
            signal_received = True
            value_received = state
        
        app_state.playback_state_changed.connect(on_playback_state_changed)
        
        # Set a new value
        test_value = 'play'
        app_state.playback_state = test_value
        
        # Verify value was updated
        assert app_state.playback_state == test_value
        
        # Verify signal was emitted with correct value
        assert signal_received
        assert value_received == test_value
        
        # Set same value again
        signal_received = False
        app_state.playback_state = test_value
        
        # Verify signal was not emitted for same value
        assert not signal_received
    
    def test_current_frame_property(self, app_state, qapp):
        """Test current frame property and signal emission."""
        # Set up mock logger
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Connect to signal
            signal_received = False
            value_received = None
            
            def on_current_frame_changed(frame):
                nonlocal signal_received, value_received
                signal_received = True
                value_received = frame
            
            app_state.current_frame_changed.connect(on_current_frame_changed)
            
            # Set a new value
            test_value = 10
            app_state.current_frame = test_value
            
            # Verify value was updated
            assert app_state.current_frame == test_value
            
            # Verify signal was emitted with correct value
            assert signal_received
            assert value_received == test_value
            
            # Set same value again
            signal_received = False
            app_state.current_frame = test_value
            
            # Verify signal was not emitted for same value
            assert not signal_received
            
            # Test image path update when valid index
            app_state._image_paths = ["path1", "path2", "path3"]
            app_state.current_frame = 1  # Should select "path2"
            
            # Verify current image was updated
            assert app_state.current_image == "path2"
    
    def test_set_active_tab(self, app_state, qapp):
        """Test set_active_tab method."""
        # Connect to signal
        signal_received = False
        value_received = None
        
        def on_active_tab_changed(tab_name):
            nonlocal signal_received, value_received
            signal_received = True
            value_received = tab_name
        
        app_state.active_tab_changed.connect(on_active_tab_changed)
        
        # Call the method
        test_value = 'settings'
        app_state.set_active_tab(test_value)
        
        # Verify value was updated
        assert app_state.active_tab == test_value
        
        # Verify signal was emitted with correct value
        assert signal_received
        assert value_received == test_value 