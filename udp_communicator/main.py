import src.addresses as addr
from src.interface import Interface
from src.server import Server
from src.client import Client

from time import sleep

entity_type = -1

def initialize_application(settings: (bool | None) = None) -> int:
    if settings == None:
        app_type = Interface.entity_menu_choice('init')

        if app_type == 1:
            addr.foreign_ip, addr.foreign_port = Interface.initialize_entity("client")
            return init_client(addr.foreign_ip, addr.foreign_port)
        elif app_type == 2:
            addr.own_ip, addr.own_port = Interface.initialize_entity("server")
            return init_server(addr.own_ip, addr.own_port)
        else:
            return 0
    elif settings:
        return init_client(addr.foreign_ip, addr.foreign_port, True)
    else:
        return init_server(addr.own_ip, addr.own_port)

def init_client(ip: str, port: int, switch: bool = False) -> int:
    client = Client(ip, port)
    return client.call_client(switch)

def init_server(ip: str, port: int) -> int:
    server = Server(ip, port)
    return server.call_server()

while True:
    if entity_type == 1:
        sleep(1.4)
        Interface.chmod_console_output("server", "client")
        entity_type = initialize_application(True)
    elif entity_type == 2:
        sleep(.7)
        Interface.chmod_console_output("client", "server")
        entity_type = initialize_application(False)
    elif entity_type == 0:
        break
    else:
        entity_type = initialize_application()

print('***Application shutdown***')