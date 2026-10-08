import socket
import threading
import sys

Host = 'localhost'
#dice que lo que le pase por la terminal lo convierta a entero(lo que va  a ser el server)
PUERTO = int(sys.argv[1])
datos={}

