import socket
import threading
import json
import sys

HOST = 'localhost'
#dice que lo que le pase por la terminal lo convierta a entero(lo que va  a ser el server)
PUERTO = int(sys.argv[1])
datos={}

def atender(cliente):
    while True:
        mensaje = cliente.recv(1024).decode()

        if not mensaje:
            break

        datos["ultimo"] = mensaje
        respuesta = json.dumps(datos)
        cliente.send(respuesta.encode())

    cliente.close()

servidor = socket.socket()
servidor.bind((HOST, PUERTO))
servidor.listen()