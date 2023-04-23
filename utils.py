import os
from dataclasses import dataclass, field
from typing import Dict, Optional
from constants import CHANNELS_RGB, CHANNELS_RGBA, QOI_PADDING

@dataclass
class Pixel:
    px_bytes: bytearray = field(init=False)

    def __post_init__(self):
        self.px_bytes = bytearray((0, 0, 0, 255))

    def update(self, values: bytes) -> None:
        n_channels = len(values)
        if n_channels not in (CHANNELS_RGB, CHANNELS_RGBA):
            raise ValueError("a tuple of 3 or 4 values should be provided")

        self.px_bytes[:n_channels] = values

    def __str__(self) -> str:
        r, g, b, a = self.px_bytes
        return f"R: {r} G: {g} B: {b} A: {a}"

    @property
    def bytes(self) -> bytes:
        return bytes(self.px_bytes)

    @property
    def hash(self) -> int:
        r, g, b, a = self.px_bytes
        return (r * 3 + g * 5 + b * 7 + a * 11) % 64

    @property
    def red(self) -> int:
        return self.px_bytes[0]

    @property
    def green(self) -> int:
        return self.px_bytes[1]

    @property
    def blue(self) -> int:
        return self.px_bytes[2]

    @property
    def alpha(self) -> int:
        return self.px_bytes[3]


class ByteWriter:
    def __init__(self, size: int):
        self.bytes = bytearray(size)
        self.write_pos = 0

    def write(self, byte: int) -> None:
        self.bytes[self.write_pos] = byte % 256
        self.write_pos += 1

    def output(self) -> bytes:
        return bytes(self.bytes[:self.write_pos])


class ByteReader:
    padding_len = len(QOI_PADDING)

    def __init__(self, data: bytes):
        self.bytes = data
        self.read_pos = 0
        self.max_pos = len(self.bytes) - self.padding_len

    def read(self) -> Optional[int]:
        if self.read_pos >= self.max_pos:
            return None

        out = self.bytes[self.read_pos]
        self.read_pos += 1
        return out

    def output(self) -> bytes:
        return bytes(self.bytes[:self.read_pos])


def replace_extension(path: str, extension: str) -> str:
    pre, ext = os.path.splitext(path)
    new_path = pre + "." + extension
    return new_path
