"""
Tennis Tracker Application Module

This module defines the main application class for the Tennis Ball Tracker.
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from src.views.main_window import MainWindow
from src.utils.logger import Logger
from src.utils.settings_manager import SettingsManager
from src.controllers.image_manager import ImageManager
from src.models.app_state import AppState
import sys

class TennisTrackerApp(QApplication):
    """
    Main application class for the Tennis Ball Tracker.
    
    This class initializes the application, sets up the main window,
    and manages the application lifecycle.
    """
    
    def __init__(self, argv):
        """Initialize the Tennis Ball Tracker application."""
        super(TennisTrackerApp, self).__init__(argv)
        
        # Initialize singletons
        self.logger = Logger.instance()
        self.settings_manager = SettingsManager.instance()
        self.image_manager = ImageManager.instance()
        self.app_state = AppState.instance()
        
        # Set application information
        self.setApplicationName("Tennis Ball Tracker")
        self.setApplicationVersion("0.1.0")
        self.setOrganizationName("Tennis Tracker Team")
        self.setOrganizationDomain("example.com")
        
        # Create and show main window
        self.main_window = MainWindow()
        self.main_window.show()
        
        self.logger.info("Tennis Ball Tracker application initialized")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.logger.info("Application shutting down...")
        # Any cleanup needed before exit
        event.accept() 