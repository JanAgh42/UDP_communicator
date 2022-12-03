from .signal_types import Signals
from .interface import Interface
from .general import General

from zlib import crc32
import os

class Server (General):

    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)

        self.save_path = "C:\\Users\\Public\\FIIT STU\\Predmety_sem5\\Počítačové a komunikačné siete\\zadanie2\\udp_communicator\\received"

        self.connected_client = False

    def call_server(self) -> int:
        self.init_socket()

        self.entity_socket.bind(self.adresses)

        print("Server addresses:", self.adresses)
        print("UDP server up and listening...")

        while True:
            data, addr = self.entity_socket.recvfrom(self.buffer_size)

            if not self.connected_client and int.from_bytes(data[: 2], 'big') == Signals.SYN.value:
                self.reply_change_connection(data[: 2], addr)
                self.client_addr = addr
                self.connected_client = True
    
                print("server - successful connection with client")
            elif self.connected_client and int.from_bytes(data[: 2], 'big') == Signals.FIN.value:
                self.reply_change_connection(data[: 2], addr)
                self.connected_client = False
    
                print("server - successful disconnection of client")
            elif self.connected_client and int.from_bytes(data[: 2], 'big') == Signals.SWITCH.value:
                self.request_change_connection(Signals.FIN, self.client_addr)

                print("server - successful disconnection of client")
                return 1
            elif self.connected_client and int.from_bytes(data[: 2], 'big') == Signals.DATA_INIT.value:
                self.send_packet(self.eval_sig(data[: 2]).value, addr)
                self.init_transfer(data)
            else:
                print("server - couldn't recognize signal")

    def init_transfer(self, data: bytes) -> None:
        dec_packet = self.decode_data_packet(data)
        dec_packet[4] = dec_packet[4].decode()

        Interface.transfer_console_output("text" if dec_packet == "text" else "file", dec_packet[2])

        if dec_packet[4] == "text":
            message_content = self.receive_data(dec_packet[2])

            print(f"server - message from client: { message_content.decode() }")
            print(f"server - size of message: { dec_packet[3] }B")
        else:
            file_content = self.receive_data(dec_packet[2])
            output_path = "{}/{}".format(self.save_path, dec_packet[4])

            with open(output_path, "wb") as out_file:
                out_file.write(file_content)

            print(f"server - file from client: { dec_packet[4] }")
            print(f"server - size of file: { dec_packet[3] }B")
            print(f"server - saved at: { output_path }")

    def receive_data(self, fragments: int) -> bytearray:
        received = bytearray()

        for index in range(0, fragments):
            while True:
                data, addr = self.entity_socket.recvfrom(self.buffer_size)
                packet = self.decode_data_packet(data)

                if crc32(packet[4]) == packet[5]:
                    print(f"server - packet { index + 1 }/{ fragments } correct - { packet[3] }B")
                    self.send_packet(self.eval_sig(data[: 2]).value, addr)
                    received.extend(packet[4])
                    break
                else:
                    print(f"server - packet { index + 1 }/{ fragments } error")
                    self.send_packet(Signals.ERROR.value, addr)
        return received