#!/usr/bin/env python3
"""
Problema 1: Sockets básicos - Servidor
Objetivo: Crear un servidor TCP que acepte una conexión y intercambie mensajes básicos
"""

import socket


direccion_servidor = ("localhost", 8000)



servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)


servidor.bind(direccion_servidor)


# El parámetro define el número máximo de conexiones en cola
servidor.listen(1)
print("Servidor a la espera de conexiones ...")


# accept() bloquea hasta que llega una conexión
# conn: nuevo socket para comunicarse con el cliente
# addr: dirección y puerto del cliente
conn, addr = servidor.accept()

print(f"Conexión realizada por {addr}")

# TODO: Recibir datos del cliente (hasta 1024 bytes)
 
# TODO: Enviar respuesta al cliente (convertida a bytes)
# sendall() asegura que todos los datos sean enviados

# TODO: Cerrar la conexión con el cliente

