"""
Tennis Ball Tracker Application

This is the main entry point for the Tennis Ball Tracker application.
It initializes the application and starts the main window.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.views.app import TennisTrackerApp
from src.utils.logger import Logger


def main():
    """Main application entry point."""
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QCoreApplication
    from src.views.main_window import MainWindow

    # Create application
    app = QApplication(sys.argv)
    
    # Set application information
    QCoreApplication.setApplicationName("Tennis Ball Tracker")
    QCoreApplication.setApplicationVersion("0.1.0")
    QCoreApplication.setOrganizationName("Tennis Tracker Team")
    QCoreApplication.setOrganizationDomain("example.com")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create logger
    logger = Logger.instance()
    logger.info("Application starting...")
    
    # Create main window
    main_app = TennisTrackerApp()
    main_window = MainWindow(main_app)
    main_app.setCentralWidget(main_window)
    
    # Show window
    main_app.show()
    
    # Start event loop
    exit_code = app.exec()
    
    logger.info(f"Application exiting with code {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 