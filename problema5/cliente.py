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

def calculate_hash(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        while True:
            chunk = file.read(BUFFER_SIZE)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()

def upload():
    path = Path(input("Ruta del archivo que quieres subir: "))

    if not path.is_file():
        print("El archivo no existe.")
        return

    filename = path.name
    size = path.stat().st_size
    checksum = calculate_hash(path)

    with socket.create_connection(ADDRESS) as client:
        command = f"UPLOAD {filename} {size} {checksum}\n"
        client.sendall(command.encode("utf-8"))

        with open(path, "rb") as file:
            while True:
                chunk = file.read(BUFFER_SIZE)

                if not chunk:
                    break

                client.sendall(chunk)

        print("Servidor:", read_line(client))


    