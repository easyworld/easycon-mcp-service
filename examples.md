# EasyCon MCP Service - API Examples

This document provides comprehensive examples for all API endpoints.

## Table of Contents
- [Connection Management](#connection-management)
- [Basic Controls](#basic-controls)
- [Combo Buttons](#combo-buttons)
- [Sequences](#sequences)
- [Macros](#macros)
- [Batch Operations](#batch-operations)
- [Device Control](#device-control)
- [Utilities](#utilities)

---

## Connection Management

### List Available Ports
```bash
curl http://localhost:8000/ports
```

Response:
```json
[
  {"device": "COM3", "desc": "USB Serial Port"},
  {"device": "COM4", "desc": "Arduino Uno"}
]
```

### Connect to Device
```bash
curl -X POST http://localhost:8000/connect \
  -H "Content-Type: application/json" \
  -d '{"port":"COM3","baud":115200}'
```

### Initialize Device (Handshake)
```bash
curl -X POST http://localhost:8000/init
```

### Check Connection Status
```bash
curl http://localhost:8000/status
```

Response:
```json
{"connected": true, "port": "COM3"}
```

### Disconnect
```bash
curl -X POST http://localhost:8000/disconnect
```

---

## Basic Controls

### Press Single Button
```bash
# Press A button for 50ms
curl -X POST http://localhost:8000/press/button \
  -H "Content-Type: application/json" \
  -d '{"button":"A","durationMs":50}'

# Press HOME button for 100ms
curl -X POST http://localhost:8000/press/button \
  -H "Content-Type: application/json" \
  -d '{"button":"HOME","durationMs":100}'
```

### Press D-Pad Direction
```bash
# Press UP
curl -X POST http://localhost:8000/press/hat \
  -H "Content-Type: application/json" \
  -d '{"direction":"TOP","durationMs":50}'

# Press DOWN-RIGHT diagonal
curl -X POST http://localhost:8000/press/hat \
  -H "Content-Type: application/json" \
  -d '{"direction":"BOTTOM_RIGHT","durationMs":50}'
```

### Control Analog Sticks
```bash
# Move left stick up
curl -X POST http://localhost:8000/stick \
  -H "Content-Type: application/json" \
  -d '{"lx":128,"ly":0,"rx":128,"ry":128,"durationMs":100}'

# Move right stick to top-right
curl -X POST http://localhost:8000/stick \
  -H "Content-Type: application/json" \
  -d '{"lx":128,"ly":128,"rx":255,"ry":0,"durationMs":100}'
```

### Reset Controller State
```bash
curl -X POST http://localhost:8000/reset
```

---

## Combo Buttons

### Press Multiple Buttons Simultaneously

#### Take Screenshot (L+R)
```bash
curl -X POST http://localhost:8000/press/combo \
  -H "Content-Type: application/json" \
  -d '{"buttons":["L","R"],"durationMs":50}'
```

#### Open Home Menu + Quick Settings (HOME+X)
```bash
curl -X POST http://localhost:8000/press/combo \
  -H "Content-Type: application/json" \
  -d '{"buttons":["HOME","X"],"durationMs":100}'
```

#### Press A+B+X+Y
```bash
curl -X POST http://localhost:8000/press/combo \
  -H "Content-Type: application/json" \
  -d '{"buttons":["A","B","X","Y"],"durationMs":100}'
```

---

## Sequences

### Simple Button Sequence
```bash
# Press A, wait 500ms, press B, wait 500ms, press A again
curl -X POST http://localhost:8000/sequence \
  -H "Content-Type: application/json" \
  -d '{
  "steps": [
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":500},
    {"type":"button","button":"B","durationMs":50},
    {"type":"wait","durationMs":500},
    {"type":"button","button":"A","durationMs":50}
  ],
  "repeatCount": 1
}'
```

### Complex Sequence with Combos and Sticks
```bash
curl -X POST http://localhost:8000/sequence \
  -H "Content-Type: application/json" \
  -d '{
  "steps": [
    {"type":"combo","buttons":["ZL","ZR"],"durationMs":100},
    {"type":"wait","durationMs":200},
    {"type":"stick","lx":255,"ly":128,"durationMs":500},
    {"type":"button","button":"A","durationMs":50},
    {"type":"hat","direction":"TOP","durationMs":50}
  ],
  "repeatCount": 3
}'
```

### Auto-Farming Sequence
```bash
# Spam A button 10 times with delays
curl -X POST http://localhost:8000/sequence \
  -H "Content-Type: application/json" \
  -d '{
  "steps": [
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":100}
  ],
  "repeatCount": 10
}'
```

---

## Macros

### Save a Macro

#### Berry Farming Macro
```bash
curl -X POST http://localhost:8000/macro/save \
  -H "Content-Type: application/json" \
  -d '{
  "name": "farm_berries",
  "steps": [
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":500},
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":1000},
    {"type":"button","button":"B","durationMs":50},
    {"type":"wait","durationMs":500}
  ]
}'
```

#### Pokemon Egg Hatching Macro
```bash
curl -X POST http://localhost:8000/macro/save \
  -H "Content-Type: application/json" \
  -d '{
  "name": "hatch_eggs",
  "steps": [
    {"type":"stick","lx":128,"ly":0,"durationMs":1000},
    {"type":"wait","durationMs":100},
    {"type":"stick","lx":128,"ly":255,"durationMs":1000},
    {"type":"wait","durationMs":100}
  ]
}'
```

#### Menu Navigation Macro
```bash
curl -X POST http://localhost:8000/macro/save \
  -H "Content-Type: application/json" \
  -d '{
  "name": "open_settings",
  "steps": [
    {"type":"button","button":"HOME","durationMs":100},
    {"type":"wait","durationMs":1000},
    {"type":"hat","direction":"BOTTOM","durationMs":50},
    {"type":"wait","durationMs":200},
    {"type":"button","button":"A","durationMs":50}
  ]
}'
```

### List All Macros
```bash
curl http://localhost:8000/macro/list
```

Response:
```json
{
  "macros": [
    {"name": "farm_berries", "steps": 6},
    {"name": "hatch_eggs", "steps": 4},
    {"name": "open_settings", "steps": 7}
  ]
}
```

### Get Macro Details
```bash
curl http://localhost:8000/macro/farm_berries
```

### Execute a Macro
```bash
# Run once
curl -X POST http://localhost:8000/macro/execute \
  -H "Content-Type: application/json" \
  -d '{"name":"farm_berries","repeatCount":1}'

# Run 20 times
curl -X POST http://localhost:8000/macro/execute \
  -H "Content-Type: application/json" \
  -d '{"name":"hatch_eggs","repeatCount":20}'
```

### Delete a Macro
```bash
curl -X DELETE http://localhost:8000/macro/farm_berries
```

---

## Batch Operations

### Execute Multiple Commands in One Request

#### Quick Game Start Sequence
```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
  "commands": [
    {"type":"button","button":"HOME","durationMs":100},
    {"type":"wait","durationMs":1000},
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":2000},
    {"type":"button","button":"A","durationMs":50}
  ]
}'
```

#### Complex Battle Combo
```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
  "commands": [
    {"type":"combo","buttons":["ZL","A"],"durationMs":100},
    {"type":"wait","durationMs":500},
    {"type":"stick","lx":255,"ly":128,"rx":128,"ry":128,"durationMs":200},
    {"type":"button","button":"B","durationMs":50},
    {"type":"wait","durationMs":100},
    {"type":"combo","buttons":["L","R"],"durationMs":50}
  ]
}'
```

---

## Device Control

### LED Control

#### Turn LED On
```bash
curl -X POST http://localhost:8000/led \
  -H "Content-Type: application/json" \
  -d '{"state":true}'
```

#### Turn LED Off
```bash
curl -X POST http://localhost:8000/led \
  -H "Content-Type: application/json" \
  -d '{"state":false}'
```

### Get Firmware Version
```bash
curl http://localhost:8000/version
```

Response:
```json
{
  "ok": true,
  "respHex": "76312e302e30",
  "version": "v1.0.0"
}
```

### Change Controller Mode

#### Switch to Pro Controller Mode
```bash
curl -X POST http://localhost:8000/controller/mode \
  -H "Content-Type: application/json" \
  -d '{"mode":0}'
```

#### Switch to Joy-Con (L) Mode
```bash
curl -X POST http://localhost:8000/controller/mode \
  -H "Content-Type: application/json" \
  -d '{"mode":1}'
```

#### Switch to Joy-Con (R) Mode
```bash
curl -X POST http://localhost:8000/controller/mode \
  -H "Content-Type: application/json" \
  -d '{"mode":2}'
```

### Change Controller Color

#### Red and White Controller
```bash
curl -X POST http://localhost:8000/controller/color \
  -H "Content-Type: application/json" \
  -d '{
    "body_r":255,"body_g":0,"body_b":0,
    "button_r":255,"button_g":255,"button_b":255
  }'
```

#### Blue and Yellow Controller
```bash
curl -X POST http://localhost:8000/controller/color \
  -H "Content-Type: application/json" \
  -d '{
    "body_r":0,"body_g":100,"body_b":255,
    "button_r":255,"button_g":255,"button_b":0
  }'
```

#### Black Controller
```bash
curl -X POST http://localhost:8000/controller/color \
  -H "Content-Type: application/json" \
  -d '{
    "body_r":0,"body_g":0,"body_b":0,
    "button_r":50,"button_g":50,"button_b":50
  }'
```

### Unpair Controller
```bash
curl -X POST http://localhost:8000/unpair
```

---

## Utilities

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "connected": true,
  "port": "COM3",
  "macros_count": 3,
  "version": "2.0.0"
}
```

### List Available Buttons
```bash
curl http://localhost:8000/buttons
```

Response:
```json
{
  "buttons": [
    "Y", "B", "A", "X", "L", "R", "ZL", "ZR",
    "MINUS", "PLUS", "LCLICK", "RCLICK", "HOME", "CAPTURE"
  ]
}
```

### List Available Directions
```bash
curl http://localhost:8000/directions
```

Response:
```json
{
  "directions": [
    "TOP", "TOP_RIGHT", "RIGHT", "BOTTOM_RIGHT",
    "BOTTOM", "BOTTOM_LEFT", "LEFT", "TOP_LEFT", "CENTER"
  ]
}
```

### Send Raw Bytes
```bash
# Using hex string
curl -X POST http://localhost:8000/raw/send \
  -H "Content-Type: application/json" \
  -d '{"hex":"A5A581","timeoutMs":500,"maxBytes":255}'

# Using byte array
curl -X POST http://localhost:8000/raw/send \
  -H "Content-Type: application/json" \
  -d '{"bytes":[165,165,129],"timeoutMs":500,"maxBytes":255}'
```

---

## Python Examples

### Using `requests` Library

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Connect
response = requests.post(f"{BASE_URL}/connect", json={"port": "COM3", "baud": 115200})
print(response.json())

# Initialize
response = requests.post(f"{BASE_URL}/init")
print(response.json())

# Press A button
response = requests.post(f"{BASE_URL}/press/button", json={"button": "A", "durationMs": 50})
print(response.json())

# Press combo
response = requests.post(f"{BASE_URL}/press/combo", json={"buttons": ["L", "R"], "durationMs": 50})
print(response.json())

# Execute sequence
sequence = {
    "steps": [
        {"type": "button", "button": "A", "durationMs": 50},
        {"type": "wait", "durationMs": 100},
        {"type": "button", "button": "B", "durationMs": 50}
    ],
    "repeatCount": 3
}
response = requests.post(f"{BASE_URL}/sequence", json=sequence)
print(response.json())

# Save and execute macro
macro = {
    "name": "my_macro",
    "steps": [
        {"type": "button", "button": "HOME", "durationMs": 100},
        {"type": "wait", "durationMs": 1000}
    ]
}
requests.post(f"{BASE_URL}/macro/save", json=macro)
requests.post(f"{BASE_URL}/macro/execute", json={"name": "my_macro", "repeatCount": 1})

# Disconnect
requests.post(f"{BASE_URL}/disconnect")
```

---

## PowerShell Examples

```powershell
$baseUrl = "http://localhost:8000"

# Connect
Invoke-RestMethod -Method Post -Uri "$baseUrl/connect" `
    -ContentType "application/json" `
    -Body '{"port":"COM3","baud":115200}'

# Press button
Invoke-RestMethod -Method Post -Uri "$baseUrl/press/button" `
    -ContentType "application/json" `
    -Body '{"button":"A","durationMs":50}'

# Health check
Invoke-RestMethod -Method Get -Uri "$baseUrl/health"
```

---

## Use Cases

### 1. Automated Pokemon Shiny Hunting
```bash
# Save a shiny hunting macro
curl -X POST http://localhost:8000/macro/save \
  -H "Content-Type: application/json" \
  -d '{
  "name": "shiny_hunt",
  "steps": [
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":15000},
    {"type":"button","button":"HOME","durationMs":100},
    {"type":"wait","durationMs":1000},
    {"type":"button","button":"X","durationMs":50},
    {"type":"wait","durationMs":500},
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":2000}
  ]
}'

# Run it 1000 times
curl -X POST http://localhost:8000/macro/execute \
  -H "Content-Type: application/json" \
  -d '{"name":"shiny_hunt","repeatCount":1000}'
```

### 2. Automatic Item Farming
```bash
curl -X POST http://localhost:8000/sequence \
  -H "Content-Type: application/json" \
  -d '{
  "steps": [
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":500},
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":1500},
    {"type":"combo","buttons":["B","B"],"durationMs":100}
  ],
  "repeatCount": 50
}'
```

### 3. Menu Navigation Test
```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
  "commands": [
    {"type":"button","button":"HOME","durationMs":100},
    {"type":"wait","durationMs":1000},
    {"type":"hat","direction":"RIGHT","durationMs":50},
    {"type":"wait","durationMs":200},
    {"type":"hat","direction":"RIGHT","durationMs":50},
    {"type":"wait","durationMs":200},
    {"type":"button","button":"A","durationMs":50}
  ]
}'
```
