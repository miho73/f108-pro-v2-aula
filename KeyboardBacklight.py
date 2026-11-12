import enum

from CommandBlock import CommandBlock, RGBColor

class KeyboardBacklightMode(enum.Enum):
    OFF = 0
    Static = 1
    SinglePointOn = 2
    SinglePointOff = 3
    StarrySky = 4
    Snowfall = 5
    Blooming = 6
    DynamicBreathing = 7
    SpectrumCycle = 8
    ColorfulSprig = 9
    ColorfulCross = 10
    Drifting = 11
    PeakReturn = 12
    InstantTrigger = 13
    DualAction = 14
    RippleSpread = 15
    FlowingStream = 16
    MountainLayers = 17
    GentleRain = 18
    Shuttle = 19


class KeyboardBacklight(CommandBlock):
    def __init__(
            self,
            brightness: int,
            light_mode: KeyboardBacklightMode,
            speed: int,
            color: RGBColor,
            colorful_effects: bool,
            reverse_effects: bool,
            secondary_color: RGBColor = RGBColor("000000"),
            effect_mode_type: int = 0
    ):
        if not (1 <= brightness <= 5) or not (1 <= speed <= 5):
            raise ValueError("Brightness and speed must be between 1 and 5")

        super().__init__(operand=0x23)
        self.brightness = brightness
        self.light_mode = light_mode.value
        self.speed = speed
        self.color = color
        self.colorful_effects = colorful_effects
        self.reverse_effects = reverse_effects
        self.secondary_color = secondary_color
        self.effect_mode_type = effect_mode_type

    def command(self) -> bytes:
        head = [0x10, 0x00, 0x00, 0x00, 0x01, 0x00, self.light_mode]
        head.extend(self.color.color)
        head.extend(self.secondary_color.color)
        head.extend([0xFF, 0x01 if self.colorful_effects else 0x00, self.brightness, self.speed, 0x01 if self.reverse_effects else 0x00, self.effect_mode_type, 0x00, 0xAA, 0x55])
        return super().get_common_command_byte(head)

    def expect(self) -> bytes:
        head = [0x10, 0x00, 0x00, 0x00, 0x01, 0x00, self.light_mode]
        head.extend(self.color.color)
        head.extend(self.secondary_color.color)
        head.extend([0xFF, 0x01 if self.colorful_effects else 0x00, self.brightness, self.speed, 0x01 if self.reverse_effects else 0x00, self.effect_mode_type, 0x00, 0xAA, 0x55])
        return super().get_common_response_byte(head)
