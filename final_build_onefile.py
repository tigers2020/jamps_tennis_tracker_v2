import os
import sys
import shutil
from pathlib import Path

def ensure_directory_exists(directory):
    """Ensure directory exists, create if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    return directory

def main():
    """Build a single executable file with all resources embedded"""
    print("Starting Tennis Ball Tracker single file build process...")
    
    # Clean previous build directories
    print("Cleaning build directories...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Ensure all resource directories exist
    ensure_directory_exists("src/resources/images/icons")
    ensure_directory_exists("src/resources/tests/images")
    ensure_directory_exists("src/resources/tests")
    ensure_directory_exists("src/resources/models")
    ensure_directory_exists("src/resources/videos")
    ensure_directory_exists("tests/images")
    
    # Build command with only existing resources
    cmd = ["pyinstaller",
           "--clean",
           "--noconfirm",
           "--onefile",
           "--windowed",
           "--name", "TennisBallTracker",
           "--icon", "src/resources/images/icons/play.png"]
    
    # Add resources to the command, checking if they exist
    resources = []
    
    # Add icon files
    icons_dir = "src/resources/images/icons"
    if os.path.exists(icons_dir) and os.listdir(icons_dir):
        resources.append((icons_dir, "src/resources/images/icons"))
    
    # Add test images
    test_images_dir = "src/resources/tests/images"
    if os.path.exists(test_images_dir) and os.listdir(test_images_dir):
        resources.append((test_images_dir, "src/resources/tests/images"))
    
    # Add tests directory
    tests_dir = "src/resources/tests"
    if os.path.exists(tests_dir) and os.listdir(tests_dir):
        resources.append((tests_dir, "src/resources/tests"))
    
    # Add models directory
    models_dir = "src/resources/models"
    if os.path.exists(models_dir) and os.listdir(models_dir):
        resources.append((models_dir, "src/resources/models"))
    
    # Add videos directory (even if empty)
    videos_dir = "src/resources/videos"
    if os.path.exists(videos_dir):
        # Create a dummy file if directory is empty
        if not os.listdir(videos_dir):
            dummy_file = os.path.join(videos_dir, "README.txt")
            with open(dummy_file, "w") as f:
                f.write("Directory for video files")
            print(f"Created dummy file in empty directory: {videos_dir}")
        resources.append((videos_dir, "src/resources/videos"))
    
    # Add test images from tests directory
    tests_images_dir = "tests/images"
    if os.path.exists(tests_images_dir) and os.listdir(tests_images_dir):
        resources.append((tests_images_dir, "tests/images"))
    
    # Add planned features JSON
    planned_features = "src/resources/planned_features.json"
    if os.path.exists(planned_features):
        resources.append((planned_features, "src/resources"))
    
    # Add resources to PyInstaller command
    for src, dest in resources:
        add_data_param = f"{src};{dest}"
        cmd.extend(["--add-data", add_data_param])
        print(f"Adding resource: {add_data_param}")
    
    # Add main script
    cmd.append("run.py")
    
    # Convert command list to string
    cmd_str = " ".join(cmd)
    
    # Print the command
    print("\nExecuting build command:")
    print(cmd_str)
    
    # Execute the command
    result = os.system(cmd_str)
    
    # Check result
    if result == 0:
        print("\nBuild completed successfully!")
        print("Single executable file created: dist/TennisBallTracker.exe")
        
        # Verify the file exists
        if os.path.exists("dist/TennisBallTracker.exe"):
            size_mb = os.path.getsize("dist/TennisBallTracker.exe") / (1024 * 1024)
            print(f"File size: {size_mb:.2f} MB")
        else:
            print("ERROR: Executable file not found!")
    else:
        print(f"\nBuild failed with error code: {result}")
        print("Check the error messages above for details.")

if __name__ == "__main__":
    main() 