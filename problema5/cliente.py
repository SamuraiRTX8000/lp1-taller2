import socket
import hashlib
from pathlib import Path

ADDRESS = ("localhost", 8000)
BUFFER_SIZE = 4096
#permite leer las respuestas del server

def read_line(conn):
    data = bytearray()

    while True:
        byte = conn.recv(1)

        if not byte:
            raise ConnectionError("Conexión cerrada")

        if byte == b"\n":
            return data.decode("utf-8")

        data.extend(byte)


    