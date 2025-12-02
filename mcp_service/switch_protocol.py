from enum import Enum
from dataclasses import dataclass
from typing import List

class SwitchButton(Enum):
    Y = 0x01
    B = 0x02
    A = 0x04
    X = 0x08
    L = 0x10
    R = 0x20
    ZL = 0x40
    ZR = 0x80
    MINUS = 0x100
    PLUS = 0x200
    LCLICK = 0x400
    RCLICK = 0x800
    HOME = 0x1000
    CAPTURE = 0x2000

class SwitchHAT(Enum):
    TOP = 0x00
    TOP_RIGHT = 0x01
    RIGHT = 0x02
    BOTTOM_RIGHT = 0x03
    BOTTOM = 0x04
    BOTTOM_LEFT = 0x05
    LEFT = 0x06
    TOP_LEFT = 0x07
    CENTER = 0x08

class SwitchStick:
    STICK_MIN = 0
    STICK_CENMIN = 64
    STICK_CENTER = 128
    STICK_CENMAX = 192
    STICK_MAX = 255

@dataclass
class SwitchReport:
    button: int = 0
    HAT: int = SwitchHAT.CENTER.value
    LX: int = SwitchStick.STICK_CENTER
    LY: int = SwitchStick.STICK_CENTER
    RX: int = SwitchStick.STICK_CENTER
    RY: int = SwitchStick.STICK_CENTER

    def reset(self):
        self.button = 0
        self.HAT = SwitchHAT.CENTER.value
        self.LX = SwitchStick.STICK_CENTER
        self.LY = SwitchStick.STICK_CENTER
        self.RX = SwitchStick.STICK_CENTER
        self.RY = SwitchStick.STICK_CENTER

    def to_bytes(self) -> bytes:
        # 7 字节指令 -> 7bit 分片 -> 8 字节包（最后一字节 OR 0x80 作为结束标志）
        command = [
            (self.button >> 8) & 0xFF,
            self.button & 0xFF,
            self.HAT & 0xFF,
            self.LX & 0xFF,
            self.LY & 0xFF,
            self.RX & 0xFF,
            self.RY & 0xFF,
        ]
        packet: List[int] = []
        n = 0
        bits = 0
        for b in command:
            n = (n << 8) | (b & 0xFF)
            bits += 8
            while bits >= 7:
                bits -= 7
                packet.append((n >> bits) & 0x7F)
                n &= (1 << bits) - 1
        while len(packet) < 8:
            packet.append(0)
        packet = packet[:8]
        packet[7] |= 0x80
        return bytes(packet)

RESET_REPORT = SwitchReport()