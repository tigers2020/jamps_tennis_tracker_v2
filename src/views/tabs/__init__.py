"""
Tab Module Initialization

This module provides tab interfaces for the Tennis Ball Tracker application.
"""

from src.views.tabs.settings_tab import SettingsTab
from src.views.tabs.coming_soon_tab import ComingSoonTab
from src.views.tabs.monitoring_tab import MonitoringTab

# Import calibration tab
try:
    from src.views.tabs.calibration.calibration_tab import CalibrationTab
except ImportError:
    # If calibration tab is not available, create a placeholder
    from src.views.tabs.coming_soon_tab import ComingSoonTab as CalibrationTab
    
# Import the UI theme for consistent styling across all tabs
from src.utils.ui_theme import (
    get_application_style, get_group_box_style, get_label_style, 
    get_button_style, get_checkbox_style, get_slider_style,
    get_spinbox_style, get_message_box_style, get_tab_widget_style,
    apply_dark_theme
)

__all__ = [
    'SettingsTab',
    'CalibrationTab',
    'ComingSoonTab',
    'MonitoringTab',
    # Theme exports
    'get_application_style',
    'get_group_box_style',
    'get_label_style',
    'get_button_style',
    'get_checkbox_style',
    'get_slider_style',
    'get_spinbox_style', 
    'get_message_box_style',
    'get_tab_widget_style',
    'apply_dark_theme'
] 