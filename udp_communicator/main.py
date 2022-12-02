from src.interface import Interface
from src.server import Server
from src.client import Client

#var = (250).to_bytes(1, 'big')
#x = int.from_bytes(var, 'big')

ip = ""
port = 0

entity_type = -1

def initialize_program(settings: (bool | None) = None) -> int:
    global_vars = globals()

    if settings == None:
        app_type = Interface.entity_menu_choice('init')

        if app_type == 1:
            global_vars['ip'], global_vars['port'] = Interface.initialize_entity("client")

            return init_client(global_vars['ip'], global_vars['port'])
        elif app_type == 2:
            global_vars['ip'], global_vars['port'] = Interface.initialize_entity("server")

            return init_server(global_vars['ip'], global_vars['port'])
        else:
            return 0
    elif settings:
        return init_client(global_vars['ip'], global_vars['port'])
    else:
        return init_server(global_vars['ip'], global_vars['port'])

def init_client(ip: str, port: int) -> int:
    client = Client(ip, port)
    return client.call_client()

def init_server(ip: str, port: int) -> int:
    server = Server(ip, port)
    return server.call_server()

while True:
    if entity_type == 1:
        Interface.chmod_console_output("server", "client")
        entity_type = initialize_program(True)
    elif entity_type == 2:
        Interface.chmod_console_output("client", "server")
        entity_type = initialize_program(False)
    elif entity_type == 0:
        break
    else:
        entity_type = initialize_program()

print('***Program shutdown***')