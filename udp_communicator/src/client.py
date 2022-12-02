from .interface import Interface
from .general import General

import socket

class Client (General):
    
    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)

        self.msg_from_client = "Hello UDP Server"
        self.bytes_to_send = str.encode(self.msg_from_client)
        self.buffer_size = 1024

    def call_client(self) -> int:
        self.client_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

        self.init_connection()

        while True:
            value = Interface.entity_menu_choice('client')

            if value == 0 or value == 2:
                return value
            else:
                self.init_transfer()

    def init_connection(self) -> None:
        pass

    def init_transfer(self) -> None:
        pass

    def send_packet(self) -> None:
        pass


        # udp_client_socket.sendto(self.bytes_to_send, self.server_address_port)

        # msg_from_server = udp_client_socket.recvfrom(self.buffer_size)

        # msg = "Message from Server {}".format(msg_from_server[0])

        # print(msg)