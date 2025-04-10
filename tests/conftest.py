"""
Pytest configuration file with fixtures for testing the Tennis Ball Tracker application.
"""

import os
import sys
import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ensure Qt singleton classes don't cause test failures
@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the whole test session"""
    # Prevent QtWebEngineProcess from using a GPU process
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
    # Use software OpenGL rendering instead of hardware acceleration
    os.environ["QT_OPENGL"] = "software"
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Allow testing of keyboard and mouse inputs by ignoring platform checks
    app.setAttribute(Qt.AA_DontUseNativeDialogs)
    
    yield app
    
@pytest.fixture
def temp_dir(tmpdir):
    """Create a temporary directory for tests"""
    return tmpdir

@pytest.fixture
def sample_image_path():
    """Path to a sample image for testing"""
    return os.path.join(str(project_root), "tests", "images", "sample.jpg")

@pytest.fixture
def temp_json_file(tmpdir):
    """Create a temporary JSON file for testing"""
    json_path = os.path.join(tmpdir, "test_config.json")
    with open(json_path, 'w') as f:
        f.write('{"test": "data"}')
    return json_path 