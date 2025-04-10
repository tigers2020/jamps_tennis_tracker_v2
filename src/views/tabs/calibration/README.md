# Tennis Court Calibration Module

This module provides functionality for calibrating the tennis court by selecting key points in camera images.

## Structure

The calibration module has been refactored according to the Single Responsibility Principle, with components separated by functionality:

- `calibration_tab.py`: Main UI tab component that integrates all functionality
- `point_manager.py`: Core point management and processing logic
- `point_io.py`: File I/O operations for saving/loading calibration points
- `image_utils.py`: Image processing utilities (coordinate conversions and rendering)

## Component Roles

### CalibrationTab

The main UI component that:
- Handles user interface setup and event management
- Integrates the point manager, I/O, and rendering components
- Responds to user interactions (mouse clicks, drags, key presses)
- Displays status information and manages UI state

### CalibrationPointManager

Responsible for:
- Managing point data for both left and right cameras
- Tracking the active camera and selected point state
- Processing and organizing points using clustering algorithms
- Applying alignments and optimizations to improve point quality
- Signaling when point data changes

### CalibrationPointIO

Handles file operations:
- Saving point data to JSON files
- Loading point data from JSON files
- Creating directories for storage
- Providing feedback on operation results

### Image Utilities

Contains pure functions for:
- Converting between screen and original image coordinates
- Rendering points and lines on images with proper styling

## Improvements

This refactoring provides several benefits:
1. **Separation of concerns**: UI, data management, and I/O are decoupled
2. **Improved maintainability**: Each component has a focused responsibility
3. **Better testability**: Components can be tested in isolation
4. **Reduced complexity**: Each file is smaller and more focused
5. **Code reuse**: Utilities can be shared with other parts of the application
6. **Type safety**: All components use proper type hints
7. **Consistent error handling**: Clear patterns for handling errors and providing feedback

## Usage

The API remains backward compatible. The main `CalibrationTab` class can be imported and used exactly as before:

```python
from tennis_tracker.src.gui.tabs import CalibrationTab

# Create and use the calibration tab as before
tab = CalibrationTab()
``` 