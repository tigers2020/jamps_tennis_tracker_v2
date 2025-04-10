"""
Main Window Module

This module defines the main window widget that contains the tab structure
for the Tennis Ball Tracker application.
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel,
                               QMenuBar, QMenu, QFileDialog, QMessageBox, QSizePolicy, QProgressDialog)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QAction, QPainter, QPixmap, QBrush, QPalette, QColor

from src.models.app_state import AppState
from src.controllers.image_manager import ImageManager
from src.utils.logger import Logger
from src.utils.settings_manager import SettingsManager
from src.views.tabs.monitoring_tab import MonitoringTab
from src.views.tabs.settings_tab import SettingsTab
from src.views.tabs.coming_soon_tab import ComingSoonTab
from src.utils.ui_theme import (
    get_application_style, get_tab_widget_style, get_button_style,
    get_label_style, get_group_box_style, get_message_box_style,
    apply_dark_theme, get_menu_style, get_background_style, get_app_title_style,
    get_scrollbar_style, create_status_bar_style
)
from src.constants.ui_constants import (
    PRIMARY_COLOR, ERROR_COLOR, BG_DARK, BG_MEDIUM
)
# Modified to import dynamically
# from src.views.dialogs.folder_selection_dialog import FolderSelectionDialog
import os
import json

class MainWindow(QMainWindow):
    """
    Main window widget containing the tab structure for the application.
    
    This class organizes the UI into tabs for different functionalities:
    - Monitoring Tab: Real-time ball tracking and FPGA analysis
    - Analysis Tab: System accuracy analysis tools
    - Calibration Tab: Camera calibration tools
    - Replay Tab: Instant replay functionality
    - Settings Tab: Application configuration
    """
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Get singleton instances
        self.app_state = AppState.instance()
        self.logger = Logger.instance()
        self.image_manager = ImageManager.instance()
        self.settings_manager = SettingsManager.instance()
        
        # Set window properties
        self.setWindowTitle("Tennis Ball Tracker System")
        self.setMinimumSize(1366, 736)
        
        # Create central widget with background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create layout for central widget
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Set up menu bar
        self.setup_menu_bar()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(False)
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Center align tabs
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setUsesScrollButtons(False)
        tab_bar.setDrawBase(True)
        tab_bar.setExpanding(True)  # Expand tabs to full width
        tab_bar.setElideMode(Qt.ElideNone)  # Prevent tab text truncation
        
        # Apply the application-wide theme
        self.apply_theme()
        
        # Add tabs
        self.initialize_tabs()
        
        # Add tab widget to layout
        self.layout.addWidget(self.tab_widget)
        
        # Connect signals
        self.connect_signals()
        
        # Load last used file path
        self.load_last_file_path()
        
        # Setup background image
        self.setup_background()
        
        self.logger.debug("MainWindow initialized")
    
    def apply_theme(self):
        """Apply the application-wide theme"""
        # Apply base application style
        apply_dark_theme(self)
        
        # Apply specific styles to main window components
        self.setStyleSheet(f"""
            {get_application_style()}
            QMainWindow {{
                background-color: #1e1e1e;
            }}
            {get_tab_widget_style()}
            {get_menu_style()}
        """)
        
        # Apply styles to the tab widget
        self.tab_widget.setStyleSheet(get_tab_widget_style())
    
    def move_to_center(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        screen = self.screen()
        center_point = screen.availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def closeEvent(self, event):
        """Save settings when window is closed"""
        # Save window size and position
        self.settings_manager.update_window_geometry(self.size(), self.pos())
        
        # Save current playback speed
        fps = int(self.app_state.speed * 1000)
        self.settings_manager.update_playback_speed(fps)
        
        # Call parent class closeEvent
        super(MainWindow, self).closeEvent(event)
    
    def load_window_geometry(self):
        """Load saved window size and position"""
        # Load window size
        size = self.settings_manager.get("window_size", [1280, 720])
        self.resize(size[0], size[1])
        
        # Load window position
        position = self.settings_manager.get("window_position", [100, 100])
        self.move(position[0], position[1])
    
    def load_last_file_path(self):
        """Load last used file path and automatically load images"""
        last_folder_path = self.settings_manager.get("last_folder_path", "")
        if last_folder_path and os.path.exists(last_folder_path):
            self.logger.info(f"Found last used folder path: {last_folder_path}")
            
            # Check if frames_info.json file exists
            json_file_path = os.path.join(last_folder_path, "frames_info.json")
            
            if os.path.exists(json_file_path):
                # Display progress dialog
                progress_dialog = QProgressDialog("Loading image files...", "Cancel", 0, 100, self)
                progress_dialog.setWindowModality(Qt.WindowModal)
                progress_dialog.setWindowTitle("Image Loading")
                progress_dialog.setValue(10)
                progress_dialog.show()
                
                # Update QApplication event processing
                from PySide6.QtCore import QCoreApplication
                QCoreApplication.processEvents()
                
                # Load images from JSON file
                success = self.image_manager.load_images_from_json(json_file_path)
                
                if success:
                    # Update app state on successful load
                    self.app_state.file_path = last_folder_path
                    image_count = self.image_manager.get_total_images()
                    self.app_state.total_frames = image_count
                    self.app_state.current_frame = 0
                    self.app_state.playback_state = 'pause'
                    
                    # Switch to monitoring tab
                    if self.tab_widget.currentIndex() != 0:
                        self.tab_widget.setCurrentIndex(0)
                    
                    # Update monitoring tab's image display
                    monitoring_tab = self.tab_widget.widget(0)
                    if hasattr(monitoring_tab, 'image_display_manager'):
                        monitoring_tab.image_display_manager.update_displayed_images(0)
                        # Process overlay
                        if hasattr(monitoring_tab, '_process_overlay'):
                            monitoring_tab._process_overlay(1)  # Frame number is 1 (index 0 + 1)
                    
                    progress_dialog.setValue(100)
                    progress_dialog.close()
                    self.logger.info(f"Successfully loaded {image_count} images from last used folder")
                else:
                    # Load failed
                    progress_dialog.close()
                    self.logger.error(f"Failed to load images from last used folder: {last_folder_path}")
            else:
                # Try to load regular folder without JSON
                self.logger.info(f"No frames_info.json found, trying to load regular folder: {last_folder_path}")
                success = self.image_manager.load_folder(last_folder_path)
                
                if success:
                    self.logger.info(f"Successfully loaded images from regular folder: {last_folder_path}")
                    
                    # Update app state
                    self.app_state.file_path = last_folder_path
                    image_count = self.image_manager.get_total_images()
                    self.app_state.total_frames = image_count
                    self.app_state.current_frame = 0
                    
                    # Switch to monitoring tab and update display
                    if self.tab_widget.currentIndex() != 0:
                        self.tab_widget.setCurrentIndex(0)
                    
                    # Update monitoring tab's image display
                    monitoring_tab = self.tab_widget.widget(0)
                    if hasattr(monitoring_tab, 'image_display_manager'):
                        monitoring_tab.image_display_manager.update_displayed_images(0)
                else:
                    self.logger.error(f"Failed to load images from regular folder: {last_folder_path}")
        else:
            self.logger.debug("No available last folder path")
    
    def setup_menu_bar(self):
        """Set up the menu bar with various menus and actions"""
        # Create menu bar
        self.menu_bar = QMenuBar(self)
        
        # Create File menu
        file_menu = QMenu("File", self.menu_bar)
        self.menu_bar.addMenu(file_menu)
        
        # Create Open Folder action
        open_folder_action = QAction("Open Image Folder...", self)
        open_folder_action.setShortcut("Ctrl+O")
        open_folder_action.triggered.connect(self.on_open_folder)
        file_menu.addAction(open_folder_action)
        
        # Create Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Add menu bar to the layout
        self.layout.setMenuBar(self.menu_bar)
    
    def on_open_folder(self):
        """Handle opening a folder containing images for playback"""
        self.logger.debug("Open folder menu action triggered")
        
        # Direct implementation of folder selection dialog
        initial_dir = self.settings_manager.get_last_folder_path() or os.path.expanduser("~")
        
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Image Folder", initial_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not folder_path:
            return  # User canceled
        
        self.logger.info(f"Selected folder: {folder_path}")
        
        # Save selected folder path
        self.settings_manager.update_last_folder_path(folder_path)
        
        # Display progress dialog
        progress_dialog = QProgressDialog("Loading image files...", "Cancel", 0, 100, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle("Image Loading")
        progress_dialog.setValue(10)
        progress_dialog.show()
        
        # Update QApplication event processing (maintain UI responsiveness)
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.processEvents()
        
        # Check if frames_info.json file exists
        json_file_path = os.path.join(folder_path, "frames_info.json")
        
        if os.path.exists(json_file_path):
            # If JSON file exists, load through ImageManager
            success = self.image_manager.load_images_from_json(json_file_path)
            
            if success:
                # Update app state on successful load
                self.app_state.file_path = folder_path
                image_count = self.image_manager.get_total_images()
                self.app_state.total_frames = image_count
                self.app_state.current_frame = 0
                self.app_state.playback_state = 'pause'
                
                # Switch to monitoring tab
                if self.tab_widget.currentIndex() != 0:
                    self.tab_widget.setCurrentIndex(0)
                
                # Update monitoring tab's image display
                monitoring_tab = self.tab_widget.widget(0)
                if hasattr(monitoring_tab, 'image_display_manager'):
                    monitoring_tab.image_display_manager.update_displayed_images(0)
                    # Process overlay
                    if hasattr(monitoring_tab, '_process_overlay'):
                        monitoring_tab._process_overlay(1)  # Frame number is 1 (index 0 + 1)
                
                progress_dialog.setValue(100)
                progress_dialog.close()
                QMessageBox.information(
                    self, 
                    "Load Complete", 
                    f"{image_count} images have been loaded."
                )
                self.logger.info(f"Successfully loaded {image_count} images from JSON")
            else:
                # Load failed
                progress_dialog.close()
                QMessageBox.warning(
                    self,
                    "Load Failed", 
                    "Failed to load image information file."
                )
                self.logger.error(f"Failed to load images from JSON: {json_file_path}")
        else:
            # If JSON file doesn't exist, check folder structure
            camera_dirs = [
                os.path.join(folder_path, "LeftCamera"),
                os.path.join(folder_path, "RightCamera")
            ]
            
            # Check if camera folders exist
            if all(os.path.exists(d) for d in camera_dirs):
                # Folder structure is correct but JSON file is missing
                progress_dialog.close()
                QMessageBox.warning(
                    self,
                    "Frame Info File Missing",
                    "The selected folder has the image structure but no frame information file.\n"
                    "Image processing must be performed first."
                )
                self.logger.warning("Folder has camera structure but no frames_info.json")
            else:
                # Image folder structure is incorrect
                progress_dialog.close()
                
                # Search for image formats
                img_files = []
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.bmp')):
                            img_files.append(os.path.join(root, file))
                            if len(img_files) >= 10:  # Check maximum of 10
                                break
                
                if img_files:
                    # Images exist but structure is incorrect - provide processing options
                    result = QMessageBox.question(
                        self,
                        "Folder Structure Setup",
                        "The selected folder contains image files but doesn't have the required folder structure.\n\n"
                        "The Tennis Ball Tracker application requires the following folder structure:\n"
                        "- [folder_name]/LeftCamera/raw/...\n"
                        "- [folder_name]/LeftCamera/resize/...\n"
                        "- [folder_name]/RightCamera/raw/...\n"
                        "- [folder_name]/RightCamera/resize/...\n"
                        "- [folder_name]/frames_info.json\n\n"
                        "Do you want to start the image processing?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if result == QMessageBox.Yes:
                        # Start image processing
                        self._process_image_folder(folder_path)
                else:
                    # No image files
                    QMessageBox.warning(
                        self,
                        "No Image Files",
                        "There are no image files in the selected folder."
                    )
                    
                self.logger.warning(f"Folder does not have proper structure: {folder_path}")
    
    def _process_image_folder(self, folder_path):
        """Process image folder to create the necessary folder structure and classify images."""
        # 진행 대화상자 생성
        # Create progress dialog
        from PySide6.QtWidgets import QProgressDialog
        from PySide6.QtCore import QCoreApplication, Qt
        
        progress = QProgressDialog("Processing image files...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setWindowTitle("Image Processing")
        progress.setValue(0)
        progress.show()
        
        try:
            # 1. 필요한 폴더 구조 생성
            for camera in ["LeftCamera", "RightCamera"]:
                for subdir in ["raw", "resize"]:
                    path = os.path.join(folder_path, camera, subdir)
                    os.makedirs(path, exist_ok=True)
            
            progress.setValue(10)
            QCoreApplication.processEvents()
            
            # 2. 이미지 파일 검색
            import shutil
            from PIL import Image
            
            self.logger.info("Searching for image files...")
            progress.setLabelText("Searching for image files...")
            
            left_files = []
            right_files = []
            
            # 모든 이미지 파일 검색
            all_files = []
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.bmp')):
                        file_path = os.path.join(root, file)
                        all_files.append(file_path)
            
            progress.setValue(20)
            progress.setLabelText("Classifying images...")
            QCoreApplication.processEvents()
            
            # 파일명으로 좌/우 카메라 이미지 분류
            for file in all_files:
                if progress.wasCanceled():
                    return
                    
                if "left" in file.lower() or "leftcamera" in file.lower():
                    left_files.append(file)
                elif "right" in file.lower() or "rightcamera" in file.lower():
                    right_files.append(file)
            
            # 만약 Left/Right가 구분되지 않았다면 파일을 첫 번째 절반과 두 번째 절반으로 나누기
            if not left_files and not right_files and all_files:
                all_files.sort()
                mid = len(all_files) // 2
                left_files = all_files[:mid]
                right_files = all_files[mid:]
            
            if not left_files or not right_files:
                progress.close()
                QMessageBox.warning(
                    self,
                    "Image Classification Failed",
                    "Cannot distinguish between left and right camera images.\n"
                    "Filenames must contain 'Left'/'Right' or 'LeftCamera'/'RightCamera'."
                )
                return
            
            # 파일 정렬
            left_files.sort()
            right_files.sort()
            
            progress.setValue(30)
            progress.setLabelText("Copying and adjusting files...")
            QCoreApplication.processEvents()
            
            # 3. 이미지 처리 및 복사
            self.logger.info(f"Processing {len(left_files)} left files and {len(right_files)} right files")
            total_files = min(len(left_files), len(right_files))
            frame_info = {}
            
            # 각 프레임 처리
            for i in range(total_files):
                if progress.wasCanceled():
                    return
                    
                left_file = left_files[i]
                right_file = right_files[i]
                frame_number = i + 1
                
                # 파일 경로 생성
                left_raw = f"LeftCamera/raw/frame_{frame_number:04d}_LeftCamera.jpg"
                right_raw = f"RightCamera/raw/frame_{frame_number:04d}_RightCamera.jpg"
                left_resize = f"LeftCamera/resize/frame_{frame_number:04d}_LeftCamera.jpg"
                right_resize = f"RightCamera/resize/frame_{frame_number:04d}_RightCamera.jpg"
                
                # raw 파일 복사
                self._copy_file(left_file, os.path.join(folder_path, left_raw))
                self._copy_file(right_file, os.path.join(folder_path, right_raw))
                
                # 이미지 리사이징
                self._resize_image(
                    os.path.join(folder_path, left_raw),
                    os.path.join(folder_path, left_resize),
                    height=280
                )
                self._resize_image(
                    os.path.join(folder_path, right_raw),
                    os.path.join(folder_path, right_resize),
                    height=280
                )
                
                # 프레임 정보 추가
                frame_info[str(frame_number)] = {
                    "frame_number": frame_number,
                    "left_raw": left_raw.replace("/", "\\"),
                    "right_raw": right_raw.replace("/", "\\"),
                    "left_resize": left_resize.replace("/", "\\"),
                    "right_resize": right_resize.replace("/", "\\")
                }
                
                # 진행상황 업데이트
                progress_value = 30 + int((i + 1) / total_files * 60)  # 30% ~ 90%
                progress.setValue(progress_value)
                progress.setLabelText(f"Processing images... ({i+1}/{total_files})")
                QCoreApplication.processEvents()
            
            progress.setValue(90)
            progress.setLabelText("Generating JSON file...")
            QCoreApplication.processEvents()
            
            # 4. JSON 파일 생성
            json_data = {
                "total_frames": total_files,
                "frame_info": frame_info
            }
            
            json_file_path = os.path.join(folder_path, "frames_info.json")
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4)
            
            self.logger.info(f"Created frames_info.json with {total_files} frames")
            
            progress.setValue(100)
            progress.setLabelText("Processing complete!")
            QCoreApplication.processEvents()
            
            # 처리 완료 후 이미지 로드
            success = self.image_manager.load_images_from_json(json_file_path)
            
            if success:
                # 로드 성공 시 앱 상태 업데이트
                self.app_state.file_path = folder_path
                image_count = self.image_manager.get_total_images()
                self.app_state.total_frames = image_count
                self.app_state.current_frame = 0
                self.app_state.playback_state = 'pause'
                
                # 모니터링 탭으로 전환
                if self.tab_widget.currentIndex() != 0:
                    self.tab_widget.setCurrentIndex(0)
                
                # 모니터링 탭의 이미지 갱신
                # Update monitoring tab's image display
                monitoring_tab = self.tab_widget.widget(0)
                if hasattr(monitoring_tab, 'image_display_manager'):
                    monitoring_tab.image_display_manager.update_displayed_images(0)
                    # 오버레이 처리
                    if hasattr(monitoring_tab, '_process_overlay'):
                        monitoring_tab._process_overlay(1)  # Frame number is 1 (index 0 + 1)
                
                progress.close()
                QMessageBox.information(
                    self, 
                    "Processing Complete", 
                    f"Image processing is complete.\n{image_count} images have been loaded."
                )
                self.logger.info(f"Successfully loaded {image_count} images after processing")
            else:
                progress.close()
                QMessageBox.warning(
                    self,
                    "Load Failed",
                    "Images were processed but failed to load."
                )
                self.logger.error("Failed to load images after processing")
                
        except Exception as e:
            self.logger.error(f"Error processing image folder: {str(e)}")
            progress.close()
            QMessageBox.critical(
                self,
                "Processing Error",
                f"An error occurred during image processing:\n{str(e)}"
            )
    
    def _copy_file(self, src, dst):
        """Copy a file. Skips if the destination file already exists."""
        try:
            if not os.path.exists(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                
                # 이미지 파일만 복사
                import shutil
                shutil.copy2(src, dst)
                
            return True
        except Exception as e:
            self.logger.error(f"Error copying file {src} to {dst}: {str(e)}")
            return False
    
    def _resize_image(self, src, dst, height=280):
        """Resize an image. Skips if the destination file already exists."""
        if not os.path.exists(dst):
            try:
                from PIL import Image
                img = Image.open(src)
                w, h = img.size
                new_width = int(w * height / h)
                resized_img = img.resize((new_width, height), Image.LANCZOS)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                resized_img.save(dst, "JPEG", quality=85)
            except Exception as e:
                self.logger.error(f"Error resizing image {src}: {str(e)}")
                # 리사이징 실패 시 원본 파일 복사
                self._copy_file(src, dst)
    
    def initialize_tabs(self):
        """Initialize and add all tabs to the tab widget"""
        # Initialize the monitoring tab (implemented)
        self.monitoring_tab = MonitoringTab()
        self.tab_widget.addTab(self.monitoring_tab, "Monitoring")
        
        # Create placeholder tabs for not yet implemented functionality
        self.create_placeholder_tab("Analysis")
        
        # Initialize the calibration tab
        from src.views.tabs import CalibrationTab
        self.calibration_tab = CalibrationTab()
        self.tab_widget.addTab(self.calibration_tab, "Calibration")
        
        self.create_placeholder_tab("Instant Replay")
        
        # Initialize the settings tab
        self.settings_tab = SettingsTab()
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        # Initialize the coming soon tab
        self.coming_soon_tab = ComingSoonTab()
        self.tab_widget.addTab(self.coming_soon_tab, "Coming Soon")
        
        # Connect settings tab signals
        self.settings_tab.settings_changed.connect(self.on_settings_changed)
    
    def create_placeholder_tab(self, name):
        """Create a placeholder tab with 'coming soon' message"""
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        
        # Add a descriptive label
        label = QLabel(f"{name} features coming soon...")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        self.tab_widget.addTab(placeholder, name)
    
    def connect_signals(self):
        """Connect signals to slots"""
        # Connect app state signals
        self.app_state.active_tab_changed.connect(self.on_active_tab_changed)
        self.app_state.current_frame_changed.connect(self.on_frame_changed)
        
        # Connect tab widget signals
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Connect image manager signals
        # Add any additional signal connections here
    
    @Slot(str)
    def on_active_tab_changed(self, tab_name):
        """Handle active tab change"""
        self.logger.debug(f"Switching to tab: {tab_name}")
        
        # Map tab names to indices
        tab_indices = {
            "monitoring": 0,
            "analysis": 1,
            "calibration": 2,
            "replay": 3,
            "settings": 4
        }
        
        # Set the current tab based on the tab name
        if tab_name in tab_indices:
            self.tab_widget.setCurrentIndex(tab_indices[tab_name])
    
    @Slot(int)
    def on_frame_changed(self, frame):
        """
        Handle frame changes from app state by updating image manager
        
        Args:
            frame: New frame index
        """
        # Only update if we have images loaded
        if self.image_manager.get_total_images() > 0:
            # Set the current image based on the frame number
            self.image_manager.set_current_index(frame)
    
    @Slot(int)
    def on_tab_changed(self, index):
        """Handler for tab change events"""
        tab_names = ["Monitoring", "Analysis", "Calibration", "Instant Replay", "Settings", "Coming Soon"]
        if 0 <= index < len(tab_names):
            self.logger.debug(f"Tab changed to: {tab_names[index]}")
            
            # Additional tab-specific actions can be added here
    
    @Slot()
    def on_settings_changed(self):
        """Handle settings changes"""
        self.logger.info("Settings changed, updating application state")
        
        # Update playback speed in app state
        fps = self.settings_manager.get_playback_speed()
        self.app_state.speed = fps / 1000.0
        
        # Update loop playback setting
        self.app_state.loop_playback = self.settings_manager.get("loop_playback", True)
        
        # Forward settings changes to monitoring tab
        if hasattr(self, 'monitoring_tab'):
            # Update FPGA connection settings
            if hasattr(self.monitoring_tab, 'update_fpga_settings'):
                fpga_settings = {
                    'com_port': self.settings_manager.get("fpga_com_port", ""),
                    'baud_rate': self.settings_manager.get("fpga_baud_rate", 115200),
                    'data_bits': self.settings_manager.get("fpga_data_bits", 8),
                    'auto_connect': self.settings_manager.get("fpga_auto_connect", False)
                }
                self.monitoring_tab.update_fpga_settings(fpga_settings)
            
            # Update playback settings
            if hasattr(self.monitoring_tab, 'player_controls'):
                self.monitoring_tab.player_controls.update_speed(fps)
                
            # Update other relevant settings as needed 
    
    def setup_background(self):
        """Set up the background image for the main window"""
        # Background will be drawn in paintEvent, but we'll check here that it exists
        background = QPixmap("src/resources/images/background.png")
        
        if background.isNull():
            self.logger.warning("Failed to load background image")
            # Apply a fallback dark color if image is not available
            palette = self.palette()
            palette.setColor(QPalette.Window, BG_MEDIUM)
            self.setPalette(palette)
            self.centralWidget().setAutoFillBackground(True)
        else:
            self.logger.debug("Background image loaded successfully")
            # Set transparent background for widgets to allow background image to show
            self.centralWidget().setStyleSheet("background-color: transparent;")
            self.tab_widget.setStyleSheet(self.tab_widget.styleSheet() + "background-color: transparent;")
    
    def paintEvent(self, event):
        """Override paint event to ensure background is properly stretched"""
        # Call the parent class's paintEvent to handle normal painting
        super(MainWindow, self).paintEvent(event)
        
        # Create a painter for this widget
        painter = QPainter(self)
        
        # Load the background image
        background = QPixmap("src/resources/images/background.png")
        if not background.isNull():
            # Draw the background image stretched to fill the entire window
            painter.drawPixmap(0, 0, self.width(), self.height(), background)
        
        # End the painting session
        painter.end() 

    def _setup_dark_theme(self):
        """Set up dark theme for the application"""
        palette = self.palette()
        palette.setColor(QPalette.Window, BG_MEDIUM)
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette) 