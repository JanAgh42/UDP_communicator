from .signal_types import Signals
from .interface import Interface
from .general import General

from zlib import crc32

class Server (General):

    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)

        self.save_path = "C:\\Users\\Public\\FIIT STU\\Predmety_sem5\\Počítačové a komunikačné siete\\zadanie2\\udp_communicator\\received"

        self.connected_client = False

    def call_server(self) -> int:
        self.init_socket()
        self.entity_socket.bind(self.adresses)
        Interface.server_init_console_output(self.adresses)

        while True:
            data, addr = self.entity_socket.recvfrom(self.buffer_size)

            if not self.connected_client and int.from_bytes(data[: 1], 'big') == Signals.SYN.value:
                self.reply_change_connection(data[: 1], addr)
                self.client_addr = addr
                self.connected_client = True
                print("server - successful connection with client")

            elif self.connected_client and int.from_bytes(data[: 1], 'big') == Signals.FIN.value:
                self.reply_change_connection(data[: 1], addr)
                self.connected_client = False
                print("server - successful disconnection of client")
                
            elif self.connected_client and int.from_bytes(data[: 1], 'big') == Signals.SWITCH.value:
                self.request_change_connection(Signals.FIN, self.client_addr)
                self.entity_socket.close()
                print("server - successful disconnection of client")
                return 1

            elif self.connected_client and int.from_bytes(data[: 1], 'big') == Signals.DATA_INIT.value:
                self.send_packet(self.eval_sig(data[: 1]).value, addr)
                self.init_transfer(data)

            elif self.connected_client and int.from_bytes(data[: 1], 'big') == Signals.KEEP_ALIVE.value:
                self.send_packet(self.eval_sig(data[: 1]).value, addr)
                print("server - received keepalive from client")

    def init_transfer(self, data: bytes) -> None:
        dec_packet = self.decode_data_packet(data)
        dec_packet[3] = dec_packet[3].decode()
        Interface.transfer_console_output("text" if dec_packet == "text" else "file", dec_packet[2])

        if dec_packet[3] == "text":
            message_content, size = self.receive_data(dec_packet[2])
            Interface.text_console_output(message_content.decode(), size)
        else:
            file_content, size = self.receive_data(dec_packet[2])
            output_path = "{}/{}".format(self.save_path, dec_packet[3])

            with open(output_path, "wb") as out_file:
                out_file.write(file_content)

            Interface.file_console_output(dec_packet[3], size, output_path)

    def receive_data(self, fragments: int) -> tuple[bytearray, int]:
        received = bytearray()
        length = 0

        for index in range(0, fragments):
            while True:
                data, addr = self.entity_socket.recvfrom(self.buffer_size)

                packet = self.decode_data_packet(data)

                if crc32(packet[3]) == packet[4]:
                    print(f"server - packet { index + 1 }/{ fragments } correct - { len(packet[3]) }B")
                    length += len(packet[3])
                    self.send_packet(self.eval_sig(data[: 1]).value, addr)
                    received.extend(packet[3])
                    break
                else:
                    print(f"server - packet { index + 1 }/{ fragments } error in data")
                    self.send_packet(Signals.ERROR.value, addr)

        return (received, length)