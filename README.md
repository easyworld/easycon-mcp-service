# EasyCon MCP Service

EasyCon MCP Service: HTTP/JSON API for Nintendo Switch control over EasyCon protocol via serial (USB/UART).

This service implements:
- Serial lifecycle: list ports, connect/disconnect, status
- EasyCon handshake: send [A5, A5, 81] and expect [80]
- Switch controls: buttons, D-Pad (HAT), sticks, and reset
- **NEW**: Combo buttons, sequences, macros, LED control, controller settings
- **NEW**: Batch operations, health monitoring
- Raw send/receive for debugging/extension

## Requirements

- Python 3.9+
- A serial device that speaks EasyCon protocol (115200 8N1)

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn mcp_service.server:app --host 0.0.0.0 --port 8000
```

## API Reference

### Connection Management
- **GET** `/ports` - List available serial ports
- **POST** `/connect` - Connect to serial port
- **POST** `/disconnect` - Disconnect from serial port
- **GET** `/status` - Get connection status
- **POST** `/init` - Initialize device (handshake)

### Basic Controls
- **POST** `/press/button` - Press a single button
- **POST** `/press/hat` - Press D-Pad direction
- **POST** `/stick` - Control analog sticks
- **POST** `/reset` - Send reset command

### Advanced Controls (NEW)
- **POST** `/press/combo` - Press multiple buttons simultaneously
- **POST** `/sequence` - Execute a sequence of actions with repeat
- **POST** `/batch` - Execute multiple commands in batch

### Macro System (NEW)
- **POST** `/macro/save` - Save a macro
- **GET** `/macro/list` - List all saved macros
- **GET** `/macro/{name}` - Get macro details
- **DELETE** `/macro/{name}` - Delete a macro
- **POST** `/macro/execute` - Execute a saved macro

### Device Control (NEW)
- **POST** `/led` - Control device LED (on/off)
- **GET** `/version` - Get firmware version
- **POST** `/controller/mode` - Change controller mode (Pro/JoyCon)
- **POST** `/controller/color` - Change controller color
- **POST** `/unpair` - Unpair controller from console

### Utilities
- **GET** `/health` - Health check endpoint
- **GET** `/buttons` - List all available buttons
- **GET** `/directions` - List all available HAT directions
- **POST** `/raw/send` - Send raw bytes

## Examples

### Basic Usage

```bash
# 1) List ports
curl http://localhost:8000/ports

# 2) Connect
curl -X POST http://localhost:8000/connect -H "Content-Type: application/json" \
     -d '{"port":"/dev/ttyUSB0","baud":115200}'

# 3) Handshake
curl -X POST http://localhost:8000/init

# 4) Press A for 50ms
curl -X POST http://localhost:8000/press/button -H "Content-Type: application/json" \
     -d '{"button":"A","durationMs":50}'

# 5) Reset
curl -X POST http://localhost:8000/reset

# 6) Disconnect
curl -X POST http://localhost:8000/disconnect
```

### Combo Buttons

```bash
# Press A+B simultaneously for 100ms
curl -X POST http://localhost:8000/press/combo -H "Content-Type: application/json" \
     -d '{"buttons":["A","B"],"durationMs":100}'

# Press L+R (screenshot combo)
curl -X POST http://localhost:8000/press/combo -H "Content-Type: application/json" \
     -d '{"buttons":["L","R"],"durationMs":50}'
```

### Sequences

```bash
# Execute a sequence: press A, wait, press B, repeat 3 times
curl -X POST http://localhost:8000/sequence -H "Content-Type: application/json" \
     -d '{
  "steps": [
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":100},
    {"type":"button","button":"B","durationMs":50}
  ],
  "repeatCount": 3
}'
```

### Macros

```bash
# Save a macro
curl -X POST http://localhost:8000/macro/save -H "Content-Type: application/json" \
     -d '{
  "name": "farm_berries",
  "steps": [
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":500},
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":1000}
  ]
}'

# List macros
curl http://localhost:8000/macro/list

# Execute macro 10 times
curl -X POST http://localhost:8000/macro/execute -H "Content-Type: application/json" \
     -d '{"name":"farm_berries","repeatCount":10}'

# Delete macro
curl -X DELETE http://localhost:8000/macro/farm_berries
```

### Batch Operations

```bash
# Execute multiple commands in one request
curl -X POST http://localhost:8000/batch -H "Content-Type: application/json" \
     -d '{
  "commands": [
    {"type":"button","button":"HOME","durationMs":100},
    {"type":"wait","durationMs":1000},
    {"type":"button","button":"A","durationMs":50},
    {"type":"combo","buttons":["A","B"],"durationMs":100}
  ]
}'
```

### Device Control

```bash
# Turn LED on
curl -X POST http://localhost:8000/led -H "Content-Type: application/json" \
     -d '{"state":true}'

# Get firmware version
curl http://localhost:8000/version

# Change to Pro Controller mode
curl -X POST http://localhost:8000/controller/mode -H "Content-Type: application/json" \
     -d '{"mode":0}'

# Change controller color (red body, white buttons)
curl -X POST http://localhost:8000/controller/color -H "Content-Type: application/json" \
     -d '{"body_r":255,"body_g":0,"body_b":0,"button_r":255,"button_g":255,"button_b":255}'
```

### Utilities

```bash
# Health check
curl http://localhost:8000/health

# List available buttons
curl http://localhost:8000/buttons

# List available directions
curl http://localhost:8000/directions
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Action Step Types

When using `/sequence`, `/macro/save`, or batch operations, the following action types are supported:

| Type | Required Fields | Optional Fields | Description |
|------|----------------|-----------------|-------------|
| `button` | `button` | `durationMs` | Press a single button |
| `combo` | `buttons` | `durationMs` | Press multiple buttons simultaneously |
| `hat` | `direction` | `durationMs` | Press D-Pad direction |
| `stick` | - | `lx`, `ly`, `rx`, `ry`, `durationMs` | Control analog sticks |
| `wait` | - | `durationMs` | Wait/delay |

## Button Names

A, B, X, Y, L, R, ZL, ZR, PLUS, MINUS, LCLICK, RCLICK, HOME, CAPTURE

## Direction Names

TOP, TOP_RIGHT, RIGHT, BOTTOM_RIGHT, BOTTOM, BOTTOM_LEFT, LEFT, TOP_LEFT, CENTER

## Controller Modes

- `0`: Pro Controller
- `1`: Joy-Con (L)
- `2`: Joy-Con (R)

## Notes

- Serial settings are fixed to 115200 8N1.
- Each press sends action → waits for `durationMs` → sends RESET.
- Handshake will clear stale bytes before sending.
- Macros are stored in memory and will be lost on server restart.
- For persistent macros, consider saving them to a file or database.

## License

MIT
