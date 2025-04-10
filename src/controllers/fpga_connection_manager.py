"""
FPGA Connection Manager Module

Module that manages FPGA connections and configurations.
"""

import serial
import serial.tools.list_ports
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QDialogButtonBox
import time

from src.utils.logger import Logger
from src.models.singleton import qt_singleton

class FpgaSettingsDialog(QDialog):
    """
    Dialog for configuring FPGA serial connection settings
    
    This dialog allows setting:
    - Baud Rate
    - Data Bits
    - Parity
    - Stop Bits
    - Flow Control
    """
    
    def __init__(self, parent=None):
        super(FpgaSettingsDialog, self).__init__(parent)
        
        self.setWindowTitle("FPGA Connection Settings")
        
        # Create layouts
        layout = QVBoxLayout(self)
        
        # Create settings form layout
        form_layout = QFormLayout()
        
        # Baud Rate
        self.baud_rate_combo = QComboBox()
        self.baud_rate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        form_layout.addRow("Baud Rate:", self.baud_rate_combo)
        
        # Data Bits
        self.data_bits_combo = QComboBox()
        self.data_bits_combo.addItems(["5", "6", "7", "8"])
        form_layout.addRow("Data Bits:", self.data_bits_combo)
        
        # Parity
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["None", "Even", "Odd", "Mark", "Space"])
        form_layout.addRow("Parity:", self.parity_combo)
        
        # Stop Bits
        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.addItems(["1", "1.5", "2"])
        form_layout.addRow("Stop Bits:", self.stop_bits_combo)
        
        # Flow Control
        self.flow_control_combo = QComboBox()
        self.flow_control_combo.addItems(["None", "Hardware", "Software"])
        form_layout.addRow("Flow Control:", self.flow_control_combo)
        
        layout.addLayout(form_layout)
        
        # Add standard buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set default values
        self.baud_rate_combo.setCurrentText("115200")
        self.data_bits_combo.setCurrentText("8")
        self.parity_combo.setCurrentText("None")
        self.stop_bits_combo.setCurrentText("1")
        self.flow_control_combo.setCurrentText("None")
    
    def get_settings(self):
        """Get current settings from the dialog"""
        return {
            'baud_rate': int(self.baud_rate_combo.currentText()),
            'data_bits': int(self.data_bits_combo.currentText()),
            'parity': self.parity_combo.currentIndex(),
            'stop_bits': float(self.stop_bits_combo.currentText()),
            'flow_control': self.flow_control_combo.currentIndex()
        }

@qt_singleton
class FpgaConnectionManager(QObject):
    """
    Class that manages FPGA connections
    
    This class provides the following functionality:
    - Listing available serial ports
    - Managing FPGA connections
    - Managing connection settings
    """
    
    # Connection state change signal
    connection_state_changed = Signal(bool)  # connected/disconnected
    
    def __init__(self):
        super(FpgaConnectionManager, self).__init__()
        
        # Get logger instance
        self.logger = Logger.instance()
        
        # Connection state
        self._connected = False
        
        # Current port and settings
        self._current_port = None
        self._settings = {
            'baud_rate': 115200,
            'data_bits': 8,
            'parity': 0,  # None
            'stop_bits': 1,
            'flow_control': 0  # None
        }
        
        # Serial port object
        self._serial_port = None
    
    def get_available_ports(self):
        """Get list of available serial ports"""
        ports = list(serial.tools.list_ports.comports())
        self.logger.debug(f"Found {len(ports)} COM ports")
        return ports
    
    def is_connected(self):
        """Get current connection state"""
        return self._connected
    
    def connect_to_fpga(self, port_name=None):
        """
        Connect to FPGA
        
        Args:
            port_name: Name of port to connect to
            
        Returns:
            bool: True if successful, False if failed
        """
        if not port_name:
            self.logger.warning("No COM port selected")
            return False
            
        # In a real implementation, you would connect to the serial port here
        # For now, we'll simulate a successful connection
        
        self._current_port = port_name
        self._connected = True
        self.logger.info(f"Connected to FPGA on port {port_name}")
        self.connection_state_changed.emit(True)
        return True
    
    def disconnect_fpga(self):
        """
        Disconnect FPGA
        
        Returns:
            bool: Always returns True
        """
        self._connected = False
        self._current_port = None
        self.connection_state_changed.emit(False)
        self.logger.info("FPGA connection has been disconnected")
        return True
    
    def toggle_connection(self, port_name=None):
        """
        Toggle FPGA connection state
        
        Args:
            port_name: Name of port to connect to (only needed when connecting)
            
        Returns:
            bool: True if successful, False if failed
        """
        if self._connected:
            return self.disconnect_fpga()
        else:
            return self.connect_to_fpga(port_name)
    
    def update_settings(self, settings):
        """
        Update FPGA connection settings
        
        Args:
            settings: Settings dictionary
            
        Returns:
            bool: Always returns True
        """
        self.logger.debug(f"FPGA settings updated: {settings}")
        
        # Save settings
        self._settings.update(settings)
        return True
    
    def get_settings(self):
        """Get current settings"""
        return self._settings
    
    def get_current_port(self):
        """Get currently selected port"""
        return self._current_port
        
    def get_connection_state(self):
        """Get current connection state"""
        return self._connected 