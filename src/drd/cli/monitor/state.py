import enum


class ServerState(enum.Enum):
    NORMAL = 1
    ERROR_DETECTED = 2
    ERROR_HANDLING = 3
    FIX_APPLYING = 4
