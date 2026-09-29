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


def download():
    filename = input("Nombre del archivo que quieres descargar: ")

    with socket.create_connection(ADDRESS) as client:
        client.sendall(f"DOWNLOAD {filename}\n".encode("utf-8"))

        header = read_line(client)

        if not header.startswith("OK "):
            print("Servidor:", header)
            return

        _, size_text, expected_hash = header.split()
        size = int(size_text)

        path = Path(filename)
        received = 0
        digest = hashlib.sha256()

        with open(path, "wb") as file:
            while received < size:
                amount = min(BUFFER_SIZE, size - received)
                chunk = client.recv(amount)

                if not chunk:
                    raise ConnectionError("Descarga incompleta")

                file.write(chunk)
                digest.update(chunk)
                received += len(chunk)

        if digest.hexdigest() != expected_hash:
            path.unlink(missing_ok=True)
            print("Error: el checksum no coincide.")
            return

        print(f"Descarga completada: {path}")
def list_files():
    with socket.create_connection(ADDRESS) as client:
        client.sendall(b"LIST\n")

        status = read_line(client)
        print("Estado:", status)

        if status == "OK":
            print("Archivos disponibles:")

            while True:
                line = read_line(client)

                if line == ".":
                    break

                print("-", line)
while True:
    command = input("\nComando (LIST, UPLOAD, DOWNLOAD, EXIT): ")
    command = command.strip().upper()

    try:
        if command == "LIST":
            list_files()

        elif command == "UPLOAD":
            upload()

        elif command == "DOWNLOAD":
            download()

        elif command == "EXIT":
            print("Cliente cerrado.")
            break

        else:
            print("Comando desconocido.")

    except (ConnectionError, OSError, ValueError) as error:
        print("Error:", error)


  