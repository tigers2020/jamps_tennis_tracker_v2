# Tennis Ball Tracker

A Python application for tracking tennis balls in video feeds using computer vision techniques.

## Project Structure

```
tennis_tracker/
├── run.py                 # Main entry point
├── src/                   # Source code
│   ├── controllers/       # Controller logic
│   │   ├── frame_manager.py
│   │   ├── image_manager.py
│   │   └── tennis_court_detection/
│   ├── models/            # Data models
│   │   ├── app_state.py
│   │   ├── image_cache.py
│   │   └── singleton.py
│   ├── views/             # UI/GUI related files
│   │   ├── app.py
│   │   ├── main_window.py
│   │   ├── dialogs/       # Dialog windows
│   │   ├── tabs/          # Tab components
│   │   ├── widgets/       # Reusable UI widgets
│   │   └── ui/            # Qt Designer UI files
│   ├── utils/             # Utility functions
│   │   ├── config.py
│   │   ├── file_utils.py
│   │   ├── logger.py
│   │   └── settings_manager.py
│   └── resources/         # Resource files
│       ├── images/
│       └── styles/
├── tests/                 # Test files
├── docs/                  # Documentation
└── requirements.txt       # Dependencies
```

## Getting Started

### Prerequisites

- Python 3.7+
- PySide6
- OpenCV
- NumPy

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/tennis-ball-tracker.git
   cd tennis-ball-tracker
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

Run the application using:

```
python run.py
```

## Features

- Tennis court detection and calibration
- Ball tracking and trajectory analysis
- Real-time video processing
- Playback and analysis tools
- Configuration and settings management

## Development

The project follows the MVC (Model-View-Controller) architecture:

- **Models**: Data structures and business logic
- **Views**: User interface components
- **Controllers**: Connects models and views, handles user interactions

## License

This project is licensed under the MIT License - see the LICENSE file for details. 