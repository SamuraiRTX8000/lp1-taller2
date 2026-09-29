
import socket
import threading


# Dirección y puerto donde estará escuchando nuestro proxy
PROXY_ADDRESS = ("localhost", 8080)

# Cantidad máxima de bytes que recibiremos en cada operación
BUFFER_SIZE = 4096


# ---------- Logging ----------

# Esta función muestra información sobre lo que está haciendo el proxy.
# Nos sirve para monitorear las conexiones y las peticiones.
def log(message):
    print(f"[PROXY] {message}")


# ---------- Reenvío de datos ----------

# Esta función recibe datos de un socket y los envía a otro.
#
# source      -> socket del que recibimos los datos
# destination -> socket al que enviamos los datos
# direction   -> texto que utilizamos para mostrar la dirección
#                de la comunicación en el log
def forward(source, destination, direction):

    try:

        # Mantenemos la comunicación mientras sigan llegando datos
        while True:

            # Recibimos datos del socket de origen
            data = source.recv(BUFFER_SIZE)

            # Si no recibimos datos significa que la conexión terminó
            if not data:
                break

            # Enviamos los mismos datos al otro socket
            destination.sendall(data)

            # Mostramos en el log cuántos bytes fueron enviados
            log(f"{direction}: {len(data)} bytes")

    except (ConnectionError, OSError):

        # Si alguno de los sockets se desconecta,
        # simplemente terminamos el reenvío.
        pass

    finally:

        # Indicamos que ya no enviaremos más datos
        # por esta dirección del socket.
        try:
            destination.shutdown(socket.SHUT_WR)
        except OSError:
            pass


# ---------- HTTPS ----------

# El método CONNECT es utilizado por los clientes
# para establecer un túnel HTTPS a través del proxy.
#
# Ejemplo:
#
# CONNECT google.com:443 HTTP/1.1
#
def handle_connect(client, target):

    try:

        # Separamos el destino en:
        #
        # host = google.com
        # port = 443
        #
        host, port = target.split(":", 1)

        # El puerto viene como texto, por eso lo convertimos
        # a un número entero.
        port = int(port)

        log(f"HTTPS CONNECT -> {host}:{port}")

        # El proxy crea una conexión con el servidor destino.
        server = socket.create_connection((host, port))

        # Le informamos al cliente que el túnel fue creado
        # correctamente.
        client.sendall(
            b"HTTP/1.1 200 Connection Established\r\n"
            b"\r\n"
        )

        # Creamos un hilo para enviar información:
        #
        # CLIENTE -> SERVIDOR
        #
        client_to_server = threading.Thread(
            target=forward,
            args=(
                client,
                server,
                "CLIENTE -> SERVIDOR"
            ),
            daemon=True
        )

        # Creamos otro hilo para la dirección contraria:
        #
        # SERVIDOR -> CLIENTE
        #
        server_to_client = threading.Thread(
            target=forward,
            args=(
                server,
                client,
                "SERVIDOR -> CLIENTE"
            ),
            daemon=True
        )

        # Iniciamos ambos hilos
        client_to_server.start()
        server_to_client.start()

        # Esperamos a que termine la comunicación
        client_to_server.join()
        server_to_client.join()

    except (ConnectionError, OSError, ValueError) as error:

        log(f"Error CONNECT: {error}")

        # Si no podemos conectarnos al servidor,
        # enviamos un error HTTP al cliente.
        try:

            client.sendall(
                b"HTTP/1.1 502 Bad Gateway\r\n"
                b"Content-Length: 0\r\n"
                b"\r\n"
            )

        except OSError:
            pass

    finally:

        # Cerramos el socket del servidor si fue creado.
        try:
            server.close()
        except UnboundLocalError:
            pass


# ---------- HTTP ----------

# Esta función procesa las peticiones HTTP normales,
# como GET, POST, etc.
def handle_http(client, request):

    try:

        # Obtenemos la primera línea de la petición.
        #
        # Ejemplo:
        #
        # GET http://localhost:8000/hola HTTP/1.1
        #
        first_line = request.split(
            b"\r\n",
            1
        )[0].decode(
            "utf-8",
            errors="replace"
        )

        # Separamos:
        #
        # GET
        # http://localhost:8000/hola
        # HTTP/1.1
        #
        parts = first_line.split()

        # Comprobamos que tenga las partes necesarias
        if len(parts) < 3:
            return

        method = parts[0]
        url = parts[1]
        version = parts[2]

        # Mostramos la petición en el log
        log(f"HTTP {method} -> {url}")

        # Eliminamos "http://" de la URL.
        if url.startswith("http://"):
            url_without_protocol = url[7:]
        else:
            url_without_protocol = url

        # Separamos el host de la ruta.
        #
        # ejemplo:
        #
        # localhost:8000/hola
        #
        # host_port = localhost:8000
        # path      = /hola
        #
        if "/" in url_without_protocol:

            host_port, path = url_without_protocol.split(
                "/",
                1
            )

            path = "/" + path

        else:

            host_port = url_without_protocol
            path = "/"

        # Comprobamos si el host especifica un puerto.
        #
        # localhost:8000
        #
        # En ese caso:
        #
        # host = localhost
        # port = 8000
        #
        if ":" in host_port:

            host, port_text = host_port.rsplit(
                ":",
                1
            )

            port = int(port_text)

        else:

            # Si no especifica puerto,
            # utilizamos el puerto HTTP estándar.
            host = host_port
            port = 80

        # Nos conectamos al servidor destino
        server = socket.create_connection(
            (host, port)
        )

        # Buscamos dónde terminan los headers HTTP.
        #
        # HTTP separa los headers del cuerpo mediante:
        #
        # \r\n\r\n
        #
        header_end = request.find(
            b"\r\n\r\n"
        )

        if header_end == -1:

            # No encontramos separación de headers
            headers = request
            body = b""

        else:

            # Separamos headers y cuerpo
            headers = request[:header_end]

            body = request[
                header_end + 4:
            ]

        # Separamos todos los headers individuales.
        header_lines = headers.split(
            b"\r\n"
        )

        # Creamos los nuevos headers.
        new_headers = [

            # Cambiamos la primera línea.
            #
            # Antes:
            # GET http://localhost:8000/hola HTTP/1.1
            #
            # Después:
            # GET /hola HTTP/1.1
            #
            f"{method} {path} {version}".encode(
                "utf-8"
            )
        ]

        # Copiamos los headers originales
        for header in header_lines[1:]:

            if header:
                new_headers.append(header)

        # Agregamos un header propio del proxy.
        #
        # Esto demuestra que el proxy puede modificar
        # la petición antes de enviarla.
        new_headers.append(
            b"X-Proxy: Python-Proxy"
        )

        # Reconstruimos la petición completa.
        new_request = b"\r\n".join(
            new_headers
        )

        new_request += b"\r\n\r\n"

        new_request += body

        # Enviamos la petición modificada
        # al servidor destino.
        server.sendall(new_request)

        # Ahora esperamos la respuesta del servidor.
        while True:

            data = server.recv(
                BUFFER_SIZE
            )

            # Si no hay más datos,
            # el servidor terminó la respuesta.
            if not data:
                break

            # Enviamos la respuesta al cliente.
            client.sendall(data)

            # Registramos cuántos bytes recibimos.
            log(
                f"SERVIDOR -> CLIENTE: "
                f"{len(data)} bytes"
            )

        # Cerramos la conexión con el servidor
        server.close()

    except (ConnectionError, OSError, ValueError) as error:

        log(f"Error HTTP: {error}")

        # En caso de error enviamos una respuesta
        # HTTP 502 Bad Gateway.
        try:

            client.sendall(
                b"HTTP/1.1 502 Bad Gateway\r\n"
                b"Content-Length: 0\r\n"
                b"\r\n"
            )

        except OSError:
            pass


# ---------- Cliente conectado ----------

# Esta función controla cada cliente que se conecta
# al proxy.
def handle_client(client, address):

    log(f"Cliente conectado: {address}")

    try:

        # Recibimos la primera petición del cliente.
        request = client.recv(
            BUFFER_SIZE
        )

        # Si no recibimos nada,
        # terminamos la conexión.
        if not request:
            return

        # Obtenemos la primera línea.
        first_line = request.split(
            b"\r\n",
            1
        )[0].decode(
            "utf-8",
            errors="replace"
        )

        # Separamos la línea en partes.
        parts = first_line.split()

        if not parts:
            return

        # Obtenemos el método HTTP.
        method = parts[0].upper()

        # Si el método es CONNECT,
        # significa que se está solicitando
        # un túnel HTTPS.
        if method == "CONNECT":

            if len(parts) < 2:
                return

            target = parts[1]

            handle_connect(
                client,
                target
            )

        # Si no es CONNECT,
        # tratamos la petición como HTTP normal.
        else:

            handle_http(
                client,
                request
            )

    except (
        ConnectionError,
        OSError,
        UnicodeDecodeError
    ) as error:

        log(
            f"Error con cliente "
            f"{address}: {error}"
        )

    finally:

        # Cerramos la conexión con el cliente.
        client.close()

        log(
            f"Cliente desconectado: "
            f"{address}"
        )


# ---------- Servidor del Proxy ----------

def main():

    # Creamos el socket TCP del proxy.
    proxy = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    # Permite reutilizar el puerto inmediatamente
    # después de cerrar el servidor.
    proxy.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    # Asociamos el socket a localhost:8080.
    proxy.bind(
        PROXY_ADDRESS
    )

    # Ponemos el socket en modo escucha.
    proxy.listen()

    log(
        f"Proxy escuchando en "
        f"{PROXY_ADDRESS[0]}:"
        f"{PROXY_ADDRESS[1]}"
    )

    try:

        # Esperamos clientes continuamente.
        while True:

            # Aceptamos una nueva conexión.
            client, address = proxy.accept()

            # Creamos un hilo para atender
            # independientemente a ese cliente.
            thread = threading.Thread(
                target=handle_client,
                args=(client, address),
                daemon=True
            )

            # Iniciamos el hilo.
            thread.start()

    except KeyboardInterrupt:

        # Ctrl+C permite detener el proxy.
        log("Cerrando proxy...")

    finally:

        # Cerramos el socket principal.
        proxy.close()


# ---------- Inicio ----------

if __name__ == "__main__":
    main()

