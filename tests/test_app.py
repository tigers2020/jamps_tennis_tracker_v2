"""
Tests for the main application class.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication

from src.views.app import TennisTrackerApp
from src.utils.logger import Logger
from src.utils.settings_manager import SettingsManager
from src.controllers.image_manager import ImageManager
from src.models.app_state import AppState

class TestTennisTrackerApp:
    """Test the main application class."""
    
    @pytest.fixture
    def mock_singletons(self):
        """Mock singleton instances."""
        with patch.object(Logger, 'instance', return_value=MagicMock(spec=Logger)) as mock_logger, \
             patch.object(SettingsManager, 'instance', return_value=MagicMock(spec=SettingsManager)) as mock_settings, \
             patch.object(ImageManager, 'instance', return_value=MagicMock(spec=ImageManager)) as mock_image_manager, \
             patch.object(AppState, 'instance', return_value=MagicMock(spec=AppState)) as mock_app_state:
            yield {
                'logger': mock_logger,
                'settings_manager': mock_settings,
                'image_manager': mock_image_manager,
                'app_state': mock_app_state
            }
    
    @pytest.fixture
    def mock_main_window(self):
        """Mock the MainWindow class."""
        with patch('src.views.app.MainWindow') as mock_main_window:
            # Configure the mock
            mock_instance = MagicMock()
            mock_main_window.return_value = mock_instance
            yield mock_main_window
    
    def test_init(self, mock_singletons, mock_main_window):
        """Test initialization of the application."""
        # Create instance
        with patch.object(QApplication, '__init__', return_value=None):
            app = TennisTrackerApp(sys.argv)
        
        # Verify singletons were initialized
        assert app.logger is not None
        assert app.settings_manager is not None
        assert app.image_manager is not None
        assert app.app_state is not None
        
        # Verify application info was set
        assert app.applicationName() == "Tennis Ball Tracker"
        assert app.applicationVersion() == "0.1.0"
        assert app.organizationName() == "Tennis Tracker Team"
        assert app.organizationDomain() == "example.com"
        
        # Verify main window was created and shown
        mock_main_window.assert_called_once()
        mock_main_window.return_value.show.assert_called_once()
    
    def test_close_event(self, mock_singletons, mock_main_window):
        """Test handling of close events."""
        # Create event mock
        event_mock = MagicMock()
        
        # Mock app instead of creating a real instance
        with patch('src.views.app.TennisTrackerApp', spec=TennisTrackerApp) as MockApp:
            app = MockApp.return_value
            app.logger = mock_singletons['logger'].return_value
            
            # Call closeEvent directly
            TennisTrackerApp.closeEvent(app, event_mock)
            
            # Verify event was accepted
            event_mock.accept.assert_called_once()
            
            # Verify logger logged shutdown
            app.logger.info.assert_called_with("Application shutting down...") 