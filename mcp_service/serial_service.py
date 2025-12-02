import binascii
import threading
from typing import List, Optional, Tuple

import serial
import serial.tools.list_ports

class Command:
    Ready = 0xA5
    Debug = 0x80
    Hello = 0x81
    Flash = 0x82
    ScriptStart = 0x83
    ScriptStop = 0x84
    Version = 0x85
    LED = 0x86
    UnPair = 0x87
    ChangeControllerMode = 0x88
    ChangeControllerColor = 0x89
    SaveAmiibo = 0x90
    ChangeAmiiboIndex = 0x91

class Reply:
    Error = 0x00
    Busy = 0xFE
    Ack = 0xFF
    Hello = 0x80
    FlashStart = 0x81
    FlashEnd = 0x82
    ScriptAck = 0x83

def list_serial_ports() -> List[Tuple[str, str]]:
    ports = []
    for p in serial.tools.list_ports.comports():
        ports.append((p.device, f"{p.manufacturer or ''} {p.description or ''}".strip()))
    return ports

class EasyConSerial:
    def __init__(self):
        self._ser: Optional[serial.Serial] = None
        self._lock = threading.Lock()
        self._port_name: Optional[str] = None

    @property
    def connected(self) -> bool:
        return self._ser is not None and self._ser.is_open

    @property
    def port(self) -> Optional[str]:
        return self._port_name

    def connect(self, port: str, baud: int = 115200, timeout: float = 0.5):
        with self._lock:
            if self.connected:
                raise RuntimeError("Already connected")
            s = serial.Serial()
            s.port = port
            s.baudrate = baud
            s.bytesize = serial.EIGHTBITS
            s.parity = serial.PARITY_NONE
            s.stopbits = serial.STOPBITS_ONE
            s.timeout = timeout
            s.write_timeout = timeout
            s.open()
            self._ser = s
            self._port_name = port

    def disconnect(self):
        with self._lock:
            if self._ser:
                try:
                    self._ser.close()
                finally:
                    self._ser = None
                    self._port_name = None

    def eat_verbose(self):
        with self._lock:
            if not self.connected:
                raise RuntimeError("Serial not connected")
            if self._ser.in_waiting:
                _ = self._ser.read(self._ser.in_waiting)

    def send_and_recv(self, data: bytes, max_bytes: int = 255, timeout: float = 0.5) -> bytes:
        with self._lock:
            if not self.connected:
                raise RuntimeError("Serial not connected")
            old_timeout = self._ser.timeout
            self._ser.timeout = timeout
            try:
                self._ser.write(data)
                self._ser.flush()
                buf = self._ser.read(max_bytes)
                return buf or b""
            finally:
                self._ser.timeout = old_timeout

    def handshake(self) -> bytes:
        self.eat_verbose()
        req = bytes([Command.Ready, Command.Ready, Command.Hello])
        resp = self.send_and_recv(req, max_bytes=8, timeout=0.5)
        if not resp or resp[0] != Reply.Hello:
            raise RuntimeError(f"Handshake failed, got: {binascii.hexlify(resp or b'').decode()}")
        return resp