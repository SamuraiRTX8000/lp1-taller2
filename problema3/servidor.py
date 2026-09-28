#!/usr/bin/env python3
"""
Problema 3: Chat simple con múltiples clientes - Servidor
Objetivo: Crear un servidor de chat que maneje múltiples clientes simultáneamente usando threads
"""

import socket
import threading


address = ("Localhost", 8000)


# Lista para mantener todos los sockets de clientes conectados
clients = []

def handle_client(client_socket, client_name):
    """
    Maneja la comunicación con un cliente específico en un hilo separado.
    
    Args:
        client_socket: Socket del cliente
        client_name: Nombre del cliente
    """
    while True:
        try:
            
            data = client_socket.recv(1024)

            
            # Si no se reciben datos, el cliente se desconectó
            if not data:
                break
                
            # Formatear el mensaje con el nombre del cliente
            message = f"{client_name}: {data.decode()}"
            
            # Imprimir el mensaje en el servidor
            print(message)
            
            
            broadcast(message,client_socket)


            
        except ConnectionResetError:
            # Manejar desconexión inesperada del cliente
            clients.remove(client_socket)
            client_socket.close()
            break

def broadcast(message, sender_socket):
    """
    Envía un mensaje a todos los clientes conectados excepto al remitente.
    
    Args:
        message: Mensaje a enviar (string)
        sender_socket: Socket del cliente que envió el mensaje original
    """
    #"este for recorre cada cliente y le va mandando los mensajes de otros"
    for client in clients:
        if client != sender_socket:
            
            client.sendall(message.encode())



# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


servidor.bind(address)


# El parámetro define el número máximo de conexiones en cola
servidor.listen(5)

print("Servidor a la espera de conexiones ...")

# Bucle principal para aceptar conexiones entrantes

while True:
    
    client,addr = servidor.accept()
    # client: nuevo socket para comunicarse con el cliente
    # addr: dirección y puerto del cliente
    
    print(f"Conexión realizada por {addr}")
    
    
    client_name = client.recv(1024).decode()
    
    
    clients.append(client)
    
    # Enviar mensaje de confirmación de conexión al cliente
    client.send("ya estás conectado!".encode())
    
    # Notificar a todos los clientes que un nuevo usuario se unió al chat
    broadcast(f"{client_name} se ha unido al Chat.", client)
    
    
    # target: función que se ejecutará en el hilo
    # args: argumentos que se pasarán a la función
    

    client_handler = threading.Thread(target=handle_client, args=(client,client_name))
    client_handler.start()

