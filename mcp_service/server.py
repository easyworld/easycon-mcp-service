from typing import Optional, List
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from mcp_service.serial_service import EasyConSerial, list_serial_ports
from mcp_service.switch_protocol import (
    SwitchReport,
    RESET_REPORT,
    SwitchButton,
    SwitchHAT,
    SwitchStick,
)

app = FastAPI(title="EasyCon MCP Service", version="1.0.0")
SER = EasyConSerial()

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