"""
Tests for the SimulationController class.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QTimer

from src.controllers.simulation_controller import SimulationController
from src.models.app_state import AppState
from src.utils.logger import Logger

class TestSimulationController:
    """Test cases for the SimulationController class."""
    
    @pytest.fixture
    def mock_singletons(self):
        """Mock singleton instances."""
        with patch.object(AppState, 'instance', return_value=MagicMock(spec=AppState)) as mock_app_state, \
             patch.object(Logger, 'instance', return_value=MagicMock(spec=Logger)) as mock_logger:
            yield {
                'app_state': mock_app_state,
                'logger': mock_logger
            }
    
    @pytest.fixture
    def mock_qtimer(self):
        """Mock QTimer for simulation."""
        with patch('src.controllers.simulation_controller.QTimer') as mock_timer_class:
            mock_timer = MagicMock(spec=QTimer)
            mock_timer_class.return_value = mock_timer
            yield mock_timer
    
    @pytest.fixture
    def controller(self, qapp, mock_singletons, mock_qtimer):
        """Create a SimulationController instance for testing."""
        controller = SimulationController()
        controller.app_state = mock_singletons['app_state'].return_value
        controller.logger = mock_singletons['logger'].return_value
        controller._simulation_timer = mock_qtimer
        
        # Configure mocks
        controller.app_state.playback_state = 'stop'
        
        yield controller
    
    def test_init(self, controller, mock_qtimer):
        """Test initialization of SimulationController."""
        # Verify QTimer was set up correctly
        assert controller._simulation_timer is mock_qtimer
        assert controller._simulation_timer.setInterval.call_args[0][0] == 500
        assert controller._simulation_timer.timeout.connect.called
        
        # Verify initial state
        assert controller._simulation_running == False
        
        # Verify app state connection
        assert controller.app_state.playback_state_changed.connect.called
    
    def test_handle_playback_state_changed_play(self, controller):
        """Test handling playback state change to 'play'."""
        # Mock start_simulation
        with patch.object(controller, 'start_simulation') as mock_start:
            
            # Call method with 'play'
            controller._handle_playback_state_changed('play')
            
            # Verify start_simulation was called
            mock_start.assert_called_once()
    
    def test_handle_playback_state_changed_pause(self, controller, mock_qtimer):
        """Test handling playback state change to 'pause'."""
        # Call method with 'pause'
        controller._handle_playback_state_changed('pause')
        
        # Verify timer was stopped
        mock_qtimer.stop.assert_called_once()
    
    def test_handle_playback_state_changed_stop(self, controller):
        """Test handling playback state change to 'stop'."""
        # Mock stop_simulation
        with patch.object(controller, 'stop_simulation') as mock_stop:
            
            # Call method with 'stop'
            controller._handle_playback_state_changed('stop')
            
            # Verify stop_simulation was called
            mock_stop.assert_called_once()
    
    def test_start_simulation(self, controller, mock_qtimer):
        """Test starting simulation."""
        # Setup signal spy
        signal_received = False
        state_received = None
        
        def on_simulation_state_changed(state):
            nonlocal signal_received, state_received
            signal_received = True
            state_received = state
        
        controller.simulation_state_changed.connect(on_simulation_state_changed)
        
        # Prepare ImageManager mock
        with patch('src.controllers.image_manager.ImageManager') as mock_image_manager_class:
            mock_image_manager = MagicMock()
            mock_image_manager.get_total_images.return_value = 0
            mock_image_manager_class.instance.return_value = mock_image_manager
            
            # Call method when not already running
            controller._simulation_running = False
            controller.start_simulation()
            
            # Verify timer was started
            mock_qtimer.start.assert_called_once()
            
            # Verify state was updated
            assert controller._simulation_running == True
            assert controller.app_state.total_frames == 100
            assert controller.app_state.playback_state == 'play'
            
            # Verify signal was emitted
            assert signal_received
            assert state_received is True
            
            # Reset mocks
            mock_qtimer.start.reset_mock()
            signal_received = False
            
            # Call method when already running
            controller._simulation_running = True
            controller.start_simulation()
            
            # Verify timer was not started again
            mock_qtimer.start.assert_not_called()
            
            # Verify signal was not emitted again
            assert not signal_received
    
    def test_stop_simulation(self, controller, mock_qtimer):
        """Test stopping simulation."""
        # Setup signal spy
        signal_received = False
        state_received = None
        
        def on_simulation_state_changed(state):
            nonlocal signal_received, state_received
            signal_received = True
            state_received = state
        
        controller.simulation_state_changed.connect(on_simulation_state_changed)
        
        # Call method when running
        controller._simulation_running = True
        controller.stop_simulation()
        
        # Verify timer was stopped
        mock_qtimer.stop.assert_called_once()
        
        # Verify state was updated
        assert controller._simulation_running == False
        assert controller.app_state.playback_state == 'stop'
        
        # Verify signal was emitted
        assert signal_received
        assert state_received is False
        
        # Reset mocks
        mock_qtimer.stop.reset_mock()
        signal_received = False
        
        # Call method when not running
        controller._simulation_running = False
        controller.stop_simulation()
        
        # Verify timer was not stopped again
        mock_qtimer.stop.assert_not_called()
        
        # Verify signal was not emitted again
        assert not signal_received
    
    def test_toggle_simulation(self, controller):
        """Test toggling simulation state."""
        # Mock methods
        with patch.object(controller, 'start_simulation') as mock_start, \
             patch.object(controller, 'stop_simulation') as mock_stop:
            
            # Toggle when not running
            controller._simulation_running = False
            controller.toggle_simulation()
            
            # Verify start was called
            mock_start.assert_called_once()
            mock_stop.assert_not_called()
            
            # Reset mocks
            mock_start.reset_mock()
            
            # Toggle when running
            controller._simulation_running = True
            controller.toggle_simulation()
            
            # Verify stop was called
            mock_stop.assert_called_once()
            mock_start.assert_not_called()
    
    def test_is_running(self, controller):
        """Test is_running method."""
        # Test when running
        controller._simulation_running = True
        assert controller.is_running() is True
        
        # Test when not running
        controller._simulation_running = False
        assert controller.is_running() is False
    
    def test_simulate_ball_movement(self, controller):
        """Test the simulation of ball movement."""
        # Mock random.random to return predictable values
        with patch('src.controllers.simulation_controller.random.random', return_value=0.5), \
             patch('src.controllers.simulation_controller.random.uniform', return_value=5.0):
             
            # Configure mock app_state to avoid comparison between MagicMock objects
            controller.app_state.current_frame = 5
            controller.app_state.total_frames = 10
            
            # Call the private method
            controller._simulate_ball_movement()
            
            # Verify app state was updated with the new ball position (which is (5.0, 5.0, 5.0) due to our mocking)
            assert controller.app_state.ball_position == (5.0, 5.0, 5.0)
            
            # Verify current frame was incremented
            assert controller.app_state.current_frame == 6 