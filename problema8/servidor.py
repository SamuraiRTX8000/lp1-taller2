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
#
 #REINICIAR PARTIDA
# --------------------------------------------------

def reset_game():

    global board
    global current_turn
    global game_started

    with lock:

        board = [" "] * 9
        current_turn = "X"
        game_started = False

# --------------------------------------------------
# MOVIMIENTO
# --------------------------------------------------

def make_move(symbol, position):

    global current_turn
    global game_started

    with lock:

        # ¿La partida comenzó?
        if not game_started:
            return False, "La partida todavía no ha comenzado."

        # ¿Es el turno correcto?
        if symbol != current_turn:
            return False, "No es tu turno."

        # ¿La posición es válida?
        if position < 0 or position > 8:
            return False, "La posición debe estar entre 0 y 8."

        # ¿La casilla está ocupada?
        if board[position] != " ":
            return False, "Esa casilla ya está ocupada."

        # Realizamos el movimiento
        board[position] = symbol

        # Comprobamos ganador
        result = check_winner()

        if result:

            game_started = False

            if result == "DRAW":
                return True, "DRAW"

            return True, result

        # Cambiamos el turno
        if current_turn == "X":
            current_turn = "O"
        else:
            current_turn = "X"

        return True, "CONTINUE"


# --------------------------------------------------
# INICIAR PARTIDA
# --------------------------------------------------

def start_game():

    global game_started
    global current_turn

    with lock:

        if len(players) == 2:

            board[:] = [" "] * 9

            current_turn = "X"

            game_started = True

            return True

    return False
# --------------------------------------------------
# MANEJO DE JUGADORES
# --------------------------------------------------

def handle_player(conn, address, symbol):

    global players

    send_message(
        conn,
        f"Has sido asignado como jugador {symbol}."
    )

    send_message(
        conn,
        "Las posiciones del tablero son:"
    )

    send_message(
        conn,
        "0 1 2 / 3 4 5 / 6 7 8"
    )

    while True:

        try:

            data = conn.recv(1024)

            if not data:
                break

            command = data.decode(
                "utf-8",
                errors="replace"
            ).strip()

            # -----------------------------
            # MOVIMIENTO
            # -----------------------------

            if command.startswith("MOVE"):

                parts = command.split()

                if len(parts) != 2:

                    send_message(
                        conn,
                        "Uso: MOVE <posición>"
                    )

                    continue

                try:

                    position = int(parts[1])

                except ValueError:

                    send_message(
                        conn,
                        "La posición debe ser un número."
                    )

                    continue

                valid, result = make_move(
                    symbol,
                    position
                )

                if not valid:

                    send_message(
                        conn,
                        f"ERROR: {result}"
                    )

                    continue

                # Informamos a todos
                broadcast(
                    f"MOVE {symbol} {position}"
                )

                broadcast(
                    board_to_string()
                )

                # -----------------------------
                # FIN DE PARTIDA
                # -----------------------------

                if result == "DRAW":

                    broadcast(
                        "RESULTADO: EMPATE"
                    )

                elif result in ("X", "O"):

                    broadcast(
                        f"RESULTADO: GANA {result}"
                    )

                else:

                    # Informamos el siguiente turno
                    with lock:
                        turn = current_turn

                    broadcast(
                        f"TURNO: {turn}"
                    )

            # -----------------------------
            # TABLERO
            # -----------------------------

            elif command == "BOARD":

                send_message(
                    conn,
                    board_to_string()
                )

            # -----------------------------
            # SALIR
            # -----------------------------

            elif command == "QUIT":

                break

            else:

                send_message(
                    conn,
                    "Comando desconocido."
                )

        except (
            ConnectionError,
            OSError
        ):
            break
 # --------------------------------------------------
    # JUGADOR DESCONECTADO
    # --------------------------------------------------

    with lock:

        if symbol in players:

            del players[symbol]

        game_started = False

    broadcast(
        f"El jugador {symbol} se ha desconectado."
    )

    conn.close()

    print(
        f"Jugador {symbol} desconectado: {address}"
    )




