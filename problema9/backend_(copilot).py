import json
import socket
import sys
import threading

HOST = "localhost"
PEER_PORT_OFFSET = 10000
BACKEND_PORTS = (5001, 5002, 5003)

usuarios = {}
usuarios_remotos = {}
lock = threading.Lock()


def enviar(conn, mensaje, send_lock=None):
    """Envía una línea al cliente."""
    datos = (mensaje + "\n").encode("utf-8")
    if send_lock is None:
        conn.sendall(datos)
    else:
        with send_lock:
            conn.sendall(datos)


def propagar(evento):
    """Envía un evento a los demás backends."""
    datos = (json.dumps(evento, ensure_ascii=False) + "\n").encode("utf-8")

    for puerto in BACKEND_PORTS:
        if puerto == PUERTO:
            continue

        try:
            with socket.create_connection(
                (HOST, puerto + PEER_PORT_OFFSET),
                timeout=0.5,
            ) as peer:
                peer.sendall(datos)
        except OSError:
            # Un backend puede estar apagado; los demás siguen funcionando.
            continue


def difundir(sala, mensaje, excluir=None):
    """Difunde un mensaje a los clientes locales de una sala."""
    with lock:
        destinatarios = [
            (nombre, datos["conn"], datos["send_lock"])
            for nombre, datos in usuarios.items()
            if datos["sala"] == sala and nombre != excluir
        ]

    desconectados = []
    for nombre, conn, send_lock in destinatarios:
        try:
            enviar(conn, mensaje, send_lock)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, OSError):
            desconectados.append((nombre, conn))

    for nombre, conn in desconectados:
        eliminar_usuario(nombre, conn)


def procesar_evento_remoto(evento):
    """Actualiza presencia remota y difunde localmente, sin reenviar el evento."""
    tipo = evento.get("tipo")
    usuario = evento.get("usuario")
    sala = evento.get("sala")

    if not usuario:
        return

    if tipo == "join":
        with lock:
            usuarios_remotos[usuario] = sala
        difundir(sala, f"[Servidor] {usuario} entró a la sala")

    elif tipo == "leave":
        with lock:
            usuarios_remotos.pop(usuario, None)
        if sala:
            difundir(sala, f"[Servidor] {usuario} salió de la sala")

    elif tipo == "mensaje":
        difundir(sala, f"[{sala}] {usuario}: {evento.get('contenido', '')}")


def atender_peer(conn):
    """Recibe un único evento de otro backend."""
    try:
        with conn:
            archivo = conn.makefile("r", encoding="utf-8")
            linea = archivo.readline()
            archivo.close()

            if linea:
                evento = json.loads(linea)
                procesar_evento_remoto(evento)
    except (ConnectionResetError, ConnectionAbortedError, OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"Error recibiendo evento de backend: {error}")


def servidor_peers():
    """Escucha eventos internos en el puerto asociado a este backend."""
    puerto = PUERTO + PEER_PORT_OFFSET

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, puerto))
        servidor.listen()
        print(f"Sincronización interna en puerto {puerto}")

        while True:
            try:
                conn, _ = servidor.accept()
            except OSError as error:
                print(f"Error aceptando evento interno: {error}")
                continue

            threading.Thread(
                target=atender_peer,
                args=(conn,),
                daemon=True,
            ).start()


def eliminar_usuario(nombre, conn):
    """Retira y cierra un cliente; no hace nada si ya fue eliminado."""
    with lock:
        datos = usuarios.get(nombre)
        if datos is None or datos["conn"] is not conn:
            return

        usuarios.pop(nombre)
        sala = datos["sala"]

    try:
        conn.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        conn.close()
    except OSError:
        pass

    if sala:
        difundir(sala, f"[Servidor] {nombre} se desconectó")
        propagar({"tipo": "leave", "usuario": nombre, "sala": sala})


def listar_usuarios(conn, nombre):
    with lock:
        sala = usuarios[nombre]["sala"]
        locales = {
            usuario
            for usuario, datos in usuarios.items()
            if datos["sala"] == sala
        }
        remotos = {
            usuario
            for usuario, sala_remota in usuarios_remotos.items()
            if sala_remota == sala
        }

    enviar(conn, f"Usuarios en '{sala}':")
    for usuario in sorted(locales | remotos):
        enviar(conn, f"- {usuario}")
    enviar(conn, ".")


def manejar_comando(conn, nombre, linea):
    partes = linea.strip().split(maxsplit=1)
    if not partes:
        return False

    comando = partes[0].upper()
    argumento = partes[1].strip() if len(partes) == 2 else ""

    if comando == "HELP":
        enviar(conn, "Comandos: MSG mensaje, USERS, LEAVE, JOIN general, QUIT")
    elif comando == "USERS":
        listar_usuarios(conn, nombre)
    elif comando == "MSG":
        if not argumento:
            enviar(conn, "Uso: MSG mensaje")
            return False

        with lock:
            sala = usuarios[nombre]["sala"]

        evento = {
            "tipo": "mensaje",
            "usuario": nombre,
            "sala": sala,
            "contenido": argumento,
        }
        difundir(sala, f"[{sala}] {nombre}: {argumento}")
        propagar(evento)
    elif comando == "LEAVE":
        with lock:
            sala = usuarios[nombre]["sala"]
            usuarios[nombre]["sala"] = None

        if sala:
            difundir(sala, f"[Servidor] {nombre} salió de la sala")
            propagar({"tipo": "leave", "usuario": nombre, "sala": sala})
        else:
            enviar(conn, "No estás en una sala")
    elif comando == "JOIN":
        sala = argumento or "general"
        with lock:
            anterior = usuarios[nombre]["sala"]
            usuarios[nombre]["sala"] = sala

        if anterior:
            difundir(anterior, f"[Servidor] {nombre} salió de la sala")
            propagar({"tipo": "leave", "usuario": nombre, "sala": anterior})

        enviar(conn, f"OK: entraste a '{sala}'")
        difundir(sala, f"[Servidor] {nombre} entró a la sala")
        propagar({"tipo": "join", "usuario": nombre, "sala": sala})
    elif comando == "QUIT":
        enviar(conn, "Adios")
        return True
    else:
        enviar(conn, "Comando desconocido. Escribe HELP")

    return False


def manejar_cliente(conn, direccion):
    nombre = None
    send_lock = threading.Lock()

    try:
        enviar(conn, "Escribe tu nombre de usuario:")
        archivo = conn.makefile("r", encoding="utf-8")
        nombre = archivo.readline().strip()

        if not nombre or " " in nombre:
            enviar(conn, "ERROR: nombre no válido")
            return

        with lock:
            if nombre in usuarios or nombre in usuarios_remotos:
                enviar(conn, "ERROR: nombre ya conectado")
                return

            usuarios[nombre] = {
                "conn": conn,
                "sala": "general",
                "send_lock": send_lock,
            }

        enviar(conn, f"Bienvenido, {nombre}")
        enviar(conn, "Escribe HELP para ver los comandos")
        difundir("general", f"[Servidor] {nombre} entró a la sala")
        propagar({"tipo": "join", "usuario": nombre, "sala": "general"})

        while True:
            linea = archivo.readline()
            if not linea:
                break
            if manejar_comando(conn, nombre, linea):
                break

        archivo.close()

    except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, socket.timeout, OSError, UnicodeDecodeError) as error:
        print(f"Conexión con {nombre or direccion} cerrada: {error}")
    finally:
        if nombre:
            eliminar_usuario(nombre, conn)
        else:
            try:
                conn.close()
            except OSError:
                pass


def main():
    global PUERTO

    if len(sys.argv) != 2:
        print("Uso: python backend.py PUERTO")
        raise SystemExit(1)

    try:
        PUERTO = int(sys.argv[1])
    except ValueError:
        print("El puerto debe ser un número.")
        raise SystemExit(1)

    if PUERTO not in BACKEND_PORTS:
        print(f"Puertos configurados: {', '.join(map(str, BACKEND_PORTS))}")
        raise SystemExit(1)

    threading.Thread(target=servidor_peers, daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PUERTO))
        servidor.listen()
        print(f"Backend de chat funcionando en {HOST}:{PUERTO}")

        while True:
            try:
                cliente, direccion = servidor.accept()
            except OSError as error:
                print(f"Error aceptando cliente: {error}")
                continue

            threading.Thread(
                target=manejar_cliente,
                args=(cliente, direccion),
                daemon=True,
            ).start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCerrando backend...")