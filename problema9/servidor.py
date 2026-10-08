import socket
import threading

HOST = "localhost"

backends = [
    ("localhost", 5001),
    ("localhost", 5002),
    ("localhost", 5003)
]

actual = 0


def health_check(backend):
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect(backend)
        s.close()
        return True
    except:
        return False
