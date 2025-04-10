Serialized Binary Command Examples. 


# Tennis Animation Control Protocol Specification

## Overview
This document defines a set of serialized binary commands for the Tennis Match Analysis and Visualization System. These commands facilitate communication between the client, Blender server, and FPGA-based analysis hardware. The protocol adheres to the binary data structure outlined in Section 4.2 of the Blender-based Tennis Ball Animation Rendering System.

## Binary Data Structure
Each command follows this format:
- Packet Header (8 bytes): Fixed identifier "Tennis\0\0".
- Packet Type (1 byte): Command identifier (3-bit values: 001, 010, 011, 100).
- Data Length (4 bytes): Length of the variable data field in bytes (little-endian).
- Data (Variable): Command-specific payload.
- Checksum (4 bytes): CRC32 or similar integrity check (placeholder: XX XX XX XX).

All multi-byte values use little-endian byte order.

---

## Command Definitions

### 1. Determine the Court Out Liners
**Purpose**: Requests the system (e.g., FPGA) to analyze and determine the court's out-of-bounds lines for in/out judgment, supporting Section 11.2 (FPGA Image Analysis Process).

**Packet Type**: 0x01 (Binary: 001)

**Data**:
- Session ID (4 bytes): Unique identifier linking to the current analysis session.
- Court ID (2 bytes): Identifies the court layout (e.g., 0x0001 for singles, 0x0002 for doubles).

**Total Size**: 23 bytes
- Header: 8 bytes
- Type: 1 byte
- Length: 4 bytes
- Data: 6 bytes
- Checksum: 4 bytes

**Example**
Packet: 54 65 6E 6E 69 73 00 00 01 06 00 00 00 01 00 00 00 01 00 XX XX XX XX
Breakdown:

Header: "Tennis\0\0" = 54 65 6E 6E 69 73 00 00
Type: 0x01
Length: 6 bytes = 06 00 00 00
Data:
Session ID: 1 = 01 00 00 00
Court ID: 1 (singles) = 01 00
Checksum: XX XX XX XX (placeholder)

-------------------------------------------------------------------------------------------------------------------### 2. Tracking the Ball Coordinate
**Purpose**: Instructs the system to track and report the tennis ball's current (x, y, z) coordinate, supporting real-time replay and position analysis in Section 11.1.

**Packet Type**: 0x02 (Binary: 010)

**Data**:
- Session ID (4 bytes): Unique identifier linking to the current tracking session.
- Timestamp (4 bytes): Time of the request in milliseconds.

**Total Size**: 25 bytes
- Header: 8 bytes
- Type: 1 byte
- Length: 4 bytes
- Data: 8 bytes
- Checksum: 4 bytes

**Example
Packet: 54 65 6E 6E 69 73 00 00 02 08 00 00 00 01 00 00 00 64 00 00 00 XX XX XX XX
Breakdown:

Header: "Tennis\0\0" = 54 65 6E 6E 69 73 00 00
Type: 0x02
Length: 8 bytes = 08 00 00 00
Data:
Session ID: 1 = 01 00 00 00
Timestamp: 100 ms = 64 00 00 00
Checksum: XX XX XX XX (placeholder)

-------------------------------------------------------------------------------------------------------------------


### 3. LED Indicate
**Purpose**: Controls an LED indicator on hardware (e.g., FPGA) to signal events like an out-of-bounds call or tracking status, enhancing visualization per Section 11.

**Packet Type**: 0x03 (Binary: 011)

**Data**:
- Session ID (4 bytes): Unique identifier linking to the current session.
- LED State (1 byte): 0x00 (off), 0x01 (on), 0x02 (blink).
- LED ID (1 byte): Identifies the LED (e.g., 0x01 for out, 0x02 for in).

**Total Size**: 23 bytes
- Header: 8 bytes
- Type: 1 byte
- Length: 4 bytes
- Data: 6 bytes
- Checksum: 4 bytes

**Example**

Packet: 54 65 6E 6E 69 73 00 00 03 06 00 00 00 01 00 00 00 01 01 XX XX XX XX
Breakdown:

Header: "Tennis\0\0" = 54 65 6E 6E 69 73 00 00
Type: 0x03
Length: 6 bytes = 06 00 00 00
Data:
Session ID: 1 = 01 00 00 00
LED State: On = 01
LED ID: 1 (out indicator) = 01
Checksum: XX XX XX XX (placeholder)

-------------------------------------------------------------------------------------------------------------------

### 4. ETCS (Error Tracking and Control System)
**Purpose**: Reports errors or queries system status, supporting error handling mechanisms in Section 9.

**Packet Type**: 0x04 (Binary: 100)

**Data**:
- Session ID (4 bytes): Unique identifier linking to the current session.
- Error Code (2 bytes): Identifies the error (e.g., 0x0001 for network error).
- Status Flag (1 byte): 0x00 (query status), 0x01 (report error).

**Total Size**: 24 bytes
- Header: 8 bytes
- Type: 1 byte
- Length: 4 bytes
- Data: 7 bytes
- Checksum: 4 bytes

**Example**
Packet: 54 65 6E 6E 69 73 00 00 04 07 00 00 00 01 00 00 00 01 00 01 XX XX XX XX
Breakdown:

Header: "Tennis\0\0" = 54 65 6E 6E 69 73 00 00
Type: 0x04
Length: 7 bytes = 07 00 00 00
Data:
Session ID: 1 = 01 00 00 00
Error Code: 1 (network error) = 01 00
Status Flag: Report = 01
Checksum: XX XX XX XX (placeholder)

-------------------------------------------------------------------------------------------------------------------

### 5. Initial Handshake Request (Client → Server)
**Purpose**: Initiates a connection between the client and server, exchanging metadata such as client version and data file information, per Section 4.4 (Initial Connection Optimization).

**Packet Type**: 0x05 (Binary: 101)

**Data**:
- Client Version (2 bytes): Version number (e.g., 0x0100 for v1.0).
- Data File Info (8 bytes): Size of the coordinate data file in bytes.
- Number of Coordinates (4 bytes): Total number of coordinates in the file.

**Total Size**: 31 bytes
- Header: 8 bytes
- Type: 1 byte
- Length: 4 bytes
- Data: 14 bytes
- Checksum: 4 bytes

**Example**
Packet: 48 65 6C 6C 6F 00 00 00 05 0E 00 00 00 00 01 00 00 00 10 00 00 00 64 00 00 00 XX XX XX XX
Breakdown:

Header: "Hello\0\0\0" = 48 65 6C 6C 6F 00 00 00
Type: 0x05
Length: 14 bytes = 0E 00 00 00
Data:
Client Version: 1.0 = 00 01
File Size: 1MB = 00 00 10 00
Num Coords: 100 = 64 00 00 00
Checksum: XX XX XX XX (placeholder)

-------------------------------------------------------------------------------------------------------------------

### 6. Initial Handshake Response (Server → Client)
**Purpose**: Confirms the connection, providing server version, session ID, and supported parameters, per Section 4.4.

**Packet Type**: 0x06 (Binary: 110)

**Data**:
- Server Version (2 bytes): Version number (e.g., 0x0101 for v1.1).
- Session ID (4 bytes): Unique identifier for the session.
- Supported Speed Range (4 bytes): Maximum speed value (e.g., 500).

**Total Size**: 27 bytes
- Header: 8 bytes
- Type: 1 byte
- Length: 4 bytes
- Data: 10 bytes
- Checksum: 4 bytes

**Example**
Packet: 53 65 72 76 65 72 00 00 06 0A 00 00 00 01 01 01 00 00 00 F4 01 00 00 XX XX XX XX
Breakdown:

Header: "Server\0\0" = 53 65 72 76 65 72 00 00
Type: 0x06
Length: 10 bytes = 0A 00 00 00
Data:
Server Version: 1.1 = 01 01
Session ID: 1 = 01 00 00 00
Max Speed: 500 = F4 01 00 00
Checksum: XX XX XX XX (placeholder)

-------------------------------------------------------------------------------------------------------------------

### 7. Coordinate Data Transmission (Client → Server)
**Purpose**: Transmits sampled coordinate data to the server for rendering, based on speed parameter, per Sections 3.1 (Coordinate Data Processing Flow) and 5.1 (Speed Processing Flow).

**Packet Type**: 0x07 (Binary: 111)

**Data**:
- Session ID (4 bytes): Links to the current session.
- Speed (4 bytes): Integer value between 1 and 500.
- Number of Coordinates (4 bytes): Count of coordinates in this packet.
- Coordinates (Variable): Array of (x, y, z) tuples, each 12 bytes (3 × 32-bit floats).

**Total Size**: 8 + 1 + 4 + 12 + (N × 12) + 4, where N is the number of coordinates
- Example with 2 coordinates: 8 + 1 + 4 + 12 + (2 × 12) + 4 = 53 bytes
Packet: 43 6F 6F 72 64 00 00 00 07 1C 00 00 00 01 00 00 00 32 00 00 00 02 00 00 00 00 00 80 3F 00 00 00 40 00 00 40 40 00 00 00 40 00 00 80 40 00 00 C0 40 XX XX XX XX
Breakdown:

Header: "Coord\0\0\0" = 43 6F 6F 72 64 00 00 00
Type: 0x07
Length: 28 bytes = 1C 00 00 00 (12 fixed + 2 × 12 coordinates)
Data:
Session ID: 1 = 01 00 00 00
Speed: 50 = 32 00 00 00
Num Coords: 2 = 02 00 00 00
Coord 1: (1.0, 2.0, 3.0) = 00 00 80 3F 00 00 00 40 00 00 40 40
Coord 2: (2.0, 3.0, 4.0) = 00 00 00 40 00 00 80 40 00 00 C0 40
Checksum: XX XX XX XX (placeholder)

-------------------------------------------------------------------------------------------------------------------

### 8. Render Request (Client → Server)
**Purpose**: Requests the server to render the latest coordinate data into a 3D image, per Section 6.1 (Rendering Process Flow).

**Packet Type**: 0x08 (Binary: 1000)

**Data**:
- Session ID (4 bytes): Links to the current session.
- Frame Number (4 bytes): Identifies the specific frame to render (optional).

**Total Size**: 25 bytes
- Header: 8 bytes
- Type: 1 byte
- Length: 4 bytes
- Data: 8 bytes
- Checksum: 4 bytes

**Example**
Packet: 52 65 6E 64 65 72 00 00 08 08 00 00 00 01 00 00 00 01 00 00 00 XX XX XX XX
Breakdown:

Header: "Render\0\0" = 52 65 6E 64 65 72 00 00
Type: 0x08
Length: 8 bytes = 08 00 00 00
Data:
Session ID: 1 = 01 00 00 00
Frame Number: 1 = 01 00 00 00
Checksum: XX XX XX XX (placeholder)

-------------------------------------------------------------------------------------------------------------------

### 9. Render Response (Server → Client)
**Purpose**: Returns a chunk of the rendered image data to the client, per Section 7.1 (Image Transmission Process).

**Packet Type**: 0x09 (Binary: 1001)

**Data**:
- Session ID (4 bytes): Links to the current session.
- Chunk Index (4 bytes): Index of the current chunk (starts at 0).
- Total Chunks (4 bytes): Total number of chunks for the image.
- Chunk Data (Variable): Image data chunk (e.g., 8 bytes in this example, up to 8KB max).

**Total Size**: 8 + 1 + 4 + 12 + (Chunk Size) + 4
- Example with 8-byte chunk: 8 + 1 + 4 + 12 + 8 + 4 = 37 bytes

**Example**
Packet: 49 6D 61 67 65 00 00 00 09 14 00 00 00 01 00 00 00 00 00 00 00 02 00 00 00 12 34 56 78 90 AB CD EF XX XX XX XX
Breakdown:

Header: "Image\0\0\0" = 49 6D 61 67 65 00 00 00
Type: 0x09
Length: 20 bytes = 14 00 00 00 (12 fixed + 8 chunk)
Data:
Session ID: 1 = 01 00 00 00
Chunk Index: 0 = 00 00 00 00
Total Chunks: 2 = 02 00 00 00
Chunk Data: (8 bytes) = 12 34 56 78 90 AB CD EF
Checksum: XX XX XX XX (placeholder)

-------------------------------------------------------------------------------------------------------------------

### 10. Replay Data Request (Client → Server)
**Purpose**: Requests the server to render animation data from a stored replay, per Section 3.5 (Replay Data Management).

**Packet Type**: 0x0A (Binary: 1010)

**Data**:
- Session ID (4 bytes): Links to the current session.
- Animation Type Length (4 bytes): Length of the animation type string.
- Animation Type (Variable): String identifier (e.g., "serve1").
- Speed (4 bytes): Playback speed (1-500).

**Total Size**: 8 + 1 + 4 + 12 + (String Length) + 4
- Example with "serve1" (6 bytes): 8 + 1 + 4 + 12 + 6 + 4 = 35 bytes

**Example**
Packet: 52 65 70 6C 61 79 00 00 0A 12 00 00 00 01 00 00 00 06 00 00 00 73 65 72 76 65 31 32 00 00 00 XX XX XX XX
Breakdown:

Header: "Replay\0\0" = 52 65 70 6C 61 79 00 00
Type: 0x0A
Length: 18 bytes = 12 00 00 00
Data:
Session ID: 1 = 01 00 00 00
Anim Type Length: 6 = 06 00 00 00
Animation Type: "serve1" = 73 65 72 76 65 31
Speed: 50 = 32 00 00 00
Checksum: XX XX XX XX (placeholder)


