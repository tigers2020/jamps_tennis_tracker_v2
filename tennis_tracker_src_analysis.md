# Tennis Tracker Source Code Analysis

## 1. Project Structure Overview

The Tennis Tracker project follows the MVC (Model-View-Controller) architecture and is organized with the following directory structure:

```
tennis_tracker/src/
├── controllers/ - Controller classes
├── models/ - Data model classes
├── views/ - UI related classes
├── utils/ - Utility functions
└── resources/ - Resource files
```

## 2. Module Dependency Analysis

### 2.1. Core Classes and Dependencies

#### 2.1.1. Models

* **AppState** (`models/app_state.py`)
  * Application state management class implemented using the singleton pattern.
  * Dependencies: `qt_singleton` decorator from `models/singleton.py`

* **ImageCache** (`models/image_cache.py`)
  * Class for handling image caching.
  * Dependencies: `Logger` from `utils/logger.py`

* **Singleton** (`models/singleton.py`)
  * Decorator class for implementing the singleton pattern.
  * Independent implementation with no external dependencies.

#### 2.1.2. Controllers

* **ImageManager** (`controllers/image_manager.py`)
  * Image management class.
  * Dependencies:
    * `qt_singleton` from `models/singleton.py`
    * `ImageCache` from `models/image_cache.py`
    * `FrameManager` from `controllers/frame_manager.py`
    * `FileUtils` from `utils/file_utils.py`
    * `Logger` from `utils/logger.py`

* **FrameManager** (`controllers/frame_manager.py`)
  * Frame information management class.
  * Dependencies:
    * `Logger` from `utils/logger.py`
    * `FileUtils` from `utils/file_utils.py`

* **CourtDetector** (`controllers/tennis_court_detection/court_detector.py`)
  * Tennis court detection class (implementation currently in progress).
  * Relatively independent implementation with few external dependencies.

#### 2.1.3. Views

* **MainWindow** (`views/main_window.py`)
  * Main window UI class.
  * Dependencies:
    * `AppState` from `models/app_state.py`
    * `ImageManager` from `controllers/image_manager.py`
    * `Logger` from `utils/logger.py`
    * `SettingsManager` from `utils/settings_manager.py`
    * `MonitoringTab` from `views/tabs/monitoring_tab.py`
    * `SettingsTab` from `views/tabs/settings_tab.py`
    * `ComingSoonTab` from `views/tabs/coming_soon_tab.py`
    * `CalibrationTab` from `views/tabs/calibration/calibration_tab.py`
    * `FolderSelectionDialog` from `views/dialogs/folder_selection_dialog.py`

* **CalibrationTab** (`views/tabs/calibration/calibration_tab.py`)
  * Court calibration tab UI class.
  * Dependencies:
    * `ImageManager` from `controllers/image_manager.py`
    * `AppState` from `models/app_state.py`
    * Internal modules (`point_manager.py`, `point_io.py`, `image_utils.py`)

* **MonitoringTab** (`views/tabs/monitoring_tab.py`)
  * Monitoring tab UI class.
  * Dependencies:
    * `PlayerControls` from `views/widgets/player_controls.py`
    * `LedDisplay` from `views/widgets/led_display.py`
    * `AppState` from `models/app_state.py`
    * `ImageManager` from `controllers/image_manager.py`
    * `Logger` from `utils/logger.py`
    * `SettingsManager` from `utils/settings_manager.py`

* **SettingsTab** (`views/tabs/settings_tab.py`)
  * Settings tab UI class.
  * Dependencies:
    * `SettingsManager` from `utils/settings_manager.py`
    * `Logger` from `utils/logger.py`
    * `AppState` from `models/app_state.py`

* **ComingSoonTab** (`views/tabs/coming_soon_tab.py`)
  * Upcoming features introduction tab UI class.
  * Dependencies:
    * `Logger` from `utils/logger.py`

#### 2.1.4. Utilities (Utils)

* **Logger** (`utils/logger.py`)
  * Logging utility class.
  * Dependencies: `qt_singleton` from `models/singleton.py`

* **Config** (`utils/config.py`)
  * Configuration management class.
  * Dependencies:
    * `qt_singleton` from `models/singleton.py`
    * `Logger` from `utils/logger.py`

* **SettingsManager** (`utils/settings_manager.py`)
  * User settings management class.
  * Dependencies:
    * `qt_singleton` from `models/singleton.py`
    * `Logger` from `utils/logger.py`

* **FileUtils** (`utils/file_utils.py`)
  * File utility class.
  * Dependencies: `Logger` from `utils/logger.py`

### 2.2. Widget Dependencies

* **PlayerControls** (`views/widgets/player_controls.py`)
  * Dependencies:
    * `AppState` from `models/app_state.py`
    * `Logger` from `utils/logger.py`
    * `SettingsManager` from `utils/settings_manager.py`

* **LedDisplay** (`views/widgets/led_display.py`)
  * Dependencies:
    * `AppState` from `models/app_state.py`
    * `Config` from `utils/config.py`

### 2.3. Dialog Dependencies

* **FolderSelectionDialog** (`views/dialogs/folder_selection_dialog.py`)
  * Dependencies:
    * `AppState` from `models/app_state.py`
    * `Logger` from `utils/logger.py`
    * `ImageManager` from `controllers/image_manager.py`
    * `SettingsManager` from `utils/settings_manager.py`

* **CourtCalibrationDialog** (`views/dialogs/court_calibration_dialog.py`)
  * Dependencies:
    * `Logger` from `utils/logger.py`
    * `ImageManager` from `controllers/image_manager.py`

* **CameraCalibrationDialog** (`views/dialogs/camera_calibration_dialog.py`)
  * Dependencies:
    * `Logger` from `utils/logger.py`
    * `ImageManager` from `controllers/image_manager.py`

* **KeyPointSelectionDialog** (`views/dialogs/key_point_selection_dialog.py`)
  * Dependencies:
    * `Logger` from `utils/logger.py`

## 3. Unused and Duplicate Files

### 3.1. Backup Files (Unused)

The following backup files exist for reference but are not actually used and can be deleted:

1. `views/tabs/calibration_tab.py.backup`
   * Backup file for the original calibration tab, now refactored into a folder structure.

2. `views/dialogs/court_calibration_dialog_backup.py`
   * Backup file for the court calibration dialog.

3. `views/dialogs/court_calibration_dialog.py.bak`
   * Another backup file for the court calibration dialog.

4. `views/dialogs/key_point_selection_dialog.py.bak`
   * Backup file for the key point selection dialog.

### 3.2. Import Path Issues

In some files, import paths are written incorrectly, such as `core.*` or `utils.*`. These should be corrected and standardized to the `tennis_tracker.src.*` format:

1. `views/dialogs/camera_calibration_dialog.py`
2. `views/dialogs/court_calibration_dialog.py`
3. `views/dialogs/court_calibration_dialog_backup.py`
4. `views/dialogs/folder_selection_dialog.py`
5. `views/dialogs/key_point_selection_dialog.py`

### 3.3. Unimplemented or Empty Files

The `controllers/tennis_court_detection/court_detector.py` file contains only a basic class structure, and the actual functionality has not yet been implemented.

## 4. Improvement Suggestions

### 4.1. Standardize Import Paths

All import paths should be standardized to the `tennis_tracker.src.*` format to maintain consistency.

### 4.2. Remove Unnecessary Backup Files

After development is complete, it is recommended to remove unnecessary backup files to keep the codebase clean.

### 4.3. Improve Code Documentation

Some classes and functions lack documentation. In particular, the `CourtDetector` class in the `tennis_court_detection` package needs to be implemented and properly documented.

### 4.4. Add Tests

Adding unit and integration tests to the project is recommended to enhance code stability.

## 5. Conclusion

The Tennis Tracker project is generally well-structured and follows the MVC architecture. Key areas for improvement include standardizing import paths, removing unnecessary backup files, completing the implementation of the `CourtDetector` class, and adding tests. 