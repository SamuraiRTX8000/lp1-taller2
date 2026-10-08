import socket
import threading

HOST = "localhost"

backends = [
    ("localhost", 5001),
    ("localhost", 5002),
    ("localhost", 5003)
]

actual = 0


def health_check(backend):
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect(backend)
        s.close()
        return True
    except:
        return False


def elegir_backend():
    global actual

    for _ in range(len(backends)):
        backend = backends[actual]

        actual = (actual + 1) % len(backends)

        if health_check(backend):
            return backend

    return None


def atender(cliente):
    backend = elegir_backend()

    if backend is None:
        cliente.send(b"No hay servidores disponibles")
        cliente.close()
        return

    servidor_backend = socket.socket()
    servidor_backend.connect(backend)

    datos = cliente.recv(1024)

    servidor_backend.send(datos)

    respuesta = servidor_backend.recv(1024)

    cliente.send(respuesta)

    servidor_backend.close()
    cliente.close()

servidor = socket.socket()
servidor.bind((HOST, 5000))
servidor.listen()

print("Servidor principal en puerto 5000")

while True:
    cliente, direccion = servidor.accept()

    hilo = threading.Thread(
        target=atender,
        args=(cliente,)
    )

    hilo.start()