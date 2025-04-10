"""
LED Display Widget Module

This module defines a widget for displaying the in/out status with LED indicators.
It implements the blinking functionality for out-of-bounds indication.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer, Slot, Property
from PySide6.QtGui import QColor, QPalette

from src.models.app_state import AppState
from src.utils.config import Config

class LedIndicator(QFrame):
    """
    LED indicator widget that can be turned on/off and can blink.
    
    This widget simulates an LED light that can be:
    - On (solid color)
    - Off (gray color)
    - Blinking (alternating between on and off at a specified rate)
    """
    
    def __init__(self, color=QColor(0, 255, 0), parent=None):
        super(LedIndicator, self).__init__(parent)
        
        # Set up the widget
        self.setMinimumSize(30, 30)
        self.setMaximumSize(30, 30)
        self.setFrameShape(QFrame.Box)
        
        # Initialize state
        self._on = False
        self._color = color
        self._default_color = QColor(100, 100, 100)  # Off state color
        self._blink_rate = 0  # Hz (0 = no blinking)
        
        # Timer for blinking
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._toggle_led)
        
        # Initial state: off
        self.set_state(False)
    
    def _toggle_led(self):
        """Toggle the LED on/off for blinking effect"""
        self._on = not self._on
        self._update_color()
    
    def _update_color(self):
        """Update the LED color based on current state"""
        palette = self.palette()
        color = self._color if self._on else self._default_color
        palette.setColor(QPalette.Window, color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
    
    def set_state(self, on, blink_rate=0):
        """
        Set the LED state
        
        Args:
            on: True for on, False for off
            blink_rate: Blink rate in Hz (0 for no blinking)
        """
        self._on = on
        self._blink_rate = blink_rate
        
        # Stop existing timer if running
        if self._timer.isActive():
            self._timer.stop()
        
        # Set up blinking if needed
        if blink_rate > 0:
            interval = int(1000 / (2 * blink_rate))  # Convert Hz to ms
            self._timer.start(interval)
        else:
            # No blinking, just update color
            self._update_color()
    
    @Property(QColor)
    def color(self):
        """Get the LED color"""
        return self._color
    
    @color.setter
    def color(self, color):
        """Set the LED color"""
        self._color = color
        self._update_color()


class LedDisplay(QWidget):
    """
    LED display widget for showing tennis ball in/out status.
    
    This widget provides:
    - Visual indicators for various ball states
    - Multiple LED colors for different statuses
    - Support for multiple ball states:
      - Not Detected
      - In Bounds
      - Out of Bounds
      - Bounce Detected
      - In Service
      - Fault
    """
    
    # Status definitions
    STATUS_NOT_DETECTED = 0
    STATUS_IN_BOUNDS = 1
    STATUS_OUT_OF_BOUNDS = 2
    STATUS_BOUNCE = 3
    STATUS_IN_SERVICE = 4
    STATUS_FAULT = 5
    
    def __init__(self, parent=None):
        super(LedDisplay, self).__init__(parent)
        
        # Get singleton instances
        self.app_state = AppState.instance()
        self.config = Config.instance()
        
        # Current status
        self._current_status = self.STATUS_NOT_DETECTED
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        self.layout = QHBoxLayout(self)
        
        # Create status LED displays
        self.status_leds = {}
        
        # Ball Detection LED (blue)
        self.status_leds["detection"] = self._create_led_group("Detection", QColor(0, 120, 255))
        
        # In bounds LED (green)
        self.status_leds["in_bounds"] = self._create_led_group("In", QColor(0, 200, 0))
        
        # Out of bounds LED (red)
        self.status_leds["out_bounds"] = self._create_led_group("Out", QColor(255, 0, 0))
        
        # Bounce LED (yellow)
        self.status_leds["bounce"] = self._create_led_group("Bounce", QColor(255, 200, 0))
        
        # Add stretch for spacing
        self.layout.addStretch()
        
        # Set initial state (not detected)
        self.update_status(self.STATUS_NOT_DETECTED)
    
    def _create_led_group(self, label_text, color):
        """Create a LED display with label as a group"""
        # Label
        label = QLabel(label_text + ":")
        label.setStyleSheet("color: white;")
        
        # LED display
        led = LedIndicator(color)
        
        # Add to layout
        self.layout.addWidget(label)
        self.layout.addWidget(led)
        self.layout.addSpacing(15)  # Add spacing
        
        return led
    
    @Slot(bool, float)
    def update_led_state(self, in_bounds, blink_rate=0):
        """
        Legacy method for backward compatibility
        
        Args:
            in_bounds: True if the ball is in bounds, False if out
            blink_rate: Blink rate in Hz for out-of-bounds indication
        """
        # Convert from legacy In/Out state to new status model
        if in_bounds:
            self.update_status(self.STATUS_IN_BOUNDS)
        else:
            self.update_status(self.STATUS_OUT_OF_BOUNDS, blink_rate)
    
    def update_status(self, status, blink_rate=0):
        """
        Update the status for various states
        
        Args:
            status: Status code (use CLASS constants)
            blink_rate: Blink rate if needed
        """
        self._current_status = status
        
        # Reset all LEDs
        for led in self.status_leds.values():
            led.set_state(False, 0)
        
        # Set appropriate LEDs based on status
        if status == self.STATUS_NOT_DETECTED:
            # No LEDs are on
            pass
            
        elif status == self.STATUS_IN_BOUNDS:
            self.status_leds["detection"].set_state(True, 0)
            self.status_leds["in_bounds"].set_state(True, 0)
            
        elif status == self.STATUS_OUT_OF_BOUNDS:
            self.status_leds["detection"].set_state(True, 0)
            self.status_leds["out_bounds"].set_state(True, blink_rate)
            
        elif status == self.STATUS_BOUNCE:
            self.status_leds["detection"].set_state(True, 0)
            self.status_leds["bounce"].set_state(True, blink_rate)
            
        elif status == self.STATUS_IN_SERVICE:
            self.status_leds["detection"].set_state(True, 0)
            self.status_leds["in_bounds"].set_state(True, 0)
            self.status_leds["bounce"].set_state(True, 0)
            
        elif status == self.STATUS_FAULT:
            self.status_leds["detection"].set_state(True, 0)
            self.status_leds["out_bounds"].set_state(True, blink_rate)
            self.status_leds["bounce"].set_state(True, 0)
    
    def get_current_status(self):
        """Return current status code"""
        return self._current_status
    
    def get_status_text(self):
        """Return text corresponding to the current status"""
        status_texts = {
            self.STATUS_NOT_DETECTED: "Ball Not Detected",
            self.STATUS_IN_BOUNDS: "In Bounds",
            self.STATUS_OUT_OF_BOUNDS: "Out of Bounds",
            self.STATUS_BOUNCE: "Bounce Detected",
            self.STATUS_IN_SERVICE: "In Service",
            self.STATUS_FAULT: "Fault"
        }
        
        return status_texts.get(self._current_status, "Unknown Status") 