import socket

servidor = socket.socket()
servidor.connect(("localhost", 5000))

mensaje = input("Escribe un mensaje: ")

servidor.send(mensaje.encode())

respuesta = servidor.recv(1024).decode()

print("Respuesta:", respuesta)

servidor.close()