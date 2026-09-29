
import socket

ADDRESS = ("localhost", 8000)


def main():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(ADDRESS)
    server.listen()

    print(f"Servidor escuchando en {ADDRESS[0]}:{ADDRESS[1]}")

    try:
        while True:

            client, address = server.accept()

            print(f"Cliente conectado: {address}")

            request = client.recv(4096)

            if request:

                print("\n--- PETICIÓN RECIBIDA ---")
                print(request.decode("utf-8", errors="replace"))
                print("-------------------------")

                response_body = """
Hola desde el servidor HTTP.

La petición llegó correctamente.
"""

                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
                    "\r\n"
                    f"{response_body}"
                )

                client.sendall(
                    response.encode("utf-8")
                )

            client.close()

    except KeyboardInterrupt:

        print("\nServidor cerrado.")

    finally:

        server.close()


if __name__ == "__main__":
    main()

