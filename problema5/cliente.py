import socket

address = ("localhost", 8000)

with socket.create_connection(address) as client:

 # Pedir al usuario el comando
    command = input("Escribe un comando: ")

    # Enviar el comando al servidor
    client.sendall(f"{command}\n".encode("utf-8"))

    # Crear una interfaz de lectura para recibir texto
    reader = client.makefile("r", encoding="utf-8")

    # Leer la primera línea de la respuesta
    status = reader.readline().strip()

    print("Estado:", status)

    # Si el servidor respondió OK
    if status == "OK":

        print("Archivos disponibles:")

        while True:

            line = reader.readline()

            if not line:
                print("Conexión cerrada inesperadamente.")
                break

            filename = line.strip()

            if filename == ".":
                break

            print("-", filename)

    