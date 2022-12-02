import socket

class General:

    def __init__(self, ip: str, port: int) -> None:
        self.ip_addr = ip
        self.port = port

    def send_sig(self) -> None:
        pass

    def eval_sig(self) -> None:
        pass

    def end_connection(self) -> None:
        pass