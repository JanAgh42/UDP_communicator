from .signal_types import Signals

from zlib import crc32
import socket

class General:

    def __init__(self, ip: str, port: int) -> None:
        self.adresses = (ip, port)
        self.buffer_size = 1518

    def init_socket(self) -> None:
        self.entity_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

    def send_packet(self, type: int, address: tuple[str, int], data_info: list = list()) -> None:
        packet = bytearray()

        match type:
            case 0 | 1 | 2 | 3 | 4 | 5 | 6 | 9:
                packet = type.to_bytes(2, 'big')
            case 7 | 8:
                packet.extend(type.to_bytes(2, 'big'))
                packet.extend(data_info[0].to_bytes(2, 'big'))
                packet.extend(data_info[1].to_bytes(4, 'big'))
                packet.extend(data_info[2].to_bytes(2, 'big'))
                packet.extend(data_info[3])
                packet.extend(crc32(data_info[3]).to_bytes(4, 'big'))
                
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

    def decode_data_packet(self, packet: bytes) -> list:
        decoded_packet = list()

        decoded_packet.append(int.from_bytes(packet[: 2], 'big'))
        decoded_packet.append(int.from_bytes(packet[2 : 4], 'big'))
        decoded_packet.append(int.from_bytes(packet[4 : 8], 'big'))
        decoded_packet.append(int.from_bytes(packet[8 : 10], 'big'))
        decoded_packet.append(packet[10 : -4])
        decoded_packet.append(int.from_bytes(packet[-4 :], 'big'))

        return decoded_packet

    def request_change_connection(self, signal: Signals, addr: tuple[str, int]) -> None:
        self.send_packet(signal.value, addr)
        data, addr = self.entity_socket.recvfrom(self.buffer_size)
        self.send_packet(self.eval_sig(data[: 2]).value, addr)

    def reply_change_connection(self, signal: bytes, addr: tuple[str, int]) -> None:
        self.send_packet(self.eval_sig(signal).value, addr)
        data, addr = self.entity_socket.recvfrom(self.buffer_size)