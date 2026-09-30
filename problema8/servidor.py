import socket
import threading

tablero = [" "] * 9
jugadores = []
turno = "X"
lock = threading.Lock()


def mostrar_tablero():
    return f"""
{tablero[0]} | {tablero[1]} | {tablero[2]}
---------
{tablero[3]} | {tablero[4]} | {tablero[5]}
---------
{tablero[6]} | {tablero[7]} | {tablero[8]}
"""


def enviar_a_todos(mensaje):
    for jugador in jugadores:
        jugador.sendall(mensaje.encode())


def atender(cliente, simbolo):
    global turno

    cliente.sendall(f"Eres jugador {simbolo}\n".encode())

    while True:
        posicion = cliente.recv(1024).decode().strip()

        with lock:
            # Validar turno
            if turno != simbolo:
                cliente.sendall(b"No es tu turno\n")
                continue

            # Validar movimiento
            if not posicion.isdigit():
                cliente.sendall(b"Escribe un numero del 1 al 9\n")
                continue

            posicion = int(posicion) - 1

            if posicion < 0 or posicion > 8 or tablero[posicion] != " ":
                cliente.sendall(b"Movimiento invalido\n")
                continue

            # Realizar movimiento
            tablero[posicion] = simbolo
            turno = "O" if turno == "X" else "X"

            enviar_a_todos(mostrar_tablero())


servidor = socket.socket()
servidor.bind(("localhost", 8080))
servidor.listen()

print("Servidor Tic-Tac-Toe iniciado en puerto 8080")

while True:
    cliente, direccion = servidor.accept()

    with lock:
        jugadores.append(cliente)

        if len(jugadores) <= 2:
            simbolo = "X" if len(jugadores) == 1 else "O"
            threading.Thread(
                target=atender,
                args=(cliente, simbolo)
            ).start()

            print(f"Jugador {simbolo} conectado")

        else:
            cliente.sendall(b"Eres espectador\n")
            cliente.sendall(mostrar_tablero().encode())
            print("Espectador conectado")



