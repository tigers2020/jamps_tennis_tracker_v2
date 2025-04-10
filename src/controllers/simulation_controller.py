"""
Simulation Controller Module

This module provides a controller for simulating tennis ball tracking.
"""

import random
import time
from PySide6.QtCore import QObject, QTimer, Slot

from src.models.app_state import AppState
from src.utils.logger import Logger
from src.controllers.image_manager import ImageManager
from src.views.widgets.led_display import LedDisplay
from src.constants.ui_constants import (
    SIMULATION_UPDATE_INTERVAL,
    SIMULATION_BALL_X_MIN, SIMULATION_BALL_X_MAX,
    SIMULATION_BALL_Y_MIN, SIMULATION_BALL_Y_MAX,
    SIMULATION_BALL_Z_MIN, SIMULATION_BALL_Z_MAX,
    SIMULATION_STATUS_CHANGE_PROBABILITY,
    SIMULATION_DEFAULT_TOTAL_FRAMES,
    SIMULATION_BLINK_RATE
)


class SimulationController(QObject):
    """
    Controller for simulating ball tracking and FPGA behavior.
    
    This class creates random ball positions and LED status updates
    to demonstrate the system's functionality without real data.
    """
    
    def __init__(self):
        """Initialize the simulation controller"""
        super(SimulationController, self).__init__()
        
        # Get singleton instances
        self.app_state = AppState.instance()
        self.logger = Logger.instance()
        
        # Set up simulation timer
        self._simulation_timer = QTimer(self)
        self._simulation_timer.setInterval(SIMULATION_UPDATE_INTERVAL)  # update every 500ms
        self._simulation_timer.timeout.connect(self._update_simulation)
        
        # LED display reference (will be set externally)
        self._led_display = None
    
    def set_led_display(self, led_display):
        """
        Set the LED display to control during simulation
        
        Args:
            led_display: LedDisplay widget to control
        """
        self._led_display = led_display
    
    def start_simulation(self):
        """Start the simulation"""
        # Initialize simulation state
        self._init_simulation()
        
        # Start timer
        self._simulation_timer.start()
        self.logger.debug("Ball position simulation started")
    
    def _update_simulation(self):
        """Update the simulation state (called by timer)"""
        try:
            # Generate a random position within reasonable range
            x = random.uniform(SIMULATION_BALL_X_MIN, SIMULATION_BALL_X_MAX)
            y = random.uniform(SIMULATION_BALL_Y_MIN, SIMULATION_BALL_Y_MAX)
            z = random.uniform(SIMULATION_BALL_Z_MIN, SIMULATION_BALL_Z_MAX)
            
            # Update app state with new position
            self.app_state.set_ball_position(x, y, z)
            
            # Update current frame to simulate playback
            current_frame = self.app_state.current_frame
            if current_frame < self.app_state.total_frames - 1:
                self.app_state.current_frame = current_frame + 1
            else:
                self.app_state.current_frame = 0
            
            # Occasionally change status randomly (10% chance)
            if random.random() < SIMULATION_STATUS_CHANGE_PROBABILITY:
                if self._led_display:
                    # Update LED display
                    
                    # Choose a random status between 0-5
                    status = random.randint(0, 5)
                    blink_rate = SIMULATION_BLINK_RATE if status in [LedDisplay.STATUS_OUT_OF_BOUNDS, LedDisplay.STATUS_FAULT] else 0.0
                    
                    # Set the new status
                    self._led_display.set_status(status, blink_rate)
                    
                    self.logger.debug(f"Simulation: changed LED status to {status}")
                    
        except Exception as e:
            self.logger.error(f"Simulation update error: {e}")
    
    def _init_simulation(self):
        """Initialize simulation state and data"""
        # Set initial position
        self.app_state.set_ball_position(0, 0, 0)
        
        # Get image manager instance
        image_manager = ImageManager.instance()
        
        # If no images are loaded, we simulate frames as well
        if image_manager.get_total_images() == 0:
            # Set a default number of frames for the simulation
            self.app_state.total_frames = SIMULATION_DEFAULT_TOTAL_FRAMES
            self.logger.debug(f"Simulation mode: setting total_frames to {SIMULATION_DEFAULT_TOTAL_FRAMES}")
    
    def stop_simulation(self):
        """Stop the simulation"""
        self._simulation_timer.stop()
        
        # Reset LED display if we have one
        if self._led_display:
            self._led_display.set_status(LedDisplay.STATUS_NOT_DETECTED)
        
        self.logger.debug("Ball position simulation stopped")
    
    @property
    def is_running(self):
        """Check if simulation is currently running"""
        return self._simulation_timer.isActive() 