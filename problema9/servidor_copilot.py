import select
import socket
import threading

HOST = "localhost"
BACKENDS = [
    (HOST, 5001),
    (HOST, 5002),
    (HOST, 5003),
]

actual = 0
lock = threading.Lock()


def health_check(backend):
    """Comprueba si un backend acepta conexiones."""
    try:
        with socket.create_connection(backend, timeout=1):
            return True
    except OSError:
        return False


def elegir_backend():
    """Selecciona un backend disponible con Round Robin."""
    global actual

    with lock:
        for _ in range(len(BACKENDS)):
            backend = BACKENDS[actual]
            actual = (actual + 1) % len(BACKENDS)

            if health_check(backend):
                return backend

    return None


def retransmitir(cliente, backend):
    """Mantiene la conexión abierta y retransmite datos en ambas direcciones."""
    try:
        while True:
            listos, _, _ = select.select([cliente, backend], [], [])

            for origen in listos:
                destino = backend if origen is cliente else cliente
                datos = origen.recv(4096)

                if not datos:
                    return

                destino.sendall(datos)

    except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, OSError):
        pass
    finally:
        for conexion in (cliente, backend):
            try:
                conexion.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                conexion.close()
            except OSError:
                pass


def atender(cliente):
    backend = elegir_backend()

    if backend is None:
        try:
            cliente.sendall(b"No hay servidores disponibles\n")
        except OSError:
            pass
        finally:
            cliente.close()
        return

    try:
        conexion_backend = socket.create_connection(backend, timeout=2)
        conexion_backend.setblocking(True)
    except OSError:
        try:
            cliente.sendall(b"No se pudo conectar con un servidor\n")
        except OSError:
            pass
        finally:
            cliente.close()
        return

    retransmitir(cliente, conexion_backend)


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, 5000))
        servidor.listen()
        print("Servidor principal en puerto 5000")

        while True:
            try:
                cliente, direccion = servidor.accept()
            except OSError as error:
                print(f"Error aceptando conexión: {error}")
                continue

            threading.Thread(
                target=atender,
                args=(cliente,),
                daemon=True,
            ).start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCerrando servidor principal...")