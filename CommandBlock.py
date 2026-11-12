from abc import abstractmethod


def pad(data: list[int]) -> list[int]:
    padding_len = 64 - len(data)
    data.extend(b"\x00" * padding_len)
    return data


class CommandBlock:
    def __init__(self, operand: int):
        self.operand = operand

    def get_common_command_byte(self, command: list[int]) -> bytes:
        packet = [0xAA, self.operand]
        packet.extend(command)
        return bytes(pad(packet))

    def get_common_response_byte(self, expectation: list[int]) -> bytes:
        packet = [0x55, self.operand]
        packet.extend(expectation)
        return bytes(pad(packet))

    @abstractmethod
    def command(self) -> bytes:
        pass

    @abstractmethod
    def expect(self) -> bytes:
        pass

class RGBColor:
    def __init__(self, hx: str):
        if len(hx) != 6:
            raise ValueError("RGB hex code is not valid")

        self.color = [
            int(hx[0:2], 16),
            int(hx[2:4], 16),
            int(hx[4:6], 16)
        ]
