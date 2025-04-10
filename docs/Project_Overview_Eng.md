# Tennis Ball Animation Display System

## 1. Project Overview

This project is a system that displays pre-rendered tennis ball animation images. The client loads pre-rendered images from disk and displays them in sequence, providing smooth playback control and analysis capabilities.

## 2. System Architecture

### 2.1 Overall System Structure
```
+----------------+       +----------------+       +----------------+
|                |       |                |       |                |
|    Client      | <===> | File System    | <===> |  Image Storage |
|                |       |                |       |                |
+----------------+       +----------------+       +----------------+
       |                                                 |
       v                                                 v
+----------------+                               +----------------+
|                |                               |                |
|   UI Display   |                               | Image Cache    |
|                |                               |                |
+----------------+                               +----------------+
       |                                                 |
       v                                                 v
+----------------+                               +----------------+
|                |                               |                |
|  FPGA Analysis |                               | Image Loading  |
|                |                               |                |
+----------------+                               +----------------+
```

### 2.2 Client Components
- **Image Management Module**: Loading and caching pre-rendered images
- **File System Module**: Managing image file access and organization
- **UI Module**: Displaying images and user interface
- **Validation Module**: Image data validity verification
- **Speed Processing Module**: Frame rate control and playback speed adjustment
- **Replay Module**: Animation playback control functionality

### 2.3 Storage Components
- **Image Storage**: Organized directory structure for pre-rendered images
- **Cache Management**: Efficient image caching system
- **File Organization**: Structured storage of animation sequences
- **Image Loading**: Optimized image loading and memory management

## 3. File I/O and Data Processing

### 3.1 Coordinate Data Processing Flow
```
+-------------+     +--------------+     +---------------+     +----------------+     +---------------+
|             |     |              |     |               |     |                |     |               |
| File Loading| --> |Data Validation| --> |Speed-based    | --> |Coordinate System| --> |Data Serialization|
| (serve*.dat)|     |(Format/Structure)|  |Coordinate Sampling|  |Conversion (xzy→xyz)| |   (Binary)   |
|             |     |              |     |               |     |                |     |               |
+-------------+     +--------------+     +---------------+     +----------------+     +---------------+
```

### 3.2 Coordinate Conversion Process
```
Input (xzy format)                Output (xyz format)
+---+---+---+                   +---+---+---+
| x | z | y |         ->        | x | y | z |
+---+---+---+                   +---+---+---+
```

### 3.3 Data Format Documentation
- **Coordinate Data**: Tuple format consisting of three floating-point values (x, y, z)
- **Speed Parameter**: Integer value between 1 and 500
- **File Structure**: Array of consecutive coordinate values stored in binary format

### 3.4 Duplicate Data Transmission Prevention Strategy
- **Speed-based Data Sampling**: Selectively transmitting coordinate data based on speed value from the client
- **Delta Compression**: Minimizing data duplication by transmitting only the difference values between consecutive coordinates
- **Keyframe-based Transmission**: Transmitting complete coordinates only at major change points, only differences for intermediate values
- **Data Caching**: Preventing duplicate requests by caching previously transmitted data on the server side
- **Hash-based Verification**: Reusing already transmitted data by comparing hash values of coordinate data

### 3.5 Replay Data Management
- **Timestamp-based JSON Storage**: Storing in JSON format by adding timestamps to each coordinate
- **Playback Control**: Implementing animation playback, pause, and rewind functionality by loading saved JSON files
- **Sampling Metadata**: Enabling accurate reproduction by storing the speed value and sampling method used
- **Example Storage Format**:
```json
{
  "animation_type": "serve1",
  "speed": 50,
  "coordinates": [
    {"timestamp": 0, "position": [1.2, 3.4, 5.6]},
    {"timestamp": 50, "position": [1.3, 3.5, 5.7]},
    {"timestamp": 100, "position": [1.4, 3.6, 5.8]}
  ]
}
```

## 4. Network Protocol Design

### 4.1 Data Flow Diagram
```
+-------------+                               +----------------+
|   Client    |                               | Blender Server |
+-------------+                               +----------------+
      |                                               |
      | 1. Sending coordinate data sampled based on speed value |
      |---------------------------------------------->|
      |                                               |
      |                                               | 2. Animation Generation
      |                                               |-------------+
      |                                               |             |
      |                                               |<------------+
      |                                               |
      |                                               | 3. Rendering Process
      |                                               |-------------+
      |                                               |             |
      |                                               |<------------+
      |                                               |
      | 4. Returning image data (chunk-based transmission) |
      |<----------------------------------------------|
      |                                               |
      | 5. ACK/NACK Response                         |
      |---------------------------------------------->|
      |                                               |
```

### 4.2 Binary Data Structure
```
+----------------+----------------+----------------+----------------+----------------+
|                |                |                |                |                |
| Packet Header  | Packet Type    | Data Length    | Data           | Checksum       |
|    (8B)        |    (1B)        |    (4B)        | (Variable)     |    (4B)        |
|                |                |                |                |                |
+----------------+----------------+----------------+----------------+----------------+
```

### 4.3 Reliability Assurance Mechanism
- **ACK/NACK Protocol**: Ensuring reliability by implementing responses for all requests
- **Retransmission Logic**: Automatic retransmission if no response is received within a certain time
- **Session Management**: Tracking communication status through session IDs between client and server

### 4.4 Initial Connection Optimization
- **Handshake Process**: Setting up sessions with minimal data exchange during client-server connection
```
+-------------+                               +----------------+
|   Client    |                               | Blender Server |
+-------------+                               +----------------+
      |                                               |
      | 1. Connection Request (Client version, data file info) |
      |---------------------------------------------->|
      |                                               |
      | 2. Connection Response (Server version, supported parameters) |
      |<----------------------------------------------|
      |                                               |
      | 3. Metadata Exchange (Coordinate range, data format) |
      |---------------------------------------------->|
      |                                               |
      | 4. Return of Session ID and initial settings  |
      |<----------------------------------------------|
      |                                               |
```

- **Preliminary Metadata Transmission**: Initially transmitting meta-information such as total dat file size, max/min coordinate values, number of coordinates
- **Server-Client Compatibility Verification**: Early detection of compatibility issues through version information exchange
- **Preliminary Resource Allocation**: Minimizing processing delays by pre-allocating memory and resources based on metadata

## 5. Speed Parameter Processing

### 5.1 Client-side Speed Processing Flow
```
+------------------+     +-------------------+     +-------------------+
|                  |     |                   |     |                   |
| Speed Input and  | --> | Data Index        | --> | Coordinate Data   |
| Validation       |     | Calculation       |     | Sampling          |
| (Range: 1-500)   |     | (index += speed)  |     | (Send only selected)|
|                  |     |                   |     |                   |
+------------------+     +-------------------+     +-------------------+
```

### 5.2 Data Sampling Strategy Based on Speed
- **Low Speed (1-100)**: High-density sampling, high animation accuracy (sampling every 1-100 frames)
- **Medium Speed (101-300)**: Medium-density sampling, balanced performance and quality (sampling every 101-300 frames)
- **High Speed (301-500)**: Low-density sampling, maximum performance priority (sampling every 301-500 frames)

### 5.3 Network Transmission Optimization
```
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
| Original          | --> | Speed-based       | --> | Optimized Data    |
| Coordinate Data   |     | Sampling          |     | Transmission      |
| (All frames)      |     | (Selected frames) |     | (Reduced by up to 1/500) |
|                   |     |                   |     |                   |
+-------------------+     +-------------------+     +-------------------+
```

- **Transmission Reduction Effect**: Larger speed values reduce the amount of data transmitted
- **Bandwidth Efficiency**: Increasing network efficiency by selectively transmitting only necessary coordinate data
- **Improved Real-time Performance**: Minimizing transmission delays by reducing data transmission volume

### 5.4 Speed Parameter UI Design
```
+-------------------------------------------------------------+
|                                                             |
|  Speed Adjustment                                           |
|  +-----------------------------------------------------+    |
|  |                                                     |    |
|  |  [Slow] 1 [-----+------------------------] 500 [Fast] |    |
|  |        ↑                                            |    |
|  |      Current Value: 75                              |    |
|  |                                                     |    |
|  +-----------------------------------------------------+    |
|                                                             |
|  Presets: [Low Quality/High Speed] [Balanced] [High Quality/Low Speed] |
|                                                             |
|  +-----------------------------------------------------+    |
|  |                                                     |    |
|  |  [ ] Auto Speed Adjustment (Based on network conditions) |    |
|  |                                                     |    |
|  +-----------------------------------------------------+    |
|                                                             |
+-------------------------------------------------------------+
```

- **Slider Interface**: Providing an intuitive slider UI for adjusting speed values
- **Preset Buttons**: Offering preset values tailored to common usage scenarios
- **Current Value Display**: Real-time display of the currently set speed value
- **Performance Metrics Visualization**: Visualizing the tradeoff between network efficiency and animation quality for the set speed

## 6. Image Loading and Display Implementation

### 6.1 Image Loading Process Flow
```
+----------------+    +-------------------+     +----------------+
|                |    |                   |     |                |
| Image          | --> | Cache            | --> | Display       |
| Loading        |    | Management       |     | Output        |
|                |    |                   |     |                |
+----------------+    +-------------------+     +----------------+
```

### 6.2 Image Cache Management
```
                               +-----------------+
                               |                 |
           +------------------ | Image Cache     | <-----------------+
           |                   |                 |                    |
           |                   +-----------------+                    |
           |                                                         |
           v                                                         |
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| Memory Cache     |     | Disk Cache       |     | Preload         |
|                  |     |                  |     | Queue           |
+------------------+     +------------------+     +------------------+
           |                      |                        |
           v                      v                        v
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| Image Loading    |     | Image Loading    |     | Image Loading   |
| Process          |     | Process          |     | Process         |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
```

## 7. Image Processing and Display

### 7.1 Image Loading Process
```
+----------------+     +----------------+     +----------------+     +----------------+
|                |     |                |     |                |     |                |
| Image File     | --> | Image          | --> | Cache          | --> | Display       |
| Access         |     | Loading        |     | Management     |     | Queue         |
+----------------+     +----------------+     +----------------+     +----------------+
                                                                            |
+----------------+     +----------------+     +----------------+            |
|                |     |                |     |                |            |
| Screen Display | <-- | Image          | <-- | Cache         | <-----------+
|                |     | Processing     |     | Retrieval     |
+----------------+     +----------------+     +----------------+
```

### 7.2 Cache Management Strategy
- **Cache Size**: Configurable based on available system memory
- **Loading Method**: Progressive loading with priority-based caching
- **Progress Tracking**: Real-time monitoring of cache status and loading progress

## 8. Asynchronous Processing and Background Threads

### 8.1 Asynchronous Event Processing Model
```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
| Client Request   | --> | Event Loop       | --> | Async Handler    |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                                |
                                | Parallel Processing
                                v
       +------------------+     +------------------+
       |                  |     |                  |
       | Network I/O      |     | Rendering Thread |
       |                  |     | Pool             |
       +------------------+     +------------------+
```

### 8.2 Concurrency Model
- **Event Loop**: Asynchronous processing of network communications and client requests
- **Thread Pool**: Parallel processing of CPU-intensive rendering tasks
- **Task Queue**: Priority-based rendering task scheduling

## 9. Error Handling and Exception Preparation

### 9.1 Exception Handling Layer Structure
```
                  +------------------+
                  |                  |
                  | Base Exception   |
                  | Class            |
                  +------------------+
                           |
         +----------------+----------------+----------------+
         |                |                |                |
+------------------+ +----------------+ +----------------+ +----------------+
|                  | |                | |                | |                |
| Network Exception| | Data Validation| | Rendering      | | System         |
|                  | | Exception      | | Exception      | | Exception      |
+------------------+ +----------------+ +----------------+ +----------------+
```

### 9.2 Error Recovery Strategy
- **Automatic Retry**: Exponential backoff retry for temporary errors with maximum retry count specified
- **Alternative Logic**: Using default values or alternative data in case of data corruption
- **Graceful Shutdown**: Safe termination after resource cleanup in case of unrecoverable errors

## 10. Performance Optimization and Testing

### 10.1 Performance Optimization Strategy
```
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
| Memory Usage      | --> | Algorithm         | --> | System Load       |
| Optimization      |     | Efficiency        |     | Distribution      |
|                   |     |                   |     |                   |
+-------------------+     +-------------------+     +-------------------+
        |                         |                          |
        v                         v                          v
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
| Streaming         |     | Caching           |     | Parallel          |
| Processing        |     | Mechanism         |     | Processing        |
|                   |     |                   |     |                   |
+-------------------+     +-------------------+     +-------------------+
```

### 10.2 Testing Framework
- **Unit Testing**: Verification of module-specific functionality
- **Integration Testing**: Verification of overall system operation
- **Load Testing**: Simulation of multi-client and high-volume data processing scenarios
- **Automated Pipeline**: Automatic test execution in CI/CD environments

### 10.3 Implementation Example Code
**Client-side Speed-based Sampling (Python):**
```python
import json
import time
import numpy as np

def load_dat_file(file_path):
    """Load coordinate data from dat file"""
    coordinates = []
    with open(file_path, 'r') as f:
        for line in f:
            x, z, y = map(float, line.strip().split())
            coordinates.append((x, y, z))  # xzy -> xyz conversion
    return coordinates

def sample_coordinates(coordinates, speed):
    """Sample coordinates based on speed value"""
    if speed < 1:
        speed = 1
    elif speed > 500:
        speed = 500
        
    # Sample by skipping indices according to speed value
    sampled = []
    for i in range(0, len(coordinates), speed):
        sampled.append(coordinates[i])
    
    log.debug("Original coordinates: {}, Sampled: {} (reduction: {:.2f}%)".format(
        len(coordinates), len(sampled), 100 - (len(sampled) / len(coordinates) * 100)))
    return sampled

def save_replay_data(coordinates, speed, animation_type):
    """Save JSON for replay"""
    replay_data = {
        "animation_type": animation_type,
        "speed": speed,
        "coordinates": []
    }
    
    for i, pos in enumerate(coordinates):
        replay_data["coordinates"].append({
            "timestamp": i * speed,
            "position": list(pos)
        })
    
    filename = f"replay_{animation_type}_{speed}_{int(time.time())}.json"
    with open(filename, 'w') as f:
        json.dump(replay_data, f, indent=2)
    
    log.debug(f"Saved replay data to {filename}")
    return filename

def main():
    # Configuration
    file_path = "datFiles/serve1.dat"
    speed = 50  # Value between 1-500
    
    # Load and sample coordinates
    log.debug("Loading coordinates from {}".format(file_path))
    coordinates = load_dat_file(file_path)
    sampled_coords = sample_coordinates(coordinates, speed)
    
    # Save replay data
    save_replay_data(sampled_coords, speed, "serve1")
    
    # Prepare for server transmission (binary serialization)
    binary_data = bytearray()
    for x, y, z in sampled_coords:
        # Add each coordinate converted to 32-bit float to binary data
        binary_data.extend(np.float32(x).tobytes())
        binary_data.extend(np.float32(y).tobytes())
        binary_data.extend(np.float32(z).tobytes())
    
    log.debug(f"Binary data size: {len(binary_data)} bytes")
    # Here, binary_data would be transmitted to the server
    
if __name__ == "__main__":
    main()
```

## 11. Tennis Match Analysis and Visualization System

### 11.1 Analysis System Architecture
```
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
| Image Display     | --> | FPGA Image        | --> | In/Out Judgment   |
| Screen            |     | Analysis          |     | Results           |
|                   |     |                   |     |                   |
+-------------------+     +-------------------+     +-------------------+
         |                        |                          |
         v                        v                          v
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
| Real-time Replay  |     | Court Line        |     | Judgment Data     |
|                   |     | Detection         |     | Storage           |
|                   |     | Ball position     |     |                   |
|                   |     | indicator         |     |                   |
+-------------------+     +-------------------+     +-------------------+
```

### 11.2 FPGA Image Analysis Process
```
Input Image
    |
    v
+---------------+     +---------------+     +---------------+
|               |     |               |     |               |
| Preprocessing | --> | Feature       | --> | Object        |
| Stage         |     | Extraction    |     | Detection     |
|               |     |               |     |               |
+---------------+     +---------------+     +---------------+
                                                   |
                                                   v
+---------------+     +---------------+     +---------------+
|               |     |               |     |               |
| Display       | <-- | In/Out        | <-- | Position      |
| Judgment      |     | Judgment      |     | Analysis      |
| Results       |     |               |     |               |
+---------------+     +---------------+     +---------------+
```

### 11.3 Camera Control and Replay System
```
+-----------------+     +-----------------+     +-----------------+
|                 |     |                 |     |                 |
| Azimuth Slider  | --> | Camera Position | --> | Viewpoint       |
|                 |     | Calculation     |     | Update          |
+-----------------+     +-----------------+     +-----------------+
        |
        |        +-----------------+     +-----------------+
        |        |                 |     |                 |
        +------> | Elevation Slider| --> | Spherical       |
                 |                 |     | Coordinate      |
                 +-----------------+     | Conversion      |
                        |                +-----------------+
                        |        +-----------------+
                        |        |                 |
                        +------> | Distance Slider |
                                 |                 |
                                 +-----------------+
```

### 11.4 UI Layout
```
+-------------------------------------------------------+
|                                                       |
|  +------------------------+  +---------------------+  |
|  |                        |  |                     |  |
|  |                        |  |                     |  |
|  |                        |  |                     |  |
|  | Blender Rendering View |  | FPGA Analysis View  |  |
|  |                        |  |                     |  |
|  |                        |  |                     |  |
|  |                        |  |                     |  |
|  +------------------------+  +---------------------+  |
|                                                       |
|  +------------------------+  +---------------------+  |
|  | Replay Controls        |  | Camera Controls     |  |
|  | [◀] [▶] [∥] [◼]       |  | Azimuth: [-------●-]|  |
|  | Time: [-----●---]      |  | Elevation:[----●----]|  |
|  |                        |  | Distance:[---●-----] |  |
|  +------------------------+  +---------------------+  |
|                                                       |
+-------------------------------------------------------+
```

## 12. Future Improvements and Expansion Plans

### 12.1 Feature Expansion Roadmap
```
Current                                                                     Future
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
| Basic Rendering   | --> | Admin Dashboard   | --> | Distributed       |
| System            |     |                   |     | Rendering System  |
|                   |     |                   |     |                   |
+-------------------+     +-------------------+     +-------------------+
                                    |
                                    v
                          +-------------------+     +-------------------+
                          |                   |     |                   |
                          | Real-time         | --> | Cloud             |
                          | Parameter         |     | Integration       |
                          | Adjustment        |     |                   |
                          +-------------------+     +-------------------+
```

### 12.2 Scalability Enhancement Methods
- **Microservice Architecture**: Transition to a modular structure that can be independently scaled
- **Containerization**: Deployment and scaling utilizing Docker and Kubernetes
- **API Gateway**: Service access management through a centralized interface

## 13. Conclusion

This project is an efficient system that combines optimized image loading and caching with multi-threaded display to provide smooth playback of pre-rendered tennis ball animations. It minimizes memory usage through intelligent caching strategies and provides a stable and scalable display pipeline through phased implementation methods, performance optimization, and error handling mechanisms.


1. Core Tracking & Analysis Engine:
- Human-Machine Interface(HMI) & Visualization suite
- Temporal Event Review & Playback Module (Instant Replay)
- Serve Volley Trajectory Analysis & Boundary Adjudication
2. Stereo Camera System Calibration & Parameterization
3. Static Environment 3D Localization Accuracy Assement
6. Real-time Event-Driven Visual Feedback System (LED Indicators)
