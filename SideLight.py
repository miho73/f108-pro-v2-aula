import enum

from CommandBlock import CommandBlock, RGBColor

class SideLightMode(enum.Enum):
    LightFlow = 1
    Static = 2
    DynamicBreathing = 3
    SpectrumCycle = 4
    OFF = 5
    Lively = 6
    ChainReaction = 7

class SideLight(CommandBlock):
    def __init__(
            self,
            effect_mode: SideLightMode,
            color: RGBColor,
            brightness: int,
            speed: int,
            color_mode: int = 0
    ):
        if not (1 <= brightness <= 5) or not (1 <= speed <= 5):
            raise ValueError("Brightness and speed must be between 1 and 5")

        super().__init__(operand=0x2B)

        self.effect_mode = effect_mode
        self.color = color
        self.brightness = brightness
        self.speed = speed
        self.color_mode = color_mode

    def command(self) -> bytes:
        cmd = [0x18, 0x00, 0x00, 0x00, 0x01, 0x00, self.effect_mode.value]
        cmd.extend(self.color.color)
        cmd.extend([0x00, 0x00, 0x00, 0x00, self.color_mode, self.brightness, self.speed])
        return super().get_common_command_byte(cmd)

    def expect(self) -> bytes:
        cmd = [0x18, 0x00, 0x00, 0x00, 0x01, 0x00, self.effect_mode.value]
        cmd.extend(self.color.color)
        cmd.extend([0x00, 0x00, 0x00, 0x00, self.color_mode, self.brightness, self.speed])
        return super().get_common_response_byte(cmd)