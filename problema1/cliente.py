#!/usr/bin/env python3
"""
Problema 1: Sockets básicos - Cliente
Objetivo: Crear un cliente TCP que se conecte a un servidor e intercambie mensajes básicos
"""

import socket

# TODO: Crear un socket TCP/IP
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)


cliente_socket.connect(("localhost", 8000))

# TODO: Enviar datos al servidor (convertidos a bytes)
# sendall() asegura que todos los datos sean enviados

# TODO: Recibir datos del servidor (hasta 1024 bytes)

# TODO: Decodificar e imprimir los datos recibidos

# TODO: Cerrar la conexión con el servidor

