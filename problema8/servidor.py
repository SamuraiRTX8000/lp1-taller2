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

# --------------------------------------------------
# ENVÍO DE MENSAJES
# --------------------------------------------------

def send_message(conn, message):
    """
    Envía un mensaje al cliente.
    """
    try:
        conn.sendall((message + "\n").encode("utf-8"))
    except (ConnectionError, OSError):
        pass


def broadcast(message):
    """
    Envía un mensaje a todos los jugadores
    y espectadores.
    """

    with lock:

        connections = []

        # Agregamos jugadores
        for conn, address in players.values():
            connections.append(conn)

        # Agregamos espectadores
        connections.extend(spectators)

    # Enviamos fuera del lock
    # para no bloquear el estado del juego.
    for conn in connections:
        send_message(conn, message)

# --------------------------------------------------
# TABLERO
# --------------------------------------------------

def board_to_string():
    """
    Convierte el tablero en texto.
    """

    return (
        f"\n"
        f" {board[0]} | {board[1]} | {board[2]}\n"
        f"---+---+---\n"
        f" {board[3]} | {board[4]} | {board[5]}\n"
        f"---+---+---\n"
        f" {board[6]} | {board[7]} | {board[8]}\n"
    )

# --------------------------------------------------
# VALIDACIÓN DEL GANADOR
# --------------------------------------------------

def check_winner():

    combinations = [

        # Filas
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),

        # Columnas
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),

        # Diagonales
        (0, 4, 8),
        (2, 4, 6)
    ]

    for a, b, c in combinations:

        if (
            board[a] != " "
            and board[a] == board[b]
            and board[b] == board[c]
        ):
            return board[a]

    # Si no quedan casillas libres,
    # es empate.
    if " " not in board:
        return "DRAW"

    return None


