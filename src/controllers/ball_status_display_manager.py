"""
Ball Status Display Manager Module

This module manages the LED display for showing ball status.
"""

import time
import random
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtWidgets import QLabel

from src.models.app_state import AppState
from src.views.widgets.led_display import LedDisplay
from src.utils.logger import Logger

class BallStatusDisplayManager(QObject):
    """
    Class that manages tennis ball status display
    
    This class provides the following functionality:
    - LED display updates
    - Status text display updates
    - Status style management
    """
    
    # Status display styles
    STATUS_STYLE_BASE = "font-size: 14pt; font-weight: bold; color: white; padding: 5px; border-radius: 3px;"
    STATUS_STYLE_NOT_DETECTED = f"{STATUS_STYLE_BASE} background-color: #444;"
    STATUS_STYLE_IN_BOUNDS = f"{STATUS_STYLE_BASE} background-color: #006400;"
    STATUS_STYLE_OUT_OF_BOUNDS = f"{STATUS_STYLE_BASE} background-color: #8B0000;"
    STATUS_STYLE_BOUNCE = f"{STATUS_STYLE_BASE} color: black; background-color: #FFD700;"
    STATUS_STYLE_IN_SERVICE = f"{STATUS_STYLE_BASE} background-color: #228B22;"
    STATUS_STYLE_FAULT = f"{STATUS_STYLE_BASE} background-color: #B22222;"
    
    def __init__(self, status_label=None, led_display=None):
        """
        Constructor
        
        Args:
            status_label: Ball status text label (QLabel)
            led_display: LED display widget (LedDisplay)
        """
        super(BallStatusDisplayManager, self).__init__()
        
        # Get singleton instances
        self.app_state = AppState.instance()
        self.logger = Logger.instance()
        
        # UI elements
        self._status_label = status_label
        self._led_display = led_display
        
        # Connect app state signals
        if self.app_state:
            self.app_state.led_state_changed.connect(self._update_ball_status)
    
    def set_status_label(self, label):
        """
        Set status label
        
        Args:
            label: QLabel to display status text
        """
        self._status_label = label
    
    def set_led_display(self, led_display):
        """
        Set LED display widget
        
        Args:
            led_display: LED display widget (LedDisplay)
        """
        self._led_display = led_display
    
    def _update_led_display(self):
        """Update the LED display based on current app state"""
        if not self._led_display:
            return
            
        # Get state values
        in_bounds, blink_rate = self.app_state.led_state
        
        # Update LED display
        self._led_display.set_state(in_bounds)
        self._led_display.set_blink_rate(blink_rate)
        
    @Slot(bool, float)
    def _update_ball_status(self, in_bounds, blink_rate):
        """
        Update ball status when app state changes
        
        Args:
            in_bounds: Whether the ball is in bounds
            blink_rate: Blink rate for the LED
        """
        if not self._led_display or not self._status_label:
            return
            
        status_code = LedDisplay.STATUS_IN_BOUNDS if in_bounds else LedDisplay.STATUS_OUT_OF_BOUNDS
        status_text = self._led_display.get_status_text()
        
        # Update status label
        self._status_label.setText(f"Ball Status: {status_text}")
        
        # Change color according to status
        style = self.STATUS_STYLE_IN_BOUNDS if in_bounds else self.STATUS_STYLE_OUT_OF_BOUNDS
        self._status_label.setStyleSheet(style)
    
    def update_ball_status(self, status_code, blink_rate=0):
        """
        Update ball status using a new status code
        
        Args:
            status_code: Status code from LED display
            blink_rate: Blink rate (if needed)
        """
        if not self._led_display or not self._status_label:
            return
            
        # Update LED display
        self._led_display.update_status(status_code, blink_rate)
        
        # Get status text
        status_text = self._led_display.get_status_text()
        
        # Update status label
        self._status_label.setText(f"Ball Status: {status_text}")
        
        # Apply appropriate style based on status code
        self._apply_status_style(status_code)
    
    def _apply_status_style(self, status_code):
        """Apply appropriate style based on status code"""
        if not self._status_label:
            return
            
        if status_code == LedDisplay.STATUS_NOT_DETECTED:
            self._status_label.setStyleSheet(self.STATUS_STYLE_NOT_DETECTED)
        elif status_code == LedDisplay.STATUS_IN_BOUNDS:
            self._status_label.setStyleSheet(self.STATUS_STYLE_IN_BOUNDS)
        elif status_code == LedDisplay.STATUS_OUT_OF_BOUNDS:
            self._status_label.setStyleSheet(self.STATUS_STYLE_OUT_OF_BOUNDS)
        elif status_code == LedDisplay.STATUS_BOUNCE:
            self._status_label.setStyleSheet(self.STATUS_STYLE_BOUNCE)
        elif status_code == LedDisplay.STATUS_IN_SERVICE:
            self._status_label.setStyleSheet(self.STATUS_STYLE_IN_SERVICE)
        elif status_code == LedDisplay.STATUS_FAULT:
            self._status_label.setStyleSheet(self.STATUS_STYLE_FAULT) 