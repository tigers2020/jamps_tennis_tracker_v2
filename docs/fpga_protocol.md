# FPGA Communication Protocol Documentation

## 1. Command Codes

| Code (Binary) | Code (Decimal) | Description                |
|---------------|----------------|--------------------------|
| 001           | 1              | Court Boundary Detection |
| 010           | 2              | Ball Coordinate Tracking |
| 011           | 3              | LED Display Control      |
| 100           | 4              | Other Functions          |
| 101           | 5              | Judgement Result Transfer|
| 111           | 7              | System Control           |

## 2. Status Flags

### 2.1 Court Boundary Detection Status (001)
| Flag (Binary) | Description               |
|---------------|---------------------------|
| 00000         | Normal Detection          |
| 00001         | Boundary Uncertain        |
| 00010         | Partial Detection         |
| 00011         | Recalibration Required    |
| 00100         | Lighting Issues           |
| 00101         | Noise Interference        |

### 2.2 Ball Tracking Status (010)
| Flag (Binary) | Description               |
|---------------|---------------------------|
| 00000         | Normal Tracking           |
| 00001         | Low Confidence            |
| 00010         | Tracking Uncertain        |
| 00011         | Tracking Failed           |
| 00100         | Multiple Objects Detected |
| 00101         | High-Speed Movement       |
| 00110         | Predicted Position Off-Screen |

### 2.3 LED Display Status (011)
| Flag (Binary) | Description               |
|---------------|---------------------------|
| 00000         | Normal Operation          |
| 00001         | Blinking Mode             |
| 00010         | Color Gradient Mode       |
| 00011         | Emergency Display Mode    |
| 00100         | Power Saving Mode         |
| 00101         | Sequence Mode             |

### 2.4 Judgement Result Status (101)
| Flag (Binary) | Description               |
|---------------|---------------------------|
| 00000         | Confirmed Judgement       |
| 00001         | Provisional Judgement     |
| 00010         | Challenge Possible        |
| 00011         | Unconfirmed Judgement     |
| 00100         | Judgement Under Review    |
| 11111         | System Judgement N/A      |

## 3. Packet Types
| Code (Binary) | Description           |
|---------------|-----------------------|
| 00            | Data Packet           |
| 01            | Control Packet        |
| 10            | Response Packet       |
| 11            | Urgent/Priority Packet|

## 4. Data Field Format

### 4.1 Court Boundary Data (8-bit Control + 16-bit Data)
```
[Control 8-bit] [Data 16-bit]
LLLL DDDD   XXXX XXXX YYYY YYYY

L: Line Type (0001: Baseline, 0010: Sideline, 0011: Service Line, 0100: Center Mark)
D: Detection Accuracy (0-15, 15 is most accurate)
X: X Coordinate Value (8-bit)
Y: Y Coordinate Value (8-bit)
```

### 4.2 Ball Tracking Data (8-bit Control + 16-bit Data)
```
[Control 8-bit] [Data 16-bit]
IIII VVVV   XXXX XXXX YYYY YYYY

I: Ball ID (Used for multiple ball tracking)
V: Speed Value (0-15)
X: X Coordinate Value (8-bit)
Y: Y Coordinate Value (8-bit)
```

### 4.3 LED Control Data (8-bit Control + 16-bit Data)
```
[Control 8-bit] [Data 16-bit]
GGGG BBBB   CCCC CCCC PPPP PPPP

G: LED Group ID
B: Brightness Value (0-15)
C: Color Code (8-bit RGB compressed)
P: Pattern Code (0: Fixed, 1-255: Various blinking patterns)
```

### 4.4 Judgement Result Data (8-bit Control + 16-bit Data)
```
[Control 8-bit] [Data 16-bit]
TTTT CCCC   DDDD DDDD DDDD DDDD

T: Judgement Type (0001: In/Out, 0010: Line Touch, 0011: Net, 0100: Foot Fault)
C: Confidence Category (0-15)
D: Detailed Judgement Data (Meaning varies by type)
```

## 5. Usage Examples

### 5.1 Normal Ball Tracking Data (Binary Representation)
```
010 00000 00 00010100 0110101000101101
│   │     │  │      │ └─────┬──────┘
│   │     │  │      │       └─ Y Coordinate: 45 (00101101)
│   │     │  │      └─ X Coordinate: 106 (01101010)
│   │     │  └─ Ball ID: 1, Speed: 4 (00010100)
│   │     └─ Data Packet
│   └─ Normal Tracking Status
└─ Ball Tracking Command
```

### 5.2 Boundary Detection Error (Binary Representation)
```
001 00100 00 00010001 0010111100000011
│   │     │  │      │ └─────┬──────┘
│   │     │  │      │       └─ Y Coordinate: 3 (00000011)
│   │     │  │      └─ X Coordinate: 47 (00101111)
│   │     │  └─ Line Type: Baseline, Accuracy: 1 (00010001)
│   │     └─ Data Packet
│   └─ Lighting Issue Status
└─ Court Boundary Detection Command
```

### 5.3 System Reset Command (Binary Representation)
```
111 00000 01 11111111 0000000000000000
│   │     │  │        └─ Parameter: 0 (Initialize all settings)
│   │     │  └─ Action Code: System Reset (11111111)
│   │     └─ Control Packet
│   └─ Normal Priority
└─ System Control Command
```

## 6. Error Handling Codes

| Command Code | Status Flag | Description            |
|--------------|-------------|------------------------|
| 000          | 11111       | Packet Error           |
| 110          | 00001       | Retransmission Request |
| 110          | 00010       | Timeout Occurred       |
| 110          | 00011       | Checksum Mismatch      |
| 110          | 11111       | Critical System Error  | 