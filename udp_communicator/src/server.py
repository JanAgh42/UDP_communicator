from .signal_types import Signals
from .general import General

class Server (General):

    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)

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
                pass
