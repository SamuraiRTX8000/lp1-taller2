import socket
from pathlib import Path
import threading

#creacion del seerrvidor
address = ("Localhost",8000)

BUFFER_SIZE = 4096
#Crea la ruta donde  se va a guardar los archivos
STORAGE= Path("archivos")
#crea el archivo y confirma de que exista y evita errores
STORAGE.mkdir(exist_ok=True)
#----------Reforma para recibir mensajes--------


def read_line(conn):
    """Lee una línea de texto terminada en \\n."""
    #aqui se reconstruye el mensaje
    data = bytearray()

    while True:
        byte = conn.recv(1)

        if not byte:
            raise ConnectionError("Conexión cerrada")

        if byte == b"\n":
            #se pasa a string
            return data.decode("utf-8")

        data.extend(byte)

def safe_path(filename):
    #evita nombres problematicos como . y .. por el sistema operativo
    #nombres vacios
    """Evita nombres que intenten salir de STORAGE."""
    if not filename or filename in (".", ".."):
        raise ValueError("Nombre de archivo no válido")
# EVITAMOS QUE EL CLIENTE MANDE RUTAS SOLO PERMITE  NOMBRES
    if Path(filename).name != filename:
        raise ValueError("Ruta no permitida")
#crea la ruta y la vuelve canonica
    path = (STORAGE / filename).resolve()

    if path.parent != STORAGE.resolve():
        raise ValueError("Ruta no permitida")

    return path

#-----reconstruccion--------------------
def handle_client(conn,addr):
    print(f"Cliente conectado: {addr}")
    try:
#con conn.makefile("r", encoding="UTF-8") permite ponerle una interfaz a los datos del socket
#algo parecido a crear un archivo desechable que esta ligado al socket directamente
#"r" formato para la lectura 
#y el encoding="UTF-8") permite de pasar de bytes a string
        reader = conn.makefile("r", encoding="UTF-8")
        #readLine permite leer el contenido de reader hasta un salto de linea
        #strip borrra el vacio del princio y final
        command = reader.readline().strip()
#si el comando recibido es list se crea una lista 
        if command == "LIST":
            files = [
                #indica que queremos guardar
                path.name
                #itera los archivos en storage
                for path in STORAGE.iterdir()
                #solo lo incluye si es un archivo
                if path.is_file()
            ]
            conn.sendall(b"OK\n")
            #envia la lista
            for filename in files:
                conn.sendall(f"{filename}\n".encode("utf-8"))

            #le dice alsercer que ya termino el comando
            conn.sendall(b".\n")
# comandos desconocidos e informa que no existen
        else:
            conn.sendall(b"ERROR: comando desconocido\n")
#reconoce un error y lo captura y reporta
    except (ConnectionError, OSError) as error:
        print(f"Error con {addr}: {error}")

    finally:
        conn.close()
        print(f"Cliente desconectado: {addr}")

        







server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#permite reutilizar la conexion rapidamente si se llega a cerrar
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(address)
server.listen(5)
print(f"Servidor escuchando en {address[0]}:{address[1]}")

try:
    while True:
        #acepta clientes
        conn, addr = server.accept()
#crea los hilos
        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        )
        thread.start()

except KeyboardInterrupt:
    print("\nCerrando servidor...")

finally:
    server.close()
