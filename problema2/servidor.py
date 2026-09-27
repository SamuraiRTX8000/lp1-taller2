#!/usr/bin/env python3
"""
Problema 2: Comunicación bidireccional - Servidor
Objetivo: Crear un servidor TCP que devuelva exactamente lo que recibe del cliente
"""

import socket


direccion = ("Localhost", 8000)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)

server_socket.bind(direccion)


# El parámetro define el número máximo de conexiones en cola
server_socket.listen(1)

# Bucle infinito para manejar múltiples conexiones (una a la vez)
while True:

    print("Servidor a la espera de conexiones ...")
    
    # TODO: Aceptar una conexión entrante
    # accept() bloquea hasta que llega una conexión
    # conn: nuevo socket para comunicarse con el cliente
    # addr: dirección y puerto del cliente
    
    print(f"Conexión realizada por {addr}")

    # TODO: Recibir datos del cliente (hasta 1024 bytes)
    
    # Si no se reciben datos, salir del bucle
    if not data:
        break

    # Mostrar los datos recibidos (en formato bytes)
    print("Datos recibidos:", data)
    
    # TODO: Enviar los mismos datos de vuelta al cliente (echo)
    
    # TODO: Cerrar la conexión con el cliente actual

