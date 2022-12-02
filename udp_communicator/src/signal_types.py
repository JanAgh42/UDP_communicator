from enum import Enum

class Signals (Enum):
    SYN = 0
    SYN_ACK = 1
    ACK = 2
    KEEP_ALIVE = 3
    FIN = 4
    FIN_ACK = 5
    ERROR = 6
    DATA_INIT = 7
    DATA = 8
    SWITCH = 9