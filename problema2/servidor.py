#!/usr/bin/env python3
"""
Problema 2: Comunicación bidireccional - Servidor
Objetivo: Crear un servidor TCP que devuelva exactamente lo que recibe del cliente
"""

import socket


direccion = ("Localhost", 8000)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)

server.bind(direccion)


# El parámetro define el número máximo de conexiones en cola
server.listen(3)

# Bucle infinito para manejar múltiples conexiones (una a la vez)
while True:

    print("Servidor a la espera de conexiones ...")
    
    
    # accept() bloquea hasta que llega una conexión
    # conn: nuevo socket para comunicarse con el cliente
    # addr: dirección y puerto del cliente
    conn, addr = server.accept()
    
    print(f"Conexión realizada por {addr}")


    data = conn.recv(1024)
    
    # Si no se reciben datos, salir del bucle
    if not data:
        break

    # Mostrar los datos recibidos (en formato bytes)
    #no se codifica por que el mensaje ya esta codificado en bytes
    print("Datos recibidos:", data)
    
    
    conn.sendall(data)
    
    
    conn.close()

