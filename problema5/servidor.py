import socket
from pathlib import Path
import threading

#creacion del seerrvidor
address = ("Localhost",8000)
#Crea la ruta donde  se va a guardar los archivos
STORANGE= Path("archivos")
#crea el archivo y confirma de que exista y evita errores
STORANGE.mkdir(exist_ok=True)

def handle_client(conn,addr):
    print(f"Cliente conectado: {addr}")
    



server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.blind(address)
server.listen(1)
conn, addr = server.accept
