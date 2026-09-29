import socket

address = ("localhost")

with socket.create_connection(address) as client:

 # Pedir al usuario el comando
    command = input("Escribe un comando: ")

    # Enviar el comando al servidor
    client.sendall(f"{command}\n".encode("utf-8"))

    # Crear una interfaz de lectura para recibir texto
    reader = client.makefile("r", encoding="utf-8")

    # Leer la primera línea de la respuesta
    status = reader.readline().strip()
    
    