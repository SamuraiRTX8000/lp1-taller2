import socket
import threading

SERVIDOR = ("localhost", 5000)


def recibir_mensajes(lector):
    try:
        while True:
            linea = lector.readline()
            if not linea:
                print("\nConexión cerrada por el servidor.")
                return
            print(linea.rstrip())
    except OSError as error:
        print(f"\nError recibiendo mensajes: {error}")


def main():
    try:
        with socket.create_connection(SERVIDOR) as cliente:
            lector = cliente.makefile("r", encoding="utf-8")
            print(lector.readline().rstrip())

            usuario = input("Usuario: ").strip()
            cliente.sendall((usuario + "\n").encode("utf-8"))

            hilo = threading.Thread(
                target=recibir_mensajes,
                args=(lector,),
                daemon=True,
            )
            hilo.start()

            while True:
                comando = input("> ").strip()
                if not comando:
                    continue

                cliente.sendall((comando + "\n").encode("utf-8"))
                if comando.upper() == "QUIT":
                    break

            lector.close()

    except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, OSError) as error:
        print(f"Error de conexión: {error}")


if __name__ == "__main__":
    main()