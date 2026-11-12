from math import ceil

from CommandBlock import CommandBlock
import numpy as np


class DotMatrixAnimation(CommandBlock):
    WIDTH = 7
    HEIGHT = 7
    REPORT_SIZE = 4104
    HEADER_SIZE = 8
    PAYLOAD_SIZE = REPORT_SIZE - HEADER_SIZE

    def __init__(
        self,
        frame: list[np.ndarray],
        speed: int,
    ):
        super().__init__(operand=0x41)

        if not frame:
            raise ValueError("At least one frame is required")
        if len(frame) > 0xFFFF:
            raise ValueError("Number of frame cannot exceed 65535")
        if not 0 <= speed <= 101:
            raise ValueError("Animation speed must be between 0 and 101")

        self.frame = frame
        self.speed = speed
        self._validate_frames()

    def _validate_frames(self) -> None:
        for frame_index, image in enumerate(self.frame):
            if not isinstance(image, np.ndarray):
                raise TypeError(f"Frame {frame_index} must be a numpy.ndarray")
            if image.shape != (self.HEIGHT, self.WIDTH, 3):
                raise ValueError(
                    f"Frame {frame_index} must have shape "
                    f"({self.HEIGHT}, {self.WIDTH}, 3), got {image.shape}"
                )
            if image.dtype != np.int8:
                raise TypeError(
                    f"Frame {frame_index} must have dtype numpy.int8, "
                    f"got {image.dtype}"
                )

    def _data(self) -> bytes:
        frame_count = len(self.frame).to_bytes(2, "little")
        setting = (101 - self.speed).to_bytes(2, "little")
        pixels = b"".join(image.tobytes(order="C") for image in self.frame)
        return frame_count + setting + pixels

    def commands(self) -> list[bytes]:
        data = self._data()
        chunk_count = ceil(len(data) / self.PAYLOAD_SIZE)
        if chunk_count > 0xFFFF:
            raise ValueError("Animation is too big")

        commands = []
        for chunk_index in range(chunk_count):
            start = chunk_index * self.PAYLOAD_SIZE
            chunk = data[start:start + self.PAYLOAD_SIZE]
            chunk = chunk.ljust(self.PAYLOAD_SIZE, b"\x00")

            header = bytes((
                0xAA,
                self.operand,
                (chunk_index >> 8) & 0xFF,
                chunk_index & 0xFF,
                (chunk_count >> 8) & 0xFF,
                chunk_count & 0xFF,
                0x00,
                0x00,
            ))
            commands.append(header + chunk)
        return commands

    def command(self) -> bytes:
        commands = self.commands()
        if len(commands) != 1:
            raise ValueError("Animation has multiple reports; use commands()")
        return commands[0]

    def expect(self) -> bytes:
        return bytes([0x55, self.operand])
