"""
Settings Tab Module

This module defines the settings tab, which provides an interface
for configuring the Tennis Ball Tracker application.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, 
                              QGroupBox, QLabel, QPushButton, QSlider, 
                              QSpinBox, QComboBox, QCheckBox, QFileDialog, QMessageBox,
                              QFrame)
from PySide6.QtCore import Qt, Slot, Signal

from src.utils.settings_manager import SettingsManager
from src.utils.logger import Logger
from src.models.app_state import AppState
from src.utils.ui_theme import (
    get_group_box_style, get_label_style, get_button_style, 
    get_checkbox_style, get_slider_style, get_spinbox_style,
    get_form_input_label_style, get_message_box_style, get_separator_style
)
from src.constants.ui_constants import WINDOW_SIZE_PRESETS

class SettingsTab(QWidget):
    """
    Settings tab for configuring the Tennis Ball Tracker application.
    
    This tab provides configuration for:
    - Playback settings (speed, auto-play)
    - Data storage settings
    """
    
    # Signal when settings are changed
    settings_changed = Signal()
    
    def __init__(self, parent=None):
        super(SettingsTab, self).__init__(parent)
        
        # Get singleton instances
        self.logger = Logger.instance()
        self.settings_manager = SettingsManager.instance()
        self.app_state = AppState.instance()
        
        # Initialize UI components dictionary
        self.ui_components = {}
        
        # Set up the UI
        self.setup_ui()
        
        # Load current settings
        self.load_settings()
        
        self.logger.debug("SettingsTab initialized")
    
    def setup_ui(self):
        """Set up the user interface for the settings tab"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        
        # Title and description
        self.setup_title_section()
        
        # Playback Settings
        self.setup_playback_settings()
        
        # Data Storage Settings
        self.setup_data_storage_settings()
        
        # Add bottom buttons
        self.setup_action_buttons()
        
        # Add stretch at the end to push everything to the top
        self.layout.addStretch()
    
    def setup_title_section(self):
        """Set up the title and description section"""
        # Create a grouped section for title and description
        title_group = QGroupBox("Tennis Ball Tracker Settings")
        title_group.setObjectName("titleGroup")
        title_group.setStyleSheet(get_group_box_style(is_title_centered=True))
        
        title_layout = QVBoxLayout(title_group)
        title_layout.setContentsMargins(15, 20, 15, 15)
        
        description_text = (
            "Configure the Tennis Ball Tracker application settings. "
            "Adjust playback options and data storage locations. "
            "Click 'Apply Settings' to save your changes or 'Reset' to revert to defaults."
        )
        
        description_label = QLabel(description_text)
        description_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        description_label.setWordWrap(True)
        description_label.setStyleSheet(get_label_style(is_description=True))
        
        title_layout.addWidget(description_label)
        self.layout.addWidget(title_group)
    
    def setup_playback_settings(self):
        """Set up the playback settings group"""
        playback_group = QGroupBox("Playback Settings")
        playback_group.setStyleSheet(get_group_box_style())
        
        playback_layout = QFormLayout(playback_group)
        playback_layout.setContentsMargins(15, 20, 15, 15)
        playback_layout.setSpacing(12)
        
        # Playback Speed
        speed_layout = QHBoxLayout()
        
        speed_slider = QSlider(Qt.Horizontal)
        speed_slider.setRange(10, 300)  # 10-300 as slider range (will be scaled to 10-3000)
        speed_slider.setTickPosition(QSlider.TicksBelow)
        speed_slider.setTickInterval(30)
        speed_slider.setStyleSheet(get_slider_style())
        self.ui_components["speed_slider"] = speed_slider
        
        speed_spinbox = QSpinBox()
        speed_spinbox.setRange(10, 3000)
        speed_spinbox.setSuffix(" fps")
        speed_spinbox.setStyleSheet(get_spinbox_style())
        self.ui_components["speed_spinbox"] = speed_spinbox
        
        # Connect slider and spinbox
        speed_slider.valueChanged.connect(self._on_slider_changed)
        speed_spinbox.valueChanged.connect(self._on_spinbox_changed)
        speed_spinbox.valueChanged.connect(self.on_playback_speed_changed)
        
        speed_layout.addWidget(speed_slider)
        speed_layout.addWidget(speed_spinbox)
        
        speed_label = QLabel("Playback Speed:")
        speed_label.setStyleSheet(get_form_input_label_style())
        playback_layout.addRow(speed_label, speed_layout)
        
        # Auto-play on load
        autoplay_checkbox = QCheckBox("Auto-play when loading images")
        autoplay_checkbox.setStyleSheet(get_checkbox_style())
        autoplay_checkbox.toggled.connect(self.on_autoplay_toggled)
        self.ui_components["autoplay_checkbox"] = autoplay_checkbox
        playback_layout.addRow("", autoplay_checkbox)
        
        # Loop playback
        loop_checkbox = QCheckBox("Loop playback")
        loop_checkbox.setStyleSheet(get_checkbox_style())
        loop_checkbox.toggled.connect(self.on_loop_toggled)
        self.ui_components["loop_checkbox"] = loop_checkbox
        playback_layout.addRow("", loop_checkbox)
        
        # Add group to main layout
        self.layout.addWidget(playback_group)
    
    def setup_data_storage_settings(self):
        """Set up the data storage settings group"""
        storage_group = QGroupBox("Data Storage Settings")
        storage_group.setStyleSheet(get_group_box_style())
        
        storage_layout = QFormLayout(storage_group)
        storage_layout.setContentsMargins(15, 20, 15, 15)
        storage_layout.setSpacing(12)
        
        # Data Directory
        data_dir_layout = QHBoxLayout()
        data_dir_edit = QLabel()
        data_dir_edit.setFrameStyle(QLabel.StyledPanel | QLabel.Sunken)
        data_dir_edit.setMinimumWidth(300)
        data_dir_edit.setStyleSheet(get_label_style())
        self.ui_components["data_dir_edit"] = data_dir_edit
        
        browse_button = QPushButton("Browse...")
        browse_button.setStyleSheet(get_button_style())
        browse_button.clicked.connect(self.on_browse_data_dir)
        self.ui_components["browse_button"] = browse_button
        
        data_dir_layout.addWidget(data_dir_edit)
        data_dir_layout.addWidget(browse_button)
        
        dir_label = QLabel("Default Data Directory:")
        dir_label.setStyleSheet(get_form_input_label_style())
        storage_layout.addRow(dir_label, data_dir_layout)
        
        # Auto-save Results
        autosave_checkbox = QCheckBox("Auto-save analysis results")
        autosave_checkbox.setStyleSheet(get_checkbox_style())
        autosave_checkbox.toggled.connect(self.on_autosave_toggled)
        self.ui_components["autosave_checkbox"] = autosave_checkbox
        storage_layout.addRow("", autosave_checkbox)
        
        # Add group to main layout
        self.layout.addWidget(storage_group)
    
    def setup_action_buttons(self):
        """Set up action buttons at the bottom of the settings tab"""
        button_layout = QHBoxLayout()
        
        # Reset button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.on_reset_settings)
        reset_button.setStyleSheet(get_button_style())
        self.ui_components["reset_button"] = reset_button
        
        # Apply button
        apply_button = QPushButton("Apply Settings")
        apply_button.clicked.connect(self.on_apply_settings)
        apply_button.setEnabled(False)
        apply_button.setStyleSheet(get_button_style(is_primary=True))
        self.ui_components["apply_button"] = apply_button
        
        button_layout.addStretch()
        button_layout.addWidget(reset_button)
        button_layout.addWidget(apply_button)
        
        self.layout.addLayout(button_layout)
    
    def load_settings(self):
        """Load current settings from SettingsManager"""
        self.logger.debug("Loading settings in SettingsTab")
        
        # Block signals to prevent UI updates while loading settings
        self._block_signals(True)
        
        try:
            self._load_playback_settings()
            self._load_storage_settings()
        except Exception as e:
            self.logger.error(f"Error loading settings: {str(e)}")
        
        # Unblock signals after loading settings
        self._block_signals(False)
    
    def _load_playback_settings(self):
        """Load playback settings"""
        # Playback speed
        playback_speed = self.settings_manager.get("playback_speed", 30)
        autoplay = self.settings_manager.get("autoplay", True)
        loop = self.settings_manager.get("loop_playback", True)
        
        self.ui_components["speed_slider"].setValue(int(playback_speed / 10))
        self.ui_components["speed_spinbox"].setValue(playback_speed)
        self.ui_components["autoplay_checkbox"].setChecked(autoplay)
        self.ui_components["loop_checkbox"].setChecked(loop)
    
    def _load_storage_settings(self):
        """Load storage settings"""
        # Data directory
        data_dir = self.settings_manager.get("data_directory", "")
        self.ui_components["data_dir_edit"].setText(data_dir)
        
        # Auto-save
        autosave = self.settings_manager.get("auto_save_results", True)
        self.ui_components["autosave_checkbox"].setChecked(autosave)
    
    def _block_signals(self, block):
        """Block or unblock signals from UI components"""
        components = [
            "speed_slider", "speed_spinbox", 
            "autoplay_checkbox", "loop_checkbox",
            "data_dir_edit", "autosave_checkbox",
            "apply_button", "reset_button"
        ]
        
        for component_name in components:
            if component_name in self.ui_components:
                self.ui_components[component_name].blockSignals(block)
    
    def _on_slider_changed(self, value):
        """Handle changes in the speed slider"""
        # Scale the value to the actual FPS (10-3000)
        actual_value = value * 10
        
        # Update the spinbox but avoid recursion
        self.ui_components["speed_spinbox"].blockSignals(True)
        self.ui_components["speed_spinbox"].setValue(actual_value)
        self.ui_components["speed_spinbox"].blockSignals(False)
        
        self._enable_apply_button()
    
    def _on_spinbox_changed(self, value):
        """Handle changes in the speed spinbox"""
        # Scale down to slider range (10-300)
        slider_value = value // 10
        
        # Update the slider but avoid recursion
        self.ui_components["speed_slider"].blockSignals(True)
        self.ui_components["speed_slider"].setValue(slider_value)
        self.ui_components["speed_slider"].blockSignals(False)
        
        self._enable_apply_button()
    
    def _enable_apply_button(self):
        """Enable the Apply button when settings are changed"""
        self.ui_components["apply_button"].setEnabled(True)
    
    def on_playback_speed_changed(self, value):
        """Handle playback speed changes"""
        self._enable_apply_button()
    
    def on_autoplay_toggled(self, checked):
        """Handle autoplay checkbox toggle"""
        self._enable_apply_button()
    
    def on_loop_toggled(self, checked):
        """Handle loop checkbox toggle"""
        self._enable_apply_button()
    
    def on_browse_data_dir(self):
        """Handle browse data directory button click"""
        current_dir = self.ui_components["data_dir_edit"].text()
        
        # Open directory dialog
        directory = QFileDialog.getExistingDirectory(
            self, "Select Data Directory", current_dir, QFileDialog.ShowDirsOnly
        )
        
        if directory:
            self.ui_components["data_dir_edit"].setText(directory)
            self._enable_apply_button()
    
    def on_autosave_toggled(self, checked):
        """Handle autosave checkbox toggle"""
        self._enable_apply_button()
    
    def on_reset_settings(self):
        """Reset all settings to defaults"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Reset Settings")
        msg_box.setText("Are you sure you want to reset all settings to default values?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet(get_message_box_style())
        
        if msg_box.exec() == QMessageBox.Yes:
            self.settings_manager.reset_to_defaults()
            self.load_settings()
            self.settings_changed.emit()
            self.ui_components["apply_button"].setEnabled(False)
            
            # Show success message
            success_box = QMessageBox()
            success_box.setWindowTitle("Settings Reset")
            success_box.setText("All settings have been reset to default values.")
            success_box.setStyleSheet(get_message_box_style())
            success_box.exec()
    
    def on_apply_settings(self):
        """Apply the current settings"""
        # Collect all current settings
        current_settings = self._collect_current_settings()
        
        # Save the settings
        try:
            self._save_settings(current_settings)
            
            # Emit signal to notify other components
            self.settings_changed.emit()
            
            # Disable the apply button
            self.ui_components["apply_button"].setEnabled(False)
            
            # Show success message
            success_box = QMessageBox()
            success_box.setWindowTitle("Settings Saved")
            success_box.setText("Settings have been successfully applied and saved.")
            success_box.setStyleSheet(get_message_box_style())
            success_box.exec()
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")
            error_box = QMessageBox()
            error_box.setWindowTitle("Error")
            error_box.setText(f"Error applying settings: {str(e)}")
            error_box.setIcon(QMessageBox.Critical)
            error_box.setStyleSheet(get_message_box_style())
            error_box.exec()
    
    def _collect_current_settings(self):
        """Collect all current settings from UI components"""
        settings = {}
        
        # Playback settings
        settings["playback_speed"] = self.ui_components["speed_spinbox"].value()
        settings["autoplay"] = self.ui_components["autoplay_checkbox"].isChecked()
        settings["loop_playback"] = self.ui_components["loop_checkbox"].isChecked()
        
        # Storage settings
        settings["data_directory"] = self.ui_components["data_dir_edit"].text()
        settings["auto_save_results"] = self.ui_components["autosave_checkbox"].isChecked()
        
        return settings
    
    def _save_settings(self, settings):
        """Save the settings using the SettingsManager"""
        self.logger.debug("Saving settings in SettingsTab")
        
        # Update each setting individually
        for key, value in settings.items():
            self.settings_manager.set(key, value)
            
        return True 