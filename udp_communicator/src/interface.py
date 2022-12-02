import socket

class Interface:

    @staticmethod
    def entity_menu_choice(type: str) -> int:
        prompt = 'Client(1) Server(2) Exit(0): ' if type == 'init' else 'Transfer(1) Change mode(2) Exit(0): '
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

        ip_address = ""
        port = 0

        if type == "client":
            while True:
                try:
                    ip_address = input(f"Enter server IP address ({ type } side): ")
                    socket.inet_aton(ip_address)
                except socket.error:
                    print("Invalid IP address")
                    continue
                break
            
        while True:
            try:
                port = int(input(f"Enter server port ({ type } side): "))
            except ValueError:
                print("Invalid port")
                continue
            
            if port > 0 and port < 65536:
                break
        print("------------------------------------------------")

        return (ip_address if ip_address != "" else socket.gethostbyname(socket.gethostname()), port)

    @staticmethod
    def chmod_console_output(first: str, second: str) -> None:
        print(f"Changing mode from { first } to { second }...")
        print("------------------------------------------------ ")