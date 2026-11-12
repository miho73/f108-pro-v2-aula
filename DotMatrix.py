import enum

from CommandBlock import CommandBlock, RGBColor

class PickupLightMode(enum.Enum):
    CharacterMode = 0
    DanceToLight = 1
    Row = 3
    Column = 2

class DotMatrix(CommandBlock):
    def __init__(
            self,
            bg_color: RGBColor,
            txt_color: RGBColor,
            mode: PickupLightMode = PickupLightMode.CharacterMode,
            type: int = 0,
            dot_matrix_mode: int = 0,
    ):
        super().__init__(operand=0x2A)

        self.bg_hex = bg_color.color
        self.txt_hex = txt_color.color
        self.type = type
        self.mode = mode
        self.dot_matrix_mode = dot_matrix_mode

    def command(self) -> bytes:
        cmd = [0x09, 0x00, 0x00, 0x00, 0x01, 0x00]
        cmd.extend(self.bg_hex)
        cmd.extend(self.txt_hex)
        cmd.extend([self.type, self.mode.value, self.dot_matrix_mode])

        return super().get_common_command_byte(cmd)

    def expect(self) -> bytes:
        cmd = [0x09, 0x00, 0x00, 0x00, 0x01, 0x00]
        cmd.extend(self.bg_hex)
        cmd.extend(self.txt_hex)
        cmd.extend([self.type, self.mode.value, self.dot_matrix_mode])

        return super().get_common_response_byte(cmd)
