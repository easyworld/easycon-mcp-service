from typing import Optional, List, Dict, Any
import time
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from mcp_service.serial_service import EasyConSerial, list_serial_ports, Command
from mcp_service.switch_protocol import (
    SwitchReport,
    RESET_REPORT,
    SwitchButton,
    SwitchHAT,
    SwitchStick,
)

app = FastAPI(title="EasyCon MCP Service", version="2.0.0")
SER = EasyConSerial()

# In-memory macro storage
MACROS: Dict[str, List[Dict[str, Any]]] = {}

class ConnectReq(BaseModel):
    port: str
    baud: int = 115200

class PressButtonReq(BaseModel):
    button: str
    durationMs: int = Field(default=50, ge=0, le=2000)

class PressHatReq(BaseModel):
    direction: str
    durationMs: int = Field(default=50, ge=0, le=2000)

class StickReq(BaseModel):
    lx: int = Field(default=SwitchStick.STICK_CENTER, ge=0, le=255)
    ly: int = Field(default=SwitchStick.STICK_CENTER, ge=0, le=255)
    rx: int = Field(default=SwitchStick.STICK_CENTER, ge=0, le=255)
    ry: int = Field(default=SwitchStick.STICK_CENTER, ge=0, le=255)
    durationMs: int = Field(default=50, ge=0, le=5000)

class RawSendReq(BaseModel):
    hex: Optional[str] = None
    bytes: Optional[List[int]] = None
    timeoutMs: int = 500
    maxBytes: int = 255

class ComboButtonReq(BaseModel):
    buttons: List[str]
    durationMs: int = Field(default=50, ge=0, le=2000)

class ActionStep(BaseModel):
    type: str  # "button", "hat", "stick", "wait", "combo"
    button: Optional[str] = None
    buttons: Optional[List[str]] = None
    direction: Optional[str] = None
    lx: Optional[int] = None
    ly: Optional[int] = None
    rx: Optional[int] = None
    ry: Optional[int] = None
    durationMs: int = Field(default=50, ge=0, le=5000)

class SequenceReq(BaseModel):
    steps: List[ActionStep]
    repeatCount: int = Field(default=1, ge=1, le=100)

class MacroReq(BaseModel):
    name: str
    steps: List[ActionStep]

class ExecuteMacroReq(BaseModel):
    name: str
    repeatCount: int = Field(default=1, ge=1, le=100)

class LEDReq(BaseModel):
    state: bool  # True = ON, False = OFF

class ControllerModeReq(BaseModel):
    mode: int = Field(default=0, ge=0, le=2)  # 0=Pro, 1=JoyConL, 2=JoyConR

class ControllerColorReq(BaseModel):
    body_r: int = Field(default=0, ge=0, le=255)
    body_g: int = Field(default=0, ge=0, le=255)
    body_b: int = Field(default=0, ge=0, le=255)
    button_r: int = Field(default=0, ge=0, le=255)
    button_g: int = Field(default=0, ge=0, le=255)
    button_b: int = Field(default=0, ge=0, le=255)

class BatchRequest(BaseModel):
    commands: List[Dict[str, Any]]

@app.get("/ports")
def ports():
    return [{"device": d, "desc": desc} for d, desc in list_serial_ports()]

@app.post("/connect")
def connect(req: ConnectReq):
    try:
        SER.connect(req.port, req.baud)
        return {"ok": True, "port": req.port}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/disconnect")
def disconnect():
    SER.disconnect()
    return {"ok": True}

@app.get("/status")
def status():
    return {"connected": SER.connected, "port": SER.port}

@app.post("/init")
def init():
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        resp = SER.handshake()
        return {"ok": True, "respHex": resp.hex()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/press/button")
def press_button(req: PressButtonReq):
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        try:
            btn = SwitchButton[req.button.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Unknown button: {req.button}")
        report = SwitchReport(button=btn.value)
        SER.send_and_recv(report.to_bytes(), max_bytes=8, timeout=req.durationMs/1000.0)
        if req.durationMs > 0:
            time.sleep(req.durationMs / 1000.0)
        SER.send_and_recv(RESET_REPORT.to_bytes(), max_bytes=8, timeout=0.5)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/press/hat")
def press_hat(req: PressHatReq):
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        try:
            hat = SwitchHAT[req.direction.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Unknown direction: {req.direction}")
        report = SwitchReport(HAT=hat.value)
        SER.send_and_recv(report.to_bytes(), max_bytes=8, timeout=req.durationMs/1000.0)
        if req.durationMs > 0:
            time.sleep(req.durationMs / 1000.0)
        SER.send_and_recv(RESET_REPORT.to_bytes(), max_bytes=8, timeout=0.5)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stick")
def stick(req: StickReq):
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        report = SwitchReport(
            LX=req.lx, LY=req.ly, RX=req.rx, RY=req.ry
        )
        SER.send_and_recv(report.to_bytes(), max_bytes=8, timeout=req.durationMs/1000.0)
        if req.durationMs > 0:
            time.sleep(req.durationMs / 1000.0)
        SER.send_and_recv(RESET_REPORT.to_bytes(), max_bytes=8, timeout=0.5)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
def reset():
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        SER.send_and_recv(RESET_REPORT.to_bytes(), max_bytes=8, timeout=0.5)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/raw/send")
def raw_send(req: RawSendReq):
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    if not req.hex and not req.bytes:
        raise HTTPException(status_code=400, detail="hex or bytes is required")
    try:
        if req.hex:
            data = bytes.fromhex(req.hex)
        else:
            data = bytes([b & 0xFF for b in (req.bytes or [])])
        resp = SER.send_and_recv(data, max_bytes=req.maxBytes, timeout=req.timeoutMs/1000.0)
        return {"ok": True, "respHex": resp.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/press/combo")
def press_combo(req: ComboButtonReq):
    """Press multiple buttons simultaneously"""
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        button_mask = 0
        for btn_name in req.buttons:
            try:
                btn = SwitchButton[btn_name.upper()]
                button_mask |= btn.value
            except KeyError:
                raise HTTPException(status_code=400, detail=f"Unknown button: {btn_name}")
        
        report = SwitchReport(button=button_mask)
        SER.send_and_recv(report.to_bytes(), max_bytes=8, timeout=req.durationMs/1000.0)
        if req.durationMs > 0:
            time.sleep(req.durationMs / 1000.0)
        SER.send_and_recv(RESET_REPORT.to_bytes(), max_bytes=8, timeout=0.5)
        return {"ok": True, "buttons": req.buttons}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sequence")
def execute_sequence(req: SequenceReq):
    """Execute a sequence of actions"""
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        for _ in range(req.repeatCount):
            for step in req.steps:
                _execute_action_step(step)
        return {"ok": True, "steps": len(req.steps), "repeats": req.repeatCount}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/macro/save")
def save_macro(req: MacroReq):
    """Save a macro for later execution"""
    MACROS[req.name] = [step.dict() for step in req.steps]
    return {"ok": True, "name": req.name, "steps": len(req.steps)}

@app.get("/macro/list")
def list_macros():
    """List all saved macros"""
    return {"macros": [{"name": name, "steps": len(steps)} for name, steps in MACROS.items()]}

@app.get("/macro/{name}")
def get_macro(name: str):
    """Get macro details"""
    if name not in MACROS:
        raise HTTPException(status_code=404, detail=f"Macro not found: {name}")
    return {"name": name, "steps": MACROS[name]}

@app.delete("/macro/{name}")
def delete_macro(name: str):
    """Delete a saved macro"""
    if name not in MACROS:
        raise HTTPException(status_code=404, detail=f"Macro not found: {name}")
    del MACROS[name]
    return {"ok": True, "name": name}

@app.post("/macro/execute")
def execute_macro(req: ExecuteMacroReq):
    """Execute a saved macro"""
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    if req.name not in MACROS:
        raise HTTPException(status_code=404, detail=f"Macro not found: {req.name}")
    try:
        for _ in range(req.repeatCount):
            for step_dict in MACROS[req.name]:
                step = ActionStep(**step_dict)
                _execute_action_step(step)
        return {"ok": True, "name": req.name, "repeats": req.repeatCount}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/led")
def control_led(req: LEDReq):
    """Control device LED"""
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        cmd = bytes([Command.Ready, Command.Ready, Command.LED, 1 if req.state else 0])
        resp = SER.send_and_recv(cmd, max_bytes=8, timeout=0.5)
        return {"ok": True, "state": req.state, "respHex": resp.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/version")
def get_version():
    """Get firmware version"""
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        cmd = bytes([Command.Ready, Command.Ready, Command.Version])
        resp = SER.send_and_recv(cmd, max_bytes=32, timeout=0.5)
        return {"ok": True, "respHex": resp.hex(), "version": resp.decode('utf-8', errors='ignore').strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/controller/mode")
def change_controller_mode(req: ControllerModeReq):
    """Change controller mode (Pro/JoyConL/JoyConR)"""
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        cmd = bytes([Command.Ready, Command.Ready, Command.ChangeControllerMode, req.mode])
        resp = SER.send_and_recv(cmd, max_bytes=8, timeout=0.5)
        return {"ok": True, "mode": req.mode, "respHex": resp.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/controller/color")
def change_controller_color(req: ControllerColorReq):
    """Change controller color"""
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        cmd = bytes([
            Command.Ready, Command.Ready, Command.ChangeControllerColor,
            req.body_r, req.body_g, req.body_b,
            req.button_r, req.button_g, req.button_b
        ])
        resp = SER.send_and_recv(cmd, max_bytes=8, timeout=0.5)
        return {"ok": True, "respHex": resp.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/unpair")
def unpair_controller():
    """Unpair controller from console"""
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    try:
        cmd = bytes([Command.Ready, Command.Ready, Command.UnPair])
        resp = SER.send_and_recv(cmd, max_bytes=8, timeout=0.5)
        return {"ok": True, "respHex": resp.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch")
def batch_execute(req: BatchRequest):
    """Execute multiple commands in batch"""
    if not SER.connected:
        raise HTTPException(status_code=400, detail="Serial not connected")
    
    results = []
    for i, cmd in enumerate(req.commands):
        try:
            cmd_type = cmd.get("type")
            if cmd_type == "button":
                btn_req = PressButtonReq(**cmd)
                press_button(btn_req)
            elif cmd_type == "hat":
                hat_req = PressHatReq(**cmd)
                press_hat(hat_req)
            elif cmd_type == "stick":
                stick_req = StickReq(**cmd)
                stick(stick_req)
            elif cmd_type == "combo":
                combo_req = ComboButtonReq(**cmd)
                press_combo(combo_req)
            elif cmd_type == "wait":
                wait_ms = cmd.get("durationMs", 100)
                time.sleep(wait_ms / 1000.0)
            else:
                results.append({"index": i, "ok": False, "error": f"Unknown command type: {cmd_type}"})
                continue
            results.append({"index": i, "ok": True})
        except Exception as e:
            results.append({"index": i, "ok": False, "error": str(e)})
    
    return {"ok": True, "results": results}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "connected": SER.connected,
        "port": SER.port,
        "macros_count": len(MACROS),
        "version": "2.0.0"
    }

@app.get("/buttons")
def list_buttons():
    """List all available buttons"""
    return {"buttons": [btn.name for btn in SwitchButton]}

@app.get("/directions")
def list_directions():
    """List all available HAT directions"""
    return {"directions": [hat.name for hat in SwitchHAT]}

def _execute_action_step(step: ActionStep):
    """Internal helper to execute a single action step"""
    if step.type == "button":
        if not step.button:
            raise ValueError("button field required for type=button")
        btn = SwitchButton[step.button.upper()]
        report = SwitchReport(button=btn.value)
        SER.send_and_recv(report.to_bytes(), max_bytes=8, timeout=step.durationMs/1000.0)
        if step.durationMs > 0:
            time.sleep(step.durationMs / 1000.0)
        SER.send_and_recv(RESET_REPORT.to_bytes(), max_bytes=8, timeout=0.5)
    
    elif step.type == "combo":
        if not step.buttons:
            raise ValueError("buttons field required for type=combo")
        button_mask = 0
        for btn_name in step.buttons:
            btn = SwitchButton[btn_name.upper()]
            button_mask |= btn.value
        report = SwitchReport(button=button_mask)
        SER.send_and_recv(report.to_bytes(), max_bytes=8, timeout=step.durationMs/1000.0)
        if step.durationMs > 0:
            time.sleep(step.durationMs / 1000.0)
        SER.send_and_recv(RESET_REPORT.to_bytes(), max_bytes=8, timeout=0.5)
    
    elif step.type == "hat":
        if not step.direction:
            raise ValueError("direction field required for type=hat")
        hat = SwitchHAT[step.direction.upper()]
        report = SwitchReport(HAT=hat.value)
        SER.send_and_recv(report.to_bytes(), max_bytes=8, timeout=step.durationMs/1000.0)
        if step.durationMs > 0:
            time.sleep(step.durationMs / 1000.0)
        SER.send_and_recv(RESET_REPORT.to_bytes(), max_bytes=8, timeout=0.5)
    
    elif step.type == "stick":
        lx = step.lx if step.lx is not None else SwitchStick.STICK_CENTER
        ly = step.ly if step.ly is not None else SwitchStick.STICK_CENTER
        rx = step.rx if step.rx is not None else SwitchStick.STICK_CENTER
        ry = step.ry if step.ry is not None else SwitchStick.STICK_CENTER
        report = SwitchReport(LX=lx, LY=ly, RX=rx, RY=ry)
        SER.send_and_recv(report.to_bytes(), max_bytes=8, timeout=step.durationMs/1000.0)
        if step.durationMs > 0:
            time.sleep(step.durationMs / 1000.0)
        SER.send_and_recv(RESET_REPORT.to_bytes(), max_bytes=8, timeout=0.5)
    
    elif step.type == "wait":
        time.sleep(step.durationMs / 1000.0)
    
    else:
        raise ValueError(f"Unknown action type: {step.type}")