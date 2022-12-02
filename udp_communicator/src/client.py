from .signal_types import Signals
from .interface import Interface
from .general import General

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
                self.send_sig(Signals.SWITCH.value, self.adresses)
                data, addr = self.entity_socket.recvfrom(self.buffer_size)

                if int.from_bytes(data[: 2], 'big') == Signals.FIN.value:
                    self.reply_change_connection(data[: 2], addr)

                    print("client - successful disconnection from server")
                return value
            else:
                self.init_transfer()

    def init_transfer(self) -> None:
        while True:
            try:
                value = int(input("Enter max fragment size (1-1458): "))
            except ValueError:
                print("Not a number")
                continue
            
            if value > 0 and value < 1459:
                self.max_frag_size = value
                break
            else:
                print("Invalid choice")

        while True:
            value = Interface.entity_menu_choice('transfer')

            if value == 0:
                return
            elif value == 1:
                self.send_sig(Signals.DATA_INIT.value, self.adresses)
                self.text_transfer()
            else:
                self.file_transfer()

    def text_transfer(self) -> None:
        text_content = str.encode(input("Enter text: "))

    def file_transfer(self) -> None:
        pass