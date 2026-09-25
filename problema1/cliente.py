#!/usr/bin/env python3
"""
Problema 1: Sockets básicos - Cliente
Objetivo: Crear un cliente TCP que se conecte a un servidor e intercambie mensajes básicos
"""

import socket


cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)


cliente_socket.connect(("localhost", 8000))

#envia el mensaje al servidor y codifica el mensaje en bytes antes de enviarlo
mensaje = input("Ingrese un mensaje para enviar al servidor: ")
cliente_socket.sendall(mensaje.encode())

# sendall() asegura que todos los datos sean enviados

# Recibe la respuesta del servidor y decodifica el mensaje de bytes a string
mensaje_recibido = cliente_socket.recv(1024)

print("Mensaje del servidor:", mensaje_recibido.decode())

#cierra el socket del cliente
cliente_socket.close()


