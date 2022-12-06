import socket

class Interface:

    @staticmethod
    def entity_menu_choice(type: str) -> int:
        match type:
            case 'init':
                prompt = 'Client(1) Server(2) Exit(0): '
            case 'client':
                prompt = 'Transfer(1) Change mode(2) Exit(0): '
            case 'error':
                prompt = 'With error(1) Without error(2) Exit(0): '
            case _:
                prompt = 'Message(1) File(2) Exit(0): '
        value = 0

        while True:
            try:
                value = int(input(prompt))
            except ValueError:
                print("Not a number")
                continue
            
            if value == 0 or value == 1 or value == 2:
                break
            else:
                print("Invalid choice")

        return value

    @staticmethod
    def initialize_entity(type: str) -> tuple[str, int]:
        print(f'----{ type } initialization----')

        ip_address, pc_ip_addr, port = "", "", 0

        while True:
            try:
                if type == "server":
                    pc_ip_addr = socket.gethostbyname(socket.gethostname())

                ip_address = input(f"Enter server IP address ({ type } side { pc_ip_addr }): ")

                octets = ip_address.split('.')
                validation = all(0 < len(octet) < 4 and 0 <= int(octet) < 256 for octet in octets)

                if (len(octets) == 4 and validation) or (ip_address == "" and type == "server"):
                    break
            except (ValueError, AttributeError, TypeError):
                print("Invalid IP address")
            
        while True:
            try:
                port = int(input(f"Enter server port ({ type } side): "))
            except ValueError:
                print("Invalid port")
                continue
            
            if port > 0 and port < 65536:
                break
        print("------------------------------------------------")

        return (ip_address if ip_address != "" or type != "server" else pc_ip_addr, port)

    @staticmethod
    def load_fragment_size() -> int:
        value = 1458

        while True:
            try:
                value = int(input("Enter max fragment size (1-1460): "))
            except ValueError:
                print("Not a number")
                continue
            
            if value >= 1 and value <= 1460:
                break
            else:
                print("Invalid choice")

        return value

    @staticmethod
    def chmod_console_output(first: str, second: str) -> None:
        print(f"Changing mode from { first } to { second }...")
        print("------------------------------------------------")

    @staticmethod
    def transfer_console_output(name: str, num: int) -> None:
        print("------------------------------------------------")
        print(f"server - initialized { name } transfer with { num } fragments")
    
    @staticmethod
    def text_console_output(message: str, size: int) -> None:
        print("------------------------------------------------")
        print(f"server - message from client: { message }")
        print(f"server - size of message: { size }B")

    @staticmethod
    def file_console_output(name: str, size: int, path: str) -> None:
        print("------------------------------------------------")
        print(f"server - file from client: { name }")
        print(f"server - size of file: { size }B")
        print(f"server - saved at: { path }")

    @staticmethod
    def server_init_console_output(addr: tuple[str, int]) -> None:
        ip, port = addr

        print(f"Server IP: { ip } Server port: { port }")
        print("UDP server up and listening...")