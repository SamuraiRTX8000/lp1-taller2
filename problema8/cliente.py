import socket

cliente = socket.socket()
cliente.connect(("localhost", 8080))

# Recibir identificación
mensaje = cliente.recv(1024).decode()

print(mensaje)

# Saber si somos jugador
es_jugador = "JUGADOR" in mensaje

while True:

    if es_jugador:

        posicion = input("Elige una posicion (1-9): ")

        cliente.sendall(posicion.encode())

    mensaje = cliente.recv(1024).decode()

    if not mensaje:
        break

    print(mensaje)

