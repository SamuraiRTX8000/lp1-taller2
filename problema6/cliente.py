
import socket
import threading

ADDRESS = ("localhost", 8000)


# ---------- Recibir mensajes ----------

def receive_messages(reader):
    """
    Recibe mensajes del servidor continuamente.
    Se ejecuta en un hilo separado para no bloquear
    la entrada de comandos del usuario.
    """
    try:
        while True:
            message = reader.readline()

            if not message:
                print("\nConexión cerrada por el servidor.")
                break

            print(message.rstrip())

    except OSError:
        pass


# ---------- Cliente principal ----------

def main():

    try:
        # Crea la conexión con el servidor
        with socket.create_connection(ADDRESS) as client:

            # Creamos un lector para recibir mensajes
            reader = client.makefile(
                "r",
                encoding="utf-8"
            )

            # El servidor pide el nombre de usuario
            print(reader.readline().rstrip())

            # El usuario escribe su nombre
            username = input("Usuario: ").strip()

            # Enviamos el nombre al servidor
            client.sendall(
                (username + "\n").encode("utf-8")
            )

            # Creamos un hilo encargado de recibir mensajes
            receiver = threading.Thread(
                target=receive_messages,
                args=(reader,),
                daemon=True
            )

            receiver.start()

            # Bucle principal para escribir comandos
            while True:

                command = input("> ").strip()

                # Ignorar entradas vacías
                if not command:
                    continue

                # Enviar comando al servidor
                client.sendall(
                    (command + "\n").encode("utf-8")
                )

                # Si el usuario quiere salir
                if command.upper() == "QUIT":
                    break

            reader.close()

    except (ConnectionError, OSError) as error:
        print("Error de conexión:", error)


# ---------- Inicio del programa ----------

if __name__ == "__main__":
    main()

