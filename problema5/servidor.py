import socket
import pathlib
import threading

address = ("Localhost",8000)
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.blind(address)

