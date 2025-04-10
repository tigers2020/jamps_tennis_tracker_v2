"""
Simulation Controller Module

This module provides a controller for simulating tennis ball tracking.
"""

import time
import random
from PySide6.QtCore import QObject, QTimer, Signal

from src.models.app_state import AppState
from src.views.widgets.led_display import LedDisplay
from src.utils.logger import Logger

class SimulationController(QObject):
    """
    Controller for managing tennis ball movement simulation
    
    This class provides the following functionality:
    - Ball position simulation
    - Ball status simulation (in/out)
    - Simulation timer management
    """
    
    # Simulation state change signal
    simulation_state_changed = Signal(bool)  # running/stopped
    
    def __init__(self):
        super(SimulationController, self).__init__()
        
        # Get singleton instances
        self.app_state = AppState.instance()
        self.logger = Logger.instance()
        
        # Simulation timer
        self._simulation_timer = QTimer(self)
        self._simulation_timer.timeout.connect(self._simulate_ball_movement)
        self._simulation_timer.setInterval(500)  # update every 500ms
        
        # Simulation state
        self._simulation_running = False
        
        # Connect app state signals
        self.app_state.playback_state_changed.connect(self._handle_playback_state_changed)
    
    def _handle_playback_state_changed(self, state):
        """
        Handle playback state change
        
        Args:
            state: New playback state ('play', 'pause', 'stop')
        """
        # Simulation mode (no images loaded)
        if state == 'play':
            self.start_simulation()
        elif state == 'pause':
            self._simulation_timer.stop()
        elif state == 'stop':
            self.stop_simulation()
    
    def _simulate_ball_movement(self):
        """Simulate ball movement for testing"""
        # Generate random ball position
        x = random.uniform(-10.0, 10.0)
        y = random.uniform(0.0, 10.0)
        z = random.uniform(-10.0, 10.0)
        
        # Update app state
        self.app_state.ball_position = (x, y, z)
        
        # Increment current frame
        current_frame = self.app_state.current_frame
        if current_frame < self.app_state.total_frames:
            self.app_state.current_frame = current_frame + 1
        else:
            self.app_state.current_frame = 0
        
        # Occasionally change status randomly (10% chance)
        if random.random() < 0.1:
            self._update_random_ball_status()
    
    def _update_random_ball_status(self):
        """Change status randomly for testing"""
        # Choose a random status between 0-5
        status = random.randint(0, 5)
        blink_rate = 10.0 if status in [LedDisplay.STATUS_OUT_OF_BOUNDS, LedDisplay.STATUS_FAULT] else 0.0
        
        # Update for compatibility with app_state.led_state
        in_bounds = status in [LedDisplay.STATUS_IN_BOUNDS, LedDisplay.STATUS_IN_SERVICE]
        self.app_state.led_state = (in_bounds, blink_rate)
    
    def start_simulation(self):
        """Start simulation"""
        if not self._simulation_running:
            self.logger.debug("Starting simulation")
            self._simulation_timer.start()
            self._simulation_running = True
            
            # Only set total_frames if not in image mode
            from src.controllers.image_manager import ImageManager
            image_manager = ImageManager.instance()
            if image_manager.get_total_images() == 0:
                # Set initial values (only if no images)
                self.app_state.total_frames = 100
                self.logger.debug("Simulation mode: setting total_frames to 100")
            
            # Emit simulation state change signal
            self.simulation_state_changed.emit(True)
            
            # Update app state
            self.app_state.playback_state = 'play'
    
    def stop_simulation(self):
        """Stop simulation"""
        if self._simulation_running:
            self.logger.debug("Stopping simulation")
            self._simulation_timer.stop()
            self._simulation_running = False
            
            # Emit simulation state change signal
            self.simulation_state_changed.emit(False)
            
            # Update app state
            self.app_state.playback_state = 'stop'
    
    def toggle_simulation(self):
        """Toggle simulation state"""
        if self._simulation_running:
            self.stop_simulation()
        else:
            self.start_simulation()
    
    def is_running(self):
        """
        Check if simulation is running
        
        Returns:
            bool: True if running, False if not
        """
        return self._simulation_running 