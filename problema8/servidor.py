import socket
import threading

tablero = [" "] * 9
clientes = []
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
    for cliente in clientes:
        try:
            cliente.sendall(mensaje.encode())
        except:
            pass


def atender_jugador(cliente, simbolo):
    global turno

    cliente.sendall(f"JUGADOR {simbolo}\n".encode())

    while True:
        try:
            posicion = cliente.recv(1024).decode().strip()

            if not posicion:
                break

            with lock:

                if turno != simbolo:
                    cliente.sendall(b"No es tu turno\n")
                    continue

                if not posicion.isdigit():
                    cliente.sendall(b"Escribe un numero del 1 al 9\n")
                    continue

                posicion = int(posicion) - 1

                if posicion < 0 or posicion > 8:
                    cliente.sendall(b"Posicion invalida\n")
                    continue

                if tablero[posicion] != " ":
                    cliente.sendall(b"Casilla ocupada\n")
                    continue

                tablero[posicion] = simbolo

                if turno == "X":
                    turno = "O"
                else:
                    turno = "X"

                enviar_a_todos(
                    f"\nMovimiento de {simbolo}\n"
                    + mostrar_tablero()
                    + f"Turno de {turno}\n"
                )

        except:
            break


servidor = socket.socket()
servidor.bind(("localhost", 8080))
servidor.listen()

print("Servidor Tic-Tac-Toe iniciado")
print("Esperando jugadores...\n")

while True:

    cliente, direccion = servidor.accept()

    with lock:
        clientes.append(cliente)

        # MATCHMAKING
        if len(jugadores) < 2:

            if len(jugadores) == 0:
                simbolo = "X"
            else:
                simbolo = "O"

            jugadores.append(cliente)

            print(f"Jugador {simbolo} conectado")

            cliente.sendall(
                f"JUGADOR {simbolo}\n{mostrar_tablero()}"
                f"\nTurno de {turno}\n".encode()
            )

            threading.Thread(
                target=atender_jugador,
                args=(cliente, simbolo)
            ).start()

        # ESPECTADOR
        else:

            print("Nuevo espectador conectado")

            cliente.sendall(
                f"ESPECTADOR\n{mostrar_tablero()}"
                f"\nTurno de {turno}\n".encode()
            )

