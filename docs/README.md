# Tennis Ball Animation Rendering System

## Project Overview

This project is a system that renders tennis ball animations in real-time through communication between the client and the Blender server. The client sends animation coordinate data to the server, and the server processes it to return 3D rendered images.

## Necessary Conditions

- Python 2.7
- Blender
- Necessary Python packages (see requirements.txt)

## Installation Method

1. Clone the project:
```bash
git clone https://github.com/yourusername/tennis-ball-animation.git
cd tennis-ball-animation
```

2. Set up Conda environment:
```bash
conda create -n Final_Project python=2.7
conda activate Final_Project
```

3. Install necessary packages:
```bash
pip install -r requirements.txt
```

4. Modify configuration files:
   - Modify `config/client_config.py` and `config/server_config.py` as needed

## Usage

### Server Execution

```bash
conda activate Final_Project
python server/main.py
```

### Client Execution

```bash
conda activate Final_Project
python client/main.py
```

## Main Features

- Coordinate data sampling based on speed parameters
- Real-time 3D rendering
- Rendering result transmission based on chunk
- Animation recording and playback
- FPGA image analysis and in/out determination

## Project Structure

For detailed project structure and module descriptions, refer to the `docs/` directory.

## Developer Information

This project was developed as a final project. 