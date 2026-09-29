import socket
import threading
import json
from pathlib import Path

ADDRESS = ("localhost", 8000)
ROOMS_FILE = Path("salas.json")

# Estado compartido del servidor
rooms = {}
users = {}
lock = threading.Lock()

#crea un archivo json q ue me permite guardar las salas creadas y mantenerlas despues de cerrar el sever
# ---------- Persistencia ----------

def save_rooms():
    with ROOMS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            {"rooms": list(rooms.keys())},
            file,
            indent=4,
            ensure_ascii=False
        )

def load_rooms():
    if ROOMS_FILE.exists():
        with ROOMS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        for room in data.get("rooms", []):
            rooms[room] = set()

    if "general" not in rooms:
        rooms["general"] = set()

    save_rooms()

#funcion que permite enviar mensaje a una persona o a sala completa
# ---------- Comunicación ----------
#funciob que permite enviarle un mensaje a alguien especifico
def send_message(conn, message):
    conn.sendall((message + "\n").encode("utf-8"))
#le envia el mensaje a todos

def broadcast(room, message, exclude=None):
    with lock:
        connections = [
            users[name]["conn"]
            for name in rooms.get(room, set())
            if name != exclude and name in users
        ]

    for conn in connections:
        try:
            send_message(conn, message)
        except OSError:
            pass

#definicion de funciones para comandos como crear rooms y entrar a  una room
# ---------- Comandos ----------

def create_room(conn, username, room):
    with lock:
        if room in rooms:
            send_message(conn, "ERROR: la sala ya existe")
            return

        rooms[room] = set()
        save_rooms()

    send_message(conn, f"OK: sala '{room}' creada")
    broadcast(room, f"[Servidor] Se creó la sala {room}")


def join_room(conn, username, room):
    with lock:
        if room not in rooms:
            send_message(conn, "ERROR: la sala no existe")
            return

        old_room = users[username]["room"]

        if old_room == room:
            send_message(conn, "Ya estás en esa sala")
            return

        if old_room is not None:
            rooms[old_room].discard(username)

        rooms[room].add(username)
        users[username]["room"] = room

    if old_room is not None:
        broadcast(old_room, f"[Servidor] {username} salió de la sala")

    send_message(conn, f"OK: entraste a '{room}'")
    broadcast(room, f"[Servidor] {username} entró a la sala")


def leave_room(conn, username):
    with lock:
        room = users[username]["room"]

        if room is None:
            send_message(conn, "ERROR: no estás en ninguna sala")
            return

        rooms[room].discard(username)
        users[username]["room"] = None

    send_message(conn, f"OK: saliste de '{room}'")
    broadcast(room, f"[Servidor] {username} salió de la sala")


def list_rooms(conn):
    with lock:
        names = sorted(rooms.keys())

    send_message(conn, "Salas disponibles:")

    for name in names:
        send_message(conn, f"- {name}")

    send_message(conn, ".")


def list_users(conn, username):
    with lock:
        room = users[username]["room"]

        if room is None:
            send_message(conn, "ERROR: primero entra a una sala")
            return

        members = sorted(rooms[room])

    send_message(conn, f"Usuarios en '{room}':")

    for member in members:
        send_message(conn, f"- {member}")

    send_message(conn, ".")







