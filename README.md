# EasyCon MCP Service

EasyCon MCP Service: HTTP/JSON API for Nintendo Switch control over EasyCon protocol via serial (USB/UART).

This service implements:
- Serial lifecycle: list ports, connect/disconnect, status
- EasyCon handshake: send [A5, A5, 81] and expect [80]
- Switch controls: buttons, D-Pad (HAT), sticks, and reset
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

## API

- GET /ports
- POST /connect { "port": "/dev/ttyUSB0", "baud": 115200 }
- POST /disconnect
- GET /status
- POST /init
- POST /press/button { "button": "A", "durationMs": 50 }
- POST /press/hat { "direction": "TOP", "durationMs": 50 }
- POST /stick { "lx": 128, "ly": 128, "rx": 128, "ry": 128, "durationMs": 50 }
- POST /reset
- POST /raw/send { "hex": "A5A581", "timeoutMs": 500, "maxBytes": 255 }

### Example

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

## Notes

- Serial settings are fixed to 115200 8N1.
- Each press sends action -> waits for `durationMs` -> sends RESET.
- Handshake will clear stale bytes before sending.

## License

MIT