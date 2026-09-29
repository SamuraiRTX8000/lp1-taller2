
import socket

PROXY_ADDRESS = ("localhost", 8080)


def main():

    client = socket.create_connection(PROXY_ADDRESS)

    request = (
        "GET http://localhost:8000/hola HTTP/1.1\r\n"
        "Host: localhost:8000\r\n"
        "User-Agent: Cliente-Python\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    print("Enviando petición al proxy...\n")

    client.sendall(
        request.encode("utf-8")
    )

    response = b""

    while True:

        data = client.recv(4096)

        if not data:
            break

        response += data

    print("Respuesta recibida:")
    print("-------------------")
    print(response.decode("utf-8", errors="replace"))

    client.close()


if __name__ == "__main__":
    main()

