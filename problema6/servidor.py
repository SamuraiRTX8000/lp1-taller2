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


# ---------- Persistencia ----------

def save_rooms():
    with ROOMS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            {"rooms": list(rooms.keys())},
            file,
            indent=4,
            ensure_ascii=False
        )

