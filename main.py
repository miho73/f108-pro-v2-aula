import time

import hid
import numpy as np
import psutil
from tqdm import tqdm

from CommandBlock import CommandBlock, RGBColor
from DotMatrix import DotMatrix, PickupLightMode
from DotMatrixAnimation import DotMatrixAnimation
from KeyboardBacklight import KeyboardBacklight, KeyboardBacklightMode
from SideLight import SideLight, SideLightMode
from find import compare

VID = 0x38A6  # AULA
PID = 0x2749  # F108 Pro V2

MANUFACTURER_USAGE_PAGE1 = 0xFF67
MANUFACTURER_USAGE_PAGE2 = 0xFF68
USAGE = 0x0061

aula67 = None
aula68 = None

for dev in hid.enumerate(VID, PID):
    if dev["usage"] == USAGE:
        if dev["usage_page"] == MANUFACTURER_USAGE_PAGE1:
            aula67 = hid.device()
            aula67.open_path(dev["path"])
        elif dev["usage_page"] == MANUFACTURER_USAGE_PAGE2:
            aula68 = hid.device()
            aula68.open_path(dev["path"])

if not aula67 or not aula68:
    raise RuntimeError("AULA F108 Pro V2 not found")

def exec(command: CommandBlock):
    device = aula67 if command.operand == 0x41 else aula68
    reports = command.commands() if hasattr(command, "commands") else [command.command()]
    expected = command.expect()

    for report in tqdm(reports, desc="TX", unit=" report", ncols=80):
        device.write(report)
        deadline = time.monotonic() + 1.0
        while True:
            remaining_ms = int((deadline - time.monotonic()) * 1000)
            if remaining_ms <= 0:
                tqdm.write("RX timeout")
                break
            response = bytes(device.read(len(report), remaining_ms))
            if not response:
                tqdm.write("RX timeout")
                break
            if response.startswith(expected):
                break
            # Ignore input reports for other commands (for example, 55 00).
            if response[:1] == b"\x55" and response[1:2] != expected[1:2]:
                continue
            tqdm.write("RX as Unexpected")
            compare(expected, response[:len(expected)])
            break

dot_matrix_cmd = DotMatrix(
    bg_color=RGBColor("000000"),
    txt_color=RGBColor("FFFFFF"),
    mode=PickupLightMode.CharacterMode
)
key_backlight_cmd = KeyboardBacklight(
    brightness=5,
    speed=3,
    light_mode=KeyboardBacklightMode.SinglePointOff,
    color=RGBColor("FFFFFF"),
    colorful_effects=False,
    reverse_effects=False,
    secondary_color=RGBColor("FF0000"),
    effect_mode_type=2
)
lightbox_cmd = SideLight(
    effect_mode=SideLightMode.DynamicBreathing,
    color=RGBColor("FFFFFF"),
    brightness=5,
    speed=3
)
exec(dot_matrix_cmd)

DIGITS = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
}
SCREEN_COLOR = np.array([-1, 0, -1], dtype=np.int8)

def memory_frame(percent: int) -> np.ndarray:
    frame = np.zeros((7, 7, 3), dtype=np.int8)
    for digit_index, digit in enumerate(f"{min(percent, 99):02d}"):
        col_offset = digit_index * 4
        for row, glyph_row in enumerate(DIGITS[digit], start=1):
            for col, pixel in enumerate(glyph_row):
                if pixel == "1":
                    frame[row, col_offset + col] = SCREEN_COLOR
    return frame


last_screen = None
last_percent = None
try:
    while True:
        memory_percent = int(psutil.virtual_memory().percent)
        if memory_percent != last_percent:
            print(f"System memory: {memory_percent}%")
            last_percent = memory_percent
        frame = memory_frame(memory_percent)
        screen = frame.tobytes()
        if screen != last_screen:
            print(f"System memory: {memory_percent}%")
            exec(DotMatrixAnimation(frame=[frame], speed=100))
            last_screen = screen
        time.sleep(1)
except KeyboardInterrupt:
    print("Memory monitor stopped")
