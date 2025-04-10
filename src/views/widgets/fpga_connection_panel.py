"""
FPGA Connection Panel Module

This module provides a panel for FPGA connection settings and controls.
"""

from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QGridLayout, QGroupBox
)
from PySide6.QtGui import QPixmap

from src.controllers.fpga_connection_manager import FpgaConnectionManager, FpgaSettingsDialog
from src.utils.logger import Logger
from src.utils.ui_theme import (
    get_button_style, get_combobox_style, get_label_style, get_group_box_style
)
from src.constants.ui_constants import (
    CONNECTION_STATUS_RED_STYLE,
    CONNECTION_STATUS_GREEN_STYLE
)


class FpgaConnectionPanel(QWidget):
    """
    A panel for FPGA connection settings and controls.
    
    This panel provides UI elements for:
    - COM port selection
    - Connect/disconnect button
    - FPGA settings button
    - Connection status display
    """
    
    # Signals
    connection_toggled = Signal(bool)  # Connected/disconnected
    
    def __init__(self, parent=None):
        """
        Initialize the FPGA connection panel.
        
        Args:
            parent: Parent widget
        """
        super(FpgaConnectionPanel, self).__init__(parent)
        
        # Get logger instance
        self.logger = Logger.instance()
        
        # Initialize FPGA connection manager
        self.fpga_manager = FpgaConnectionManager()
        
        # Set up the UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Initial port refresh
        self._refresh_port_list()
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)
        
        # Create group box
        self.group_box = QGroupBox("FPGA Connection")
        self.group_box.setStyleSheet(get_group_box_style())
        
        # Connection grid layout - using horizontal layout to reduce height
        connection_layout = QHBoxLayout()
        connection_layout.setContentsMargins(5, 5, 5, 5)
        connection_layout.setSpacing(5)
        
        # Left side - port selection
        port_layout = QHBoxLayout()
        port_layout.setSpacing(3)
        
        # COM port dropdown with label
        port_label = QLabel("Port:")
        port_label.setStyleSheet(get_label_style())
        port_layout.addWidget(port_label)
        
        self.com_port_combo = QComboBox()
        self.com_port_combo.setStyleSheet(get_combobox_style())
        self.com_port_combo.setMaximumWidth(100)  # Limit width
        port_layout.addWidget(self.com_port_combo)
        
        # Refresh button
        self.refresh_button = QPushButton("↻")  # Using symbol to save space
        self.refresh_button.setStyleSheet(get_button_style())
        self.refresh_button.setMaximumWidth(30)  # Make button compact
        self.refresh_button.setToolTip("Refresh Ports")
        self.refresh_button.clicked.connect(self._refresh_port_list)
        port_layout.addWidget(self.refresh_button)
        
        # Add port layout to main connection layout
        connection_layout.addLayout(port_layout)
        
        # Center - connection status
        self.connection_status_label = QLabel("Disconnected")
        self.connection_status_label.setAlignment(Qt.AlignCenter)
        self.connection_status_label.setStyleSheet("color: red; font-weight: bold;")
        connection_layout.addWidget(self.connection_status_label, 1)  # Give stretch to center
        
        # Right side - action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(3)
        
        # Connect/Disconnect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.setStyleSheet(get_button_style())
        self.connect_button.clicked.connect(self._toggle_connection)
        button_layout.addWidget(self.connect_button)
        
        # Settings button
        self.settings_button = QPushButton("⚙")  # Using symbol to save space
        self.settings_button.setStyleSheet(get_button_style())
        self.settings_button.setMaximumWidth(30)  # Make button compact
        self.settings_button.setToolTip("FPGA Settings")
        self.settings_button.clicked.connect(self._show_settings_dialog)
        button_layout.addWidget(self.settings_button)
        
        # Add button layout to main connection layout
        connection_layout.addLayout(button_layout)
        
        # Add layout to group box
        group_layout = QVBoxLayout(self.group_box)
        group_layout.setContentsMargins(5, 15, 5, 5)  # Reduced top margin to accommodate title
        group_layout.addLayout(connection_layout)
        
        # Add group box to main layout
        main_layout.addWidget(self.group_box)
    
    def _connect_signals(self):
        """Connect signals to slots"""
        # FPGA connection manager signals
        self.fpga_manager.connection_state_changed.connect(self._update_connection_ui)
    
    def _refresh_port_list(self):
        """Refresh the list of available COM ports"""
        ports = self.fpga_manager.get_available_ports()
        self.com_port_combo.clear()
        
        for port in ports:
            # Convert ListPortInfo object to string (port name)
            port_name = port.device
            self.com_port_combo.addItem(port_name)
        
        self.logger.debug(f"Found {len(ports)} COM ports")
    
    def _show_settings_dialog(self):
        """Show the FPGA connection settings dialog"""
        dialog = FpgaSettingsDialog(self)
        if dialog.exec():
            settings = dialog.get_settings()
            self.fpga_manager.update_settings(settings)
    
    def _toggle_connection(self):
        """Toggle the FPGA connection state"""
        port_name = self.com_port_combo.currentText()
        if not port_name:
            self.logger.warning("No COM port selected")
            return
            
        self.fpga_manager.toggle_connection(port_name)
    
    @Slot(bool)
    def _update_connection_ui(self, connected):
        """
        Update connection UI based on connection state.
        
        Args:
            connected: Whether the FPGA is connected
        """
        if connected:
            self.connect_button.setText("Disconnect")
            self.connection_status_label.setText("Connected")
            self.connection_status_label.setStyleSheet(CONNECTION_STATUS_GREEN_STYLE)
            self.com_port_combo.setEnabled(False)
            self.settings_button.setEnabled(False)
            self.refresh_button.setEnabled(False)
        else:
            self.connect_button.setText("Connect")
            self.connection_status_label.setText("Not Connected")
            self.connection_status_label.setStyleSheet(CONNECTION_STATUS_RED_STYLE)
            self.com_port_combo.setEnabled(True)
            self.settings_button.setEnabled(True)
            self.refresh_button.setEnabled(True)
        
        # Emit signal for other components
        self.connection_toggled.emit(connected)
    
    def update_fpga_settings(self, settings):
        """
        Update FPGA connection settings.
        
        Args:
            settings: Dictionary containing FPGA settings
        """
        # COM port selection update
        if 'com_port' in settings and settings['com_port']:
            index = self.com_port_combo.findText(settings['com_port'])
            if index >= 0:
                self.com_port_combo.setCurrentIndex(index)
        
        # Auto-connect setting check
        if ('auto_connect' in settings and 
            settings['auto_connect'] and 
            not self.fpga_manager.get_connection_state()):
            # Just log that we would connect automatically on startup
            self.logger.info("Auto-connect setting changed, will connect on next startup")
    
    def get_fpga_manager(self):
        """Get the FPGA connection manager instance."""
        return self.fpga_manager 