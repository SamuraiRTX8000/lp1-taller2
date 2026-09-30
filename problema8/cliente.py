import socket

cliente = socket.socket()
cliente.connect(("localhost", 8080))

# Recibir identificación
mensaje = cliente.recv(1024).decode()

print(mensaje)

