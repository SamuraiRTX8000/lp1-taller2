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



