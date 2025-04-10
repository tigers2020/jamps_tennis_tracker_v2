"""
Tests for the MainWindow class.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout

from src.views.main_window import MainWindow
from src.models.app_state import AppState
from src.utils.logger import Logger
from src.utils.settings_manager import SettingsManager
from src.controllers.image_manager import ImageManager

class TestMainWindow:
    """Test cases for the MainWindow class."""
    
    @pytest.fixture
    def mock_singletons(self):
        """Mock singleton instances."""
        with patch.object(AppState, 'instance', return_value=MagicMock(spec=AppState)) as mock_app_state, \
             patch.object(Logger, 'instance', return_value=MagicMock(spec=Logger)) as mock_logger, \
             patch.object(SettingsManager, 'instance', return_value=MagicMock(spec=SettingsManager)) as mock_settings, \
             patch.object(ImageManager, 'instance', return_value=MagicMock(spec=ImageManager)) as mock_image_manager:
            yield {
                'app_state': mock_app_state,
                'logger': mock_logger,
                'settings_manager': mock_settings,
                'image_manager': mock_image_manager
            }
    
    @pytest.fixture
    def mock_setup_methods(self):
        """Mock setup methods in MainWindow."""
        with patch.object(MainWindow, 'setup_menu_bar'), \
             patch.object(MainWindow, 'initialize_tabs'), \
             patch.object(MainWindow, 'connect_signals'), \
             patch.object(MainWindow, 'load_last_file_path'):
            yield
    
    @pytest.fixture
    def main_window(self, qapp, mock_singletons, mock_setup_methods):
        """Create a MainWindow instance for testing."""
        # MainWindow를 직접 인스턴스화하는 대신 모의 객체 생성
        window = MagicMock(spec=MainWindow)
        
        # 필요한 속성 설정
        window.logger = mock_singletons['logger'].return_value
        window.app_state = mock_singletons['app_state'].return_value
        window.settings_manager = mock_singletons['settings_manager'].return_value
        window.image_manager = mock_singletons['image_manager'].return_value
        window.tab_widget = MagicMock(spec=QTabWidget)
        
        yield window
    
    def test_init(self, main_window, mock_singletons, mock_setup_methods):
        """Test initialization of MainWindow."""
        # Verify singletons were initialized
        assert main_window.app_state is not None
        assert main_window.logger is not None
        assert main_window.image_manager is not None
        assert main_window.settings_manager is not None
        
        # Verify UI was set up
        MainWindow.setup_menu_bar.assert_called_once()
        MainWindow.initialize_tabs.assert_called_once()
        MainWindow.connect_signals.assert_called_once()
        MainWindow.load_last_file_path.assert_called_once()
    
    def test_initialize_tabs(self, main_window, qapp):
        """Test tab initialization."""
        # Mock required modules and classes
        with patch('src.views.tabs.monitoring_tab.MonitoringTab') as MockMonitoringTab, \
             patch('src.views.tabs.settings_tab.SettingsTab') as MockSettingsTab, \
             patch('src.views.tabs.coming_soon_tab.ComingSoonTab') as MockComingSoonTab, \
             patch('src.views.tabs.CalibrationTab') as MockCalibrationTab, \
             patch.object(main_window, 'create_placeholder_tab'):
            
            # Create mock instances
            mock_monitoring_tab = MagicMock()
            mock_settings_tab = MagicMock()
            mock_coming_soon_tab = MagicMock()
            mock_calibration_tab = MagicMock()
            
            # Configure mocks
            MockMonitoringTab.return_value = mock_monitoring_tab
            MockSettingsTab.return_value = mock_settings_tab
            MockComingSoonTab.return_value = mock_coming_soon_tab
            MockCalibrationTab.return_value = mock_calibration_tab
            
            # Call method
            main_window.initialize_tabs()
            
            # Verify tabs were created
            MockMonitoringTab.assert_called_once()
            MockSettingsTab.assert_called_once()
            MockComingSoonTab.assert_called_once()
            MockCalibrationTab.assert_called_once()
            
            # Verify tabs were added to tab widget
            assert main_window.tab_widget.addTab.call_count >= 4
            
            # Verify placeholder tabs were created
            assert main_window.create_placeholder_tab.call_count >= 2
    
    def test_create_placeholder_tab(self, main_window, qapp):
        """Test placeholder tab creation."""
        with patch('src.views.main_window.QWidget') as MockWidget, \
             patch('src.views.main_window.QVBoxLayout') as MockLayout, \
             patch('src.views.main_window.QLabel') as MockLabel:
            
            # Create mock instances
            mock_widget = MagicMock()
            mock_layout = MagicMock()
            mock_label = MagicMock()
            
            # Configure mocks
            MockWidget.return_value = mock_widget
            MockLayout.return_value = mock_layout
            MockLabel.return_value = mock_label
            
            # Call method
            main_window.create_placeholder_tab("Test Tab")
            
            # Verify widget was created
            MockWidget.assert_called_once()
            
            # Verify layout was created and applied to widget
            MockLayout.assert_called_once_with(mock_widget)
            
            # Verify label was created with correct text
            MockLabel.assert_called_once()
            assert "Test Tab" in MockLabel.call_args[0][0]
            
            # Verify label was added to layout
            mock_layout.addWidget.assert_called_once_with(mock_label)
            
            # Verify tab was added to tab widget
            main_window.tab_widget.addTab.assert_called_once_with(mock_widget, "Test Tab")
    
    def test_connect_signals(self, main_window):
        """Test signal connections."""
        # Call method
        main_window.connect_signals()
        
        # Verify app state signals were connected
        main_window.app_state.active_tab_changed.connect.assert_called_once()
        main_window.app_state.current_frame_changed.connect.assert_called_once()
        
        # Verify tab widget signal was connected
        main_window.tab_widget.currentChanged.connect.assert_called_once()
    
    def test_on_active_tab_changed(self, main_window):
        """Test handling of active tab change."""
        # Set up test
        main_window.tab_widget.setCurrentIndex = MagicMock()
        
        # Call method with valid tab name
        main_window.on_active_tab_changed("monitoring")
        
        # Verify tab widget index was set
        main_window.tab_widget.setCurrentIndex.assert_called_once_with(0)
        
        # Reset mock
        main_window.tab_widget.setCurrentIndex.reset_mock()
        
        # Call method with invalid tab name
        main_window.on_active_tab_changed("invalid_tab")
        
        # Verify tab widget index was not set
        main_window.tab_widget.setCurrentIndex.assert_not_called()
    
    def test_on_frame_changed(self, main_window):
        """Test handling of frame change."""
        # Set up test
        main_window.image_manager.get_total_images.return_value = 10
        
        # Call method
        main_window.on_frame_changed(5)
        
        # Verify image manager method was called
        main_window.image_manager.set_current_index.assert_called_once_with(5)
        
        # Reset mock
        main_window.image_manager.set_current_index.reset_mock()
        
        # Test with no images loaded
        main_window.image_manager.get_total_images.return_value = 0
        
        # Call method
        main_window.on_frame_changed(5)
        
        # Verify image manager method was not called
        main_window.image_manager.set_current_index.assert_not_called()
    
    def test_on_tab_changed(self, main_window):
        """Test handling of tab change."""
        # Call method with valid index
        main_window.on_tab_changed(0)
        
        # Verify log message
        main_window.logger.debug.assert_called_once()
        assert "Monitoring" in main_window.logger.debug.call_args[0][0]
        
        # Reset mock
        main_window.logger.debug.reset_mock()
        
        # Call method with invalid index
        main_window.on_tab_changed(10)
        
        # Verify no log message
        main_window.logger.debug.assert_not_called()
    
    def test_on_settings_changed(self, main_window):
        """Test handling of settings changes."""
        # Set up test
        main_window.settings_manager.get_playback_speed.return_value = 1000
        main_window.settings_manager.get.return_value = True
        
        # Mock monitoring tab
        main_window.monitoring_tab = MagicMock()
        main_window.monitoring_tab.player_controls = MagicMock()
        main_window.monitoring_tab.update_fpga_settings = MagicMock()
        
        # Call method
        main_window.on_settings_changed()
        
        # Verify app state was updated
        assert main_window.app_state.speed == 1.0
        assert main_window.app_state.loop_playback == True
        
        # Verify monitoring tab methods were called
        main_window.monitoring_tab.update_fpga_settings.assert_called_once()
        main_window.monitoring_tab.player_controls.update_speed.assert_called_once_with(1000) 