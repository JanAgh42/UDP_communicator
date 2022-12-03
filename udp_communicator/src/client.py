from .signal_types import Signals
from .interface import Interface
from .general import General

from math import ceil
import random
import socket
import os

class Client (General):
    
    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)

        self.max_frag_size = 1458

    def call_client(self) -> int:
        self.init_socket()
        self.request_change_connection(Signals.SYN, self.adresses)

        print("client - successful connection with server")

        while True:
            value = Interface.entity_menu_choice('client')

            if value == 0:
                self.request_change_connection(Signals.FIN, self.adresses)

                print("client - successful disconnection from server")

                return value - 1
            elif value == 2:
                self.send_packet(Signals.SWITCH.value, self.adresses)
                data, addr = self.entity_socket.recvfrom(self.buffer_size)

                if int.from_bytes(data[: 2], 'big') == Signals.FIN.value:
                    self.reply_change_connection(data[: 2], addr)

                    print("client - successful disconnection from server")
                return value
            else:
                self.init_transfer()

    def init_transfer(self) -> None:
        self.max_frag_size = Interface.load_fragment_size()

        while True:
            value = Interface.entity_menu_choice('transfer')

            if value == 0:
                return
            elif value == 1:
                text_content = str.encode(input("Enter text: "))
                transfer_id = random.randint(1, 65535)
                size = len(text_content)

                header = [transfer_id, ceil(size / self.max_frag_size), size, str.encode("text")]

                self.send_packet(Signals.DATA_INIT.value, self.adresses, header)
                data, addr = self.entity_socket.recvfrom(self.buffer_size)

                if int.from_bytes(data[: 2], 'big') == Signals.ACK.value:
                    print("client - beginning of text transfer")
                    self.transfer_data(data[: 2], addr, text_content, header)
            else:
                file_name = input("Enter file name: ")
                file_path = os.path.abspath(file_name)[: - file_name.__len__()] + "send\\" + file_name

                with open(file_path, "rb") as file:
                    file_content = file.read()
                    transfer_id = random.randint(1, 65535)
                    size = len(file_content)

                    header = [transfer_id, ceil(size / self.max_frag_size), size, str.encode(file_name)]

                    self.send_packet(Signals.DATA_INIT.value, self.adresses, header)
                    data, addr = self.entity_socket.recvfrom(self.buffer_size)

                    if int.from_bytes(data[: 2], 'big') == Signals.ACK.value:
                        print("client - beginning of file transfer")
                        self.transfer_data(data[: 2], addr, file_content, header)

    def transfer_data(self, signal: bytes, addr: tuple[str, int], data: bytes, header: list) -> None:
        packets = self.create_fragments(data, header)

        for packet in packets:
            while True:
                self.send_packet(Signals.DATA.value, self.adresses, packet)

                try:
                    self.entity_socket.settimeout(5.0)
                    data, addr = self.entity_socket.recvfrom(self.buffer_size)
                    self.entity_socket.settimeout(None)

                    if int.from_bytes(data[: 2], 'big') == Signals.ACK.value:
                        print("client - delivered packet")
                        break
                    elif int.from_bytes(data[: 2], 'big') == Signals.ERROR.value:
                        print("client - re-sending latest packet - error")
                except socket.error:
                    print("client - re-sending latest packet - no server response")

    def create_fragments(self, content: bytes, header: list) -> list:
        fragmented_packets = list()
        begin = 0
        end = self.max_frag_size

        for index in range(0, header[1]):
            data = content[begin : end if index != header[1] - 1 else content.__len__()]

            fragmented_packets.append([header[0], index + 1, len(data), data])

            begin += self.max_frag_size
            end += self.max_frag_size
        
        return fragmented_packets