from .general import General

import socket

class Server (General):

    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)

        self.buffer_size  = 1024
        self.msg_from_server = "Hello UDP Client"
        self.bytes_to_send = str.encode(self.msg_from_server)

    def call_server(self) -> None:
        udp_server_socket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

        udp_server_socket.bind((self.ip_addr, self.port))

        print("UDP server up and listening")

        while(True):
            bytes_address_pair = udp_server_socket.recvfrom(self.buffer_size)

            message = bytes_address_pair[0]

            address = bytes_address_pair[1]

            client_msg = "Message from Client:{}".format(message)
            client_ip  = "Client IP Address:{}".format(address)
            
            print(client_msg)
            print(client_ip)

            udp_server_socket.sendto(self.bytes_to_send, address)

    def receive_packet(self) -> None:
        pass