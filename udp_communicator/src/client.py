from .signal_types import Signals
from .interface import Interface
from .general import General

from time import sleep
from math import ceil
import threading
import random
import socket
import os

class Client (General):
    
    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)

        self.max_frag_size = 1460
        self.keepalive_error_count = 0
        self.run_keepalive = True

    def call_client(self) -> int:
        self.init_socket()
        self.request_change_connection(Signals.SYN, self.adresses)
        print("client - successful connection with server")
        self.init_keepalive()

        while True:
            value = Interface.entity_menu_choice('client')
            
            if value == 0:
                self.request_change_connection(Signals.FIN, self.adresses)
                print("client - successful disconnection from server")
                self.run_keepalive = False
                return value - 1
            elif value == 2:
                self.send_packet(Signals.SWITCH.value, self.adresses)
                data, addr = self.entity_socket.recvfrom(self.buffer_size)

                if int.from_bytes(data[: 1], 'big') == Signals.FIN.value:
                    self.reply_change_connection(data[: 1], addr)
                    self.entity_socket.close()
                    print("client - successful disconnection from server")
                return value
            else:
                self.init_transfer()

    def init_transfer(self) -> None:
        generate_error = Interface.entity_menu_choice('error')

        if generate_error == 0:
            return
        self.max_frag_size = Interface.load_fragment_size()

        while True:
            value = Interface.entity_menu_choice('transfer')

            if value == 0:
                return
            elif value == 1:
                text_content = str.encode(input("Enter text: "))
                self.create_transfer_header(text_content, "text")
            else:
                file_name = input("Enter file name: ")
                file_path = os.path.abspath(file_name)[: - file_name.__len__()] + "send\\" + file_name

                with open(file_path, "rb") as file:
                    file_content = file.read()
                    self.create_transfer_header(file_content, file_name, generate_error)
            self.run_keepalive = True

    def create_transfer_header(self, content: bytes, type: str, error: int = 2) -> None:
        transfer_id = random.randint(1, 65535)
        self.run_keepalive = False
        size = len(content)
        header = [transfer_id, ceil(size / self.max_frag_size), str.encode(type)]
        
        self.send_packet(Signals.DATA_INIT.value, self.adresses, header)
        data, addr = self.entity_socket.recvfrom(self.buffer_size)

        if int.from_bytes(data[: 1], 'big') == Signals.ACK.value:
            print("client - beginning of file transfer")
            if self.transfer_data(content, header, False if error == 2 else True):
                print(f"client - transferred { len(content) }B")

    def transfer_data(self, content: bytes, header: list, error: bool) -> bool:
        packets, counter = self.create_fragments(content, header), 0

        for index, packet in enumerate(packets):
            while True:
                self.send_packet(Signals.DATA.value, self.adresses, packet, error)

                try:
                    self.entity_socket.settimeout(5.0)
                    data, addr = self.entity_socket.recvfrom(self.buffer_size)
                    self.entity_socket.settimeout(None)

                    if int.from_bytes(data[: 1], 'big') == Signals.ACK.value:
                        print(f"client - delivered { index + 1 }/{ packets.__len__() } - { len(packet[2]) }B")
                        break
                    elif int.from_bytes(data[: 1], 'big') == Signals.ERROR.value:
                        print("client - re-sending latest packet - error in data")
                except socket.error:
                    counter += 1
                    print("client - re-sending latest packet - no server response")
                    sleep(5.0)

                    if counter > 2:
                        return False
        return True

    def create_fragments(self, content: bytes, header: list) -> list:
        fragmented_packets = list()
        begin, end = 0, self.max_frag_size

        for index in range(0, header[1]):
            data = content[begin : end if index != header[1] - 1 else content.__len__()]
            fragmented_packets.append([header[0], index + 1, data])

            begin += self.max_frag_size
            end += self.max_frag_size
        
        return fragmented_packets

    def init_keepalive(self) -> None:
        def keep_connection(entity_socket: socket) -> None:
            while True:
                if self.run_keepalive:
                    try:
                        self.send_packet(Signals.KEEP_ALIVE.value, self.adresses)
                    except OSError:
                        return

                    try:
                        entity_socket.settimeout(5.0)
                        data, addr = entity_socket.recvfrom(self.buffer_size)
                        entity_socket.settimeout(None)

                        if int.from_bytes(data[: 1], 'big') == Signals.ACK.value:
                            keepalive_error_count = 0
                    except socket.error:
                        keepalive_error_count += 1
                        print("\nclient - no keepalive response from server")

                        if keepalive_error_count > 2:
                            self.run_keepalive = False
                    sleep(5.0)
                else:
                    sleep(0.5)
        
        self.entity_thread = threading.Thread(target = keep_connection, args = [self.entity_socket])
        self.entity_thread.start()