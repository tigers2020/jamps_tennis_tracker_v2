"""
Tennis Ball Tracker Application

This is the main entry point for the Tennis Ball Tracker application.
It initializes the application and starts the main window.
"""

import sys
import os
from pathlib import Path

# Application constants
APP_NAME = "Tennis Ball Tracker"
APP_VERSION = "0.1.0"
ORG_NAME = "Tennis Tracker Team"
ORG_DOMAIN = "example.com"
APP_STYLE = "Fusion"

# Set up paths
PROJECT_ROOT = Path(__file__).resolve().parent
TENNIS_TRACKER_PATH = PROJECT_ROOT / "tennis_tracker"

# Add project directories to Python path
sys.path.insert(0, str(PROJECT_ROOT))
if TENNIS_TRACKER_PATH.exists():
    sys.path.insert(0, str(TENNIS_TRACKER_PATH))

from src.views.app import TennisTrackerApp
from src.utils.logger import Logger


def main():
    """
    Main application entry point.
    
    Initializes the Qt application, configures application settings,
    creates the main window, and starts the event loop.
    
    Returns:
        int: Application exit code
    """
    # Create logger
    logger = Logger.instance()
    logger.info("Application starting...")
    
    # Create and initialize application
    app = TennisTrackerApp(sys.argv)
    app.setStyle(APP_STYLE)
    
    # Start event loop
    exit_code = app.exec()
    
    logger.info(f"Application exiting with code {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 