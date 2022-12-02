from .signal_types import Signals

import socket

class General:

    def __init__(self, ip: str, port: int) -> None:
        self.adresses = (ip, port)
        self.buffer_size = 1518

    def init_socket(self) -> None:
        self.entity_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

    def send_sig(self, type: int, address: tuple[str, int]) -> None:
        packet = bytes()

        match type:
            case 0 | 1 | 2 | 3 | 4 | 5 | 6 | 9:
                packet = type.to_bytes(2, 'big')
            case _:
                pass
        self.entity_socket.sendto(packet, address)


    def eval_sig(self, signal: bytes) -> Signals:
        signal_type = int.from_bytes(signal, 'big')

        match signal_type:
            case 0:
                return Signals.SYN_ACK
            case 4:
                return Signals.FIN_ACK
            case 6:
                return Signals.DATA
            case 1 | 3 | 5 | 7 | 8:
                return Signals.ACK

    def encode_packet(self) -> None:
        pass

    def request_change_connection(self, signal: Signals, addr: tuple[str, int]) -> None:
        self.send_sig(signal.value, addr)
        data, addr = self.entity_socket.recvfrom(self.buffer_size)
        self.send_sig(self.eval_sig(data[: 2]).value, addr)

    def reply_change_connection(self, signal: bytes, addr: tuple[str, int]) -> None:
        self.send_sig(self.eval_sig(signal).value, addr)
        data, addr = self.entity_socket.recvfrom(self.buffer_size)