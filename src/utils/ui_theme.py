"""
UI Theme Module

This module defines the UI theme constants and styles used across the application.
It provides a consistent look and feel for all components.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from typing import Dict, Any

# =============================================================================
# COLOR CONSTANTS
# =============================================================================

# Main theme colors
PRIMARY_COLOR = QColor(0, 180, 216, 255)      # Bright blue accent color (00b4d8)
PRIMARY_DARK = QColor(0, 119, 182, 255)       # Darker blue for hover/pressed states (0077b6)
SECONDARY_COLOR = QColor(144, 224, 239, 255)  # Light blue for secondary elements (90e0ef)

# Background colors
BG_DARK = QColor(18, 18, 18, 255)            # Main background (121212)
BG_MEDIUM = QColor(30, 30, 30, 255)          # Slightly lighter background for contrast (1e1e1e)
BG_LIGHT = QColor(45, 45, 45, 255)           # Light background for input elements (2d2d2d)
BG_HOVER = QColor(61, 61, 61, 255)           # Hover state background (3d3d3d)

# Border colors
BORDER_DARK = QColor(85, 85, 85, 255)        # Main border color (555555)
BORDER_LIGHT = QColor(102, 102, 102, 255)    # Lighter border for hover states (666666)
BORDER_FOCUS = QColor(0, 180, 216, 255)      # Border color for focus state (00b4d8)

# Text colors
TEXT_PRIMARY = QColor(224, 224, 224, 255)    # Main text color (e0e0e0)
TEXT_SECONDARY = QColor(187, 187, 187, 255)  # Secondary text color (bbbbbb)
TEXT_DISABLED = QColor(136, 136, 136, 255)   # Disabled text color (888888)
TEXT_BRIGHT = QColor(255, 255, 255, 255)     # Bright text for buttons (ffffff)
TEXT_DARK = QColor(17, 17, 17, 255)          # Dark text for contrast on light backgrounds (111111)

# Status colors
SUCCESS_COLOR = QColor(76, 175, 80, 255)     # Green for success (4caf50)
WARNING_COLOR = QColor(255, 152, 0, 255)     # Orange for warnings (ff9800)
ERROR_COLOR = QColor(244, 67, 54, 255)       # Red for errors (f44336)
INFO_COLOR = QColor(33, 150, 243, 255)       # Blue for info (2196f3)

# Status Background/Text Colors (already QColor)
STATUS_IMPLEMENTED_BG = QColor(60, 179, 113, 180)  # Medium Sea Green, less bright
STATUS_COMING_SOON_BG = QColor(255, 215, 0, 180)   # Gold, less bright
STATUS_TEXT_COLOR = QColor(17, 17, 17, 255)        # Dark text for better contrast

# Gradient colors
GRADIENT_START = QColor(0, 119, 182, 255)    # (0077b6)
GRADIENT_END = QColor(0, 180, 216, 255)      # (00b4d8)

# =============================================================================
# SIZING CONSTANTS
# =============================================================================

# Padding & margins
PADDING_SMALL = 4
PADDING_MEDIUM = 8
PADDING_LARGE = 12
PADDING_XLARGE = 16

MARGIN_SMALL = 4
MARGIN_MEDIUM = 8
MARGIN_LARGE = 12
MARGIN_XLARGE = 16

# Border radius
BORDER_RADIUS_SMALL = 4
BORDER_RADIUS_MEDIUM = 6
BORDER_RADIUS_LARGE = 8

# Font sizes
FONT_SIZE_SMALL = 12
FONT_SIZE_MEDIUM = 14
FONT_SIZE_LARGE = 15
FONT_SIZE_XLARGE = 18

# Button sizes
BUTTON_HEIGHT_SMALL = 24
BUTTON_HEIGHT_MEDIUM = 32
BUTTON_HEIGHT_LARGE = 40

# =============================================================================
# WIDGET STYLE FUNCTIONS
# =============================================================================

def get_application_style() -> str:
    """Return the global application style"""
    return f"""
        QWidget {{
            background-color: {BG_DARK.name()};
            color: {TEXT_PRIMARY.name()};
            font-size: {FONT_SIZE_MEDIUM}px;
        }}
        QLabel {{
            background-color: transparent;
            color: {TEXT_PRIMARY.name()};
            border: none;
        }}
    """

def get_group_box_style(is_title_centered: bool = False) -> str:
    """
    Return the style for QGroupBox widgets
    
    Args:
        is_title_centered: Whether the title should be centered
    """
    title_position = "top center" if is_title_centered else "top left"
    
    return f"""
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {BORDER_DARK.name()};
            border-radius: {BORDER_RADIUS_MEDIUM}px;
            margin-top: 12px;
            padding-top: 12px;
            background-color: rgba(25, 25, 25, 0.7);
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: {title_position};
            padding: 0 10px;
            color: {PRIMARY_COLOR.name()};
            font-size: {FONT_SIZE_LARGE}px;
        }}
    """

def get_label_style(is_description: bool = False) -> str:
    """
    Return the style for QLabel widgets
    
    Args:
        is_description: Whether this is a description label with different styling
    """
    if is_description:
        return f"""
            QLabel {{
                padding: {PADDING_LARGE}px;
                background-color: rgba(45, 45, 45, 0.1);
                border-radius: {BORDER_RADIUS_MEDIUM}px;
                color: {TEXT_PRIMARY.name()};
                font-size: {FONT_SIZE_MEDIUM}px;
                border: none;
            }}
        """
    else:
        return f"""
            QLabel {{
                color: {TEXT_PRIMARY.name()};
                background-color: transparent;
                border: none;
            }}
        """

def get_form_input_label_style() -> str:
    """Return the style for form input labels"""
    return f"""
        QLabel {{
            color: {TEXT_PRIMARY.name()};
            margin-right: {MARGIN_MEDIUM}px;
        }}
    """

def get_button_style(is_primary: bool = False, is_destructive: bool = False) -> str:
    """
    Return the style for QPushButton widgets
    
    Args:
        is_primary: Whether this is a primary action button
        is_destructive: Whether this is a destructive action button
    """
    if is_primary:
        return f"""
            QPushButton {{
                background-color: {PRIMARY_DARK.name()};
                color: {TEXT_BRIGHT.name()};
                border: 1px solid {PRIMARY_COLOR.name()};
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {PADDING_MEDIUM}px {PADDING_LARGE}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_COLOR.name()};
                border: 1px solid {PRIMARY_DARK.name()};
            }}
            QPushButton:pressed {{
                background-color: {SECONDARY_COLOR.name()};
                color: {BG_DARK.name()};
            }}
            QPushButton:disabled {{
                background-color: {BG_MEDIUM.name()};
                color: {TEXT_DISABLED.name()};
                border: 1px solid {BORDER_DARK.name()};
            }}
        """
    elif is_destructive:
        return f"""
            QPushButton {{
                background-color: rgba(244, 67, 54, 0.1);
                color: {ERROR_COLOR.name()};
                border: 1px solid {ERROR_COLOR.name()};
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {PADDING_MEDIUM}px {PADDING_LARGE}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(244, 67, 54, 0.2);
            }}
            QPushButton:pressed {{
                background-color: rgba(244, 67, 54, 0.3);
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: {BG_LIGHT.name()};
                color: {TEXT_PRIMARY.name()};
                border: 1px solid {BORDER_DARK.name()};
                border-radius: {BORDER_RADIUS_SMALL}px;
                padding: {PADDING_MEDIUM}px {PADDING_LARGE}px;
            }}
            QPushButton:hover {{
                background-color: {BG_HOVER.name()};
                border: 1px solid {BORDER_LIGHT.name()};
            }}
            QPushButton:pressed {{
                background-color: {PRIMARY_COLOR.name()};
                color: {TEXT_BRIGHT.name()};
            }}
        """

def get_checkbox_style() -> str:
    """Return the style for QCheckBox widgets"""
    return f"""
        QCheckBox {{
            color: {TEXT_PRIMARY.name()};
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {PRIMARY_COLOR.name()};
            border: 2px solid {TEXT_PRIMARY.name()};
        }}
    """

def get_slider_style() -> str:
    """Return the style for QSlider widgets"""
    return f"""
        QSlider::handle:horizontal {{
            background: {PRIMARY_COLOR.name()};
            border: 1px solid {BG_HOVER.name()};
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }}
        QSlider::groove:horizontal {{
            border: 1px solid #999999;
            height: 8px;
            background: {BG_LIGHT.name()};
            margin: 2px 0;
            border-radius: 4px;
        }}
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {GRADIENT_START.name()}, stop: 1 {GRADIENT_END.name()});
            border: 1px solid #777;
            height: 10px;
            border-radius: 4px;
        }}
    """

def get_spinbox_style() -> str:
    """Return the style for QSpinBox widgets"""
    return f"""
        QSpinBox {{
            background-color: {BG_LIGHT.name()};
            color: {TEXT_PRIMARY.name()};
            border: 1px solid {BORDER_DARK.name()};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: {PADDING_SMALL}px;
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {BG_MEDIUM.name()};
            width: 16px;
            border: 1px solid {BORDER_DARK.name()};
        }}
        QSpinBox::up-arrow {{
            image: url(../resources/images/up_arrow.png);
            width: 10px;
            height: 10px;
        }}
        QSpinBox::down-arrow {{
            image: url(../resources/images/down_arrow.png);
            width: 10px;
            height: 10px;
        }}
    """

def get_combobox_style() -> str:
    """Return the style for QComboBox widgets"""
    return f"""
        QComboBox {{
            background-color: {BG_LIGHT.name()};
            color: {TEXT_PRIMARY.name()};
            border: 1px solid {BORDER_DARK.name()};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: {PADDING_SMALL}px;
            min-width: 200px;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {BORDER_DARK.name()};
        }}
        QComboBox::down-arrow {{
            image: url(src/resources/icons/down-arrow.png);
            width: 12px;
            height: 12px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {BG_MEDIUM.name()};
            color: {TEXT_PRIMARY.name()};
            border: 1px solid {BORDER_DARK.name()};
            selection-background-color: {PRIMARY_DARK.name()};
        }}
    """

def get_line_edit_style() -> str:
    """Return the style for QLineEdit widgets"""
    return f"""
        QLineEdit {{
            background-color: {BG_LIGHT.name()};
            color: {TEXT_PRIMARY.name()};
            border: 1px solid {BORDER_DARK.name()};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: {PADDING_SMALL}px;
        }}
        QLineEdit:focus {{
            border: 1px solid {PRIMARY_COLOR.name()};
        }}
    """

def get_text_edit_style() -> str:
    """Return the style for QTextEdit widgets"""
    return f"""
        QTextEdit {{
            background-color: {BG_LIGHT.name()};
            color: {TEXT_PRIMARY.name()};
            border: 1px solid {BORDER_DARK.name()};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: {PADDING_SMALL}px;
        }}
        QTextEdit:focus {{
            border: 1px solid {PRIMARY_COLOR.name()};
        }}
    """

def get_dialog_style() -> str:
    """Return the style for QDialog widgets"""
    return f"""
        QDialog {{
            background-color: {BG_DARK.name()};
            color: {TEXT_PRIMARY.name()};
            border: 1px solid {BORDER_DARK.name()};
            border-radius: {BORDER_RADIUS_MEDIUM}px;
        }}
    """

def get_dialog_background_style() -> str:
    """Return the background style for QDialog widgets"""
    return f"background-color: {BG_DARK.name()}; color: {TEXT_PRIMARY.name()};"

def get_status_background_color(is_implemented: bool) -> QColor:
    """
    Return the background color for status indicators
    
    Args:
        is_implemented: Whether the feature is implemented
    """
    return STATUS_IMPLEMENTED_BG if is_implemented else STATUS_COMING_SOON_BG

def get_status_text_color() -> QColor:
    """Return the text color for status indicators"""
    return STATUS_TEXT_COLOR

def get_separator_style() -> str:
    """Return the style for separator QFrame widgets"""
    return f"""
        QFrame[frameShape="4"], QFrame[frameShape="5"] {{
            background-color: {BORDER_DARK.name()};
            height: 1px;
            border: none;
        }}
        QFrame[frameShape="5"] {{
            background-color: {BORDER_DARK.name()};
            width: 1px;
            height: auto;
        }}
    """

def get_message_box_style() -> str:
    """Return the style for QMessageBox widgets"""
    return f"""
        QMessageBox {{
            background-color: {BG_MEDIUM.name()};
            color: {TEXT_PRIMARY.name()};
        }}
        QMessageBox QLabel {{
            color: {TEXT_PRIMARY.name()};
        }}
        QMessageBox QPushButton {{
            background-color: {BG_LIGHT.name()};
            color: {TEXT_PRIMARY.name()};
            border: 1px solid {BORDER_DARK.name()};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: {PADDING_MEDIUM}px {PADDING_LARGE}px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: {BG_HOVER.name()};
            border: 1px solid {BORDER_LIGHT.name()};
        }}
    """

def get_tab_widget_style() -> str:
    """Return the style for QTabWidget widgets"""
    return f"""
        QTabWidget::pane {{
            border: 1px solid {BORDER_DARK.name()};
            background-color: {BG_DARK.name()};
            top: -1px;
        }}
        QTabBar::tab {{
            background-color: {BG_MEDIUM.name()};
            color: {TEXT_PRIMARY.name()};
            padding: {PADDING_MEDIUM}px {PADDING_LARGE}px;
            margin-right: 2px;
            border-top-left-radius: {BORDER_RADIUS_SMALL}px;
            border-top-right-radius: {BORDER_RADIUS_SMALL}px;
        }}
        QTabBar::tab:selected {{
            background-color: {PRIMARY_DARK.name()};
            color: {TEXT_BRIGHT.name()};
        }}
        QTabBar::tab:hover {{
            background-color: {BG_HOVER.name()};
        }}
    """

def get_scroll_bar_style() -> str:
    """Return the style for QScrollBar widgets"""
    return f"""
        QScrollBar:vertical {{
            border: none;
            background-color: {BG_MEDIUM.name()};
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {PRIMARY_DARK.name()};
            min-height: 30px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {PRIMARY_COLOR.name()};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            border: none;
            background-color: {BG_MEDIUM.name()};
            height: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {PRIMARY_DARK.name()};
            min-width: 30px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {PRIMARY_COLOR.name()};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
    """

def get_progress_bar_style() -> str:
    """Return the style for QProgressBar widgets"""
    return f"""
        QProgressBar {{
            border: 1px solid {BORDER_DARK.name()};
            border-radius: {BORDER_RADIUS_SMALL}px;
            text-align: center;
            background-color: {BG_LIGHT.name()};
            color: {TEXT_PRIMARY.name()};
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {GRADIENT_START.name()}, stop: 1 {GRADIENT_END.name()});
            border-radius: {BORDER_RADIUS_SMALL}px;
        }}
    """

def get_table_style() -> str:
    """Return the style for QTableWidget widgets"""
    return f"""
        QTableWidget {{
            background-color: {BG_LIGHT.name()};
            color: {TEXT_PRIMARY.name()};
            border: 1px solid {BORDER_DARK.name()};
            border-radius: {BORDER_RADIUS_SMALL}px;
            gridline-color: rgba({BORDER_DARK.red()}, {BORDER_DARK.green()}, {BORDER_DARK.blue()}, 0.5);
        }}
        QTableWidget::item {{
            padding: 5px;
        }}
        QTableWidget::item:selected {{
            background-color: {PRIMARY_DARK.name()};
            color: {TEXT_BRIGHT.name()};
        }}
        QHeaderView::section {{
            background-color: {BG_MEDIUM.name()};
            color: {TEXT_PRIMARY.name()};
            padding: 5px;
            border: 1px solid {BORDER_DARK.name()};
            font-weight: bold;
        }}
    """

def get_colored_button_style(bg_color: str, border_color: str, hover_bg_color: str, hover_border_color: str, pressed_bg_color: str) -> str:
    """
    Return a custom colored style for QPushButton widgets
    
    Args:
        bg_color: Button background color
        border_color: Button border color
        hover_bg_color: Background color when hovered
        hover_border_color: Border color when hovered
        pressed_bg_color: Background color when pressed
    """
    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: white;
            border: 1px solid {border_color};
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: {PADDING_MEDIUM}px {PADDING_LARGE}px;
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {hover_bg_color};
            border: 1px solid {hover_border_color};
        }}
        QPushButton:pressed {{
            background-color: {pressed_bg_color};
        }}
    """

def get_camera_image_style() -> str:
    """Return the style for camera image QLabel widgets with transparent background"""
    return f"""
QLabel {{
    background-color: rgba(0, 0, 0, 50);
    border: 1px solid {BORDER_DARK.name()};
}}
    """

def get_image_label_style() -> str:
    """Return the style for image label with border"""
    return f"""
QLabel {{
    border: 1px solid {BORDER_DARK.name()};
    background-color: rgba(30, 30, 30, 50);
}}
    """
    
def get_active_image_label_style() -> str:
    """Return the style for active image label with highlighted border"""
    return f"""
QLabel {{
    border: 2px solid {PRIMARY_COLOR.name()};
    background-color: rgba(30, 30, 30, 50);
}}
    """
    
def get_inactive_image_label_style() -> str:
    """Return the style for inactive image label with regular border"""
    return f"""
QLabel {{
    border: 1px solid {BORDER_DARK.name()};
    background-color: rgba(30, 30, 30, 50);
}}
    """

def get_player_button_style() -> str:
    """Return the style for player control buttons with semi-transparent background"""
    return """
        QPushButton {
            background-color: rgba(51, 51, 51, 0.3);
            color: white;
            border: 1px solid rgba(85, 85, 85, 0.3);
            border-radius: 4px;
            padding: 8px;
            margin: 4px;
            width: 45px;
            height: 45px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: rgba(70, 70, 70, 0.3);
            border: 1px solid rgba(100, 100, 100, 0.3);
        }
        QPushButton:pressed {
            background-color: rgba(40, 40, 40, 0.3);
        }
        QPushButton:disabled {
            background-color: rgba(30, 30, 30, 0.3);
            color: rgba(128, 128, 128, 0.3);
            border: 1px solid rgba(60, 60, 60, 0.3);
        }
        QPushButton:checked {
            background-color: rgba(0, 120, 215, 0.3);
            border: 1px solid rgba(0, 150, 255, 0.3);
        }
    """

def get_speed_button_style() -> str:
    """Return the style for speed preset buttons with semi-transparent background"""
    return """
        QPushButton {
            background-color: rgba(51, 51, 51, 0.3);
            color: white;
            border: 1px solid rgba(85, 85, 85, 0.3);
            border-radius: 4px;
            padding: 6px 12px;
            margin: 4px;
            min-width: 60px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: rgba(70, 70, 70, 0.3);
            border: 1px solid rgba(100, 100, 100, 0.3);
        }
        QPushButton:pressed {
            background-color: rgba(40, 40, 40, 0.3);
        }
    """

def get_player_slider_style() -> str:
    """Return the style for player time slider with semi-transparent appearance"""
    return """
        QSlider::groove:horizontal {
            background: rgba(51, 51, 51, 0.3);
            height: 8px;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: rgba(0, 120, 215, 0.8);
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
    """

def get_status_label_style(status: str) -> str:
    """
    Return the style for status label based on completion status
    
    Args:
        status: Status string ('complete', 'progress', or 'start')
    """
    if status == "complete":
        return """
            QLabel {
                font-weight: bold;
                color: green;
            }
        """
    elif status == "progress":
        return """
            QLabel {
                font-weight: bold;
                color: orange;
            }
        """
    else:  # start
        return """
            QLabel {
                font-weight: bold;
                color: black;
            }
        """

def get_disabled_button_style() -> str:
    """Return the style for disabled buttons"""
    return "color: #888888;"

def get_menu_style() -> str:
    """Return the style for QMenu widgets"""
    return f"""
        QMenuBar {{
            background-color: {BG_DARK.name()};
            color: {TEXT_PRIMARY.name()};
            padding: 2px;
            spacing: 3px;
        }}
        
        QMenuBar::item {{
            background: transparent;
            padding: 4px 8px;
            border-radius: 3px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {BG_MEDIUM.name()};
        }}
        
        QMenuBar::item:pressed {{
            background-color: {BG_LIGHT.name()};
            color: {TEXT_BRIGHT.name()};
        }}
        
        QMenu {{
            background-color: {BG_MEDIUM.name()};
            color: {TEXT_PRIMARY.name()};
            border: 1px solid {BORDER_DARK.name()};
            padding: 5px;
            opacity: 1.0;
        }}
        
        QMenu::item {{
            padding: 5px 30px 5px 20px;
            border-radius: 2px;
            background-color: {BG_MEDIUM.name()};
        }}
        
        QMenu::item:selected {{
            background-color: {BG_HOVER.name()};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {BORDER_DARK.name()};
            margin: 5px 15px;
        }}
    """

def apply_dark_theme(widget) -> None:
    """
    Apply the dark theme to the given widget
    
    Args:
        widget: The widget to apply the theme to
    """
    # Base application style
    widget.setStyleSheet(get_application_style()) 