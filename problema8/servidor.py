import socket
import threading


HOST = "localhost"
PORT = 8000

# --------------------------------------------------
# ESTADO COMPARTIDO DEL JUEGO
# --------------------------------------------------

# Tablero:
#
# [0] [1] [2]
# [3] [4] [5]
# [6] [7] [8]
#
# Una casilla vacía contiene " ".
#hace 9 cajones
board = [" "] * 9

# Jugadores:
#
# "X" -> (socket, dirección)
# "O" -> (socket, dirección)

players = {}

# Lista de espectadores
spectators = []

# Turno actual
current_turn = "X"

# Indica si hay una partida en curso
game_started = False

# Lock para proteger el estado compartido
lock = threading.Lock()
