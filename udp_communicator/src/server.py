from . import addresses as ad
from .signal_types import Signals
from .interface import Interface
from .general import General

from zlib import crc32
import socket
import os

class Server (General):

    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)

        self.save_path = os.path.abspath("received")
        self.connected_client = False

    def call_server(self) -> int:
        self.init_socket()
        self.entity_socket.bind(self.adresses)
        Interface.server_init_console_output(self.adresses)

        while True:
            if self.connected_client:
                self.entity_socket.settimeout(5.5)
            try:
                data, addr = self.entity_socket.recvfrom(self.buffer_size)
                self.entity_socket.settimeout(None)
            except socket.error:
                print("server - keepalive packet did not arrive")
                self.keepalive_counter += 1

                if self.keepalive_counter > 4:
                    print("server - aborted connection due to inactivity")
                    return -1

            if not self.connected_client and int.from_bytes(data[: 1], 'big') == Signals.SYN.value:
                self.reply_change_connection(data[: 1], addr)
                self.connected_client = True
                ad.foreign_ip, ad.foreign_port = addr
                print("server - successful connection with client")

            elif self.connected_client and int.from_bytes(data[: 1], 'big') == Signals.FIN.value:
                self.reply_change_connection(data[: 1], addr)
                self.connected_client = False
                print("server - successful disconnection of client")
                
            elif self.connected_client and int.from_bytes(data[: 1], 'big') == Signals.SWITCH.value:
                self.request_change_connection(Signals.FIN, (ad.foreign_ip, ad.foreign_port))
                print("server - successful disconnection of client")
                return 1

            elif self.connected_client and int.from_bytes(data[: 1], 'big') == Signals.DATA_INIT.value:
                self.send_packet(self.eval_sig(data[: 1]).value, addr)
                self.init_transfer(data)

            elif self.connected_client and int.from_bytes(data[: 1], 'big') == Signals.KEEP_ALIVE.value:
                self.keepalive_counter = 0
                self.send_packet(self.eval_sig(data[: 1]).value, addr)
                print("server - received keepalive from client")
            data = b'\n'

    def init_transfer(self, data: bytes) -> None:
        dec_packet = self.decode_data_packet(data)
        dec_packet[3] = dec_packet[3].decode()
        Interface.transfer_console_output("text" if dec_packet == "text" else "file", dec_packet[2])
        received_content, size = self.receive_data(dec_packet[1], dec_packet[2])

        if size == 0:
            return
        elif dec_packet[3] == "text":
            Interface.stext_console_output(received_content.decode(), size, dec_packet[2])
        else:
            output_path = "{}\{}".format(self.save_path, dec_packet[3])
            with open(output_path, "wb") as out_file:
                out_file.write(received_content)
            Interface.sfile_console_output(dec_packet[3], size, output_path, dec_packet[2])

    def receive_data(self, transfer_id: int, fragments: int) -> tuple[bytearray, int]:
        received, length = bytearray(), 0

        for index in range(0, fragments):
            counter = 0

            while True:
                try:
                    self.entity_socket.settimeout(5.0)
                    data, addr = self.entity_socket.recvfrom(self.buffer_size)
                    self.entity_socket.settimeout(None)
                except socket.error:
                    counter += 1
                    print(f"server - packet { index + 1 }/{ fragments } did not arrive")

                    if counter > 4:
                        return (received, 0)
                    continue
                packet = self.decode_data_packet(data)

                if crc32(packet[3]) == packet[4] and packet[1] == transfer_id and index + 1 == packet[2]:
                    print(f"server - packet { index + 1 }/{ fragments } correct - { len(packet[3]) }B")
                    length += len(packet[3])
                    self.send_packet(self.eval_sig(data[: 1]).value, addr)
                    received.extend(packet[3])
                    break
                elif crc32(packet[3]) == packet[4] and packet[1] == transfer_id and index + 1 > packet[2]:
                    print(f"server - packet { index + 1 }/{ fragments } already received")
                    self.send_packet(self.eval_sig(data[: 1]).value, addr)
                else:
                    print(f"server - packet { index + 1 }/{ fragments } error in data")
                    self.send_packet(Signals.ERROR.value, addr)
        return (received, length)