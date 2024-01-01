import socket
import threading
import time
from threading import Thread
import pyrebase
players_online = {}
DISCONNECT_MESSAGE = "leave"

def connect_to_fire():
    firebaseConfig = {
        "apiKey": "AIzaSyCoCxbmJVfVd3ZgD5Mlozi5jDoW4t7_j-Q",
        "authDomain": "hnd-fire.firebaseapp.com",
        "databaseURL": "https://hnd-fire-default-rtdb.europe-west1.firebasedatabase.app",
        "projectId": "hnd-fire",
        "storageBucket": "hnd-fire.appspot.com",
        "messagingSenderId": "867594392762",
        "appId": "1:867594392762:web:7ae45244a2f6f812741e83",
        "measurementId": "G-2VWFXC9HP2"
    }

    firebase = pyrebase.initialize_app(firebaseConfig)
    db = firebase.database()
    return db

def close_server():
    command = ""
    while command != "exit":
        command = input("What to do?: ")
    global server_is_active
    connect_to_fire().update({"server_addr": "inactive"})
    server_is_active = False
    server.close()
    print("Server closed, bye!")

def handle_client(conn, addr, *args):
    while True:
        data = conn.recv(HEADER).decode(FORMAT)
        if not data:
            #print("No data")
            time.sleep(.1)
            continue
        data_length = int(data)
        actual_data = conn.recv(data_length).decode(FORMAT)
        if actual_data == DISCONNECT_MESSAGE:
            break
        command_info = dict([command_pair.split(":") for command_pair in actual_data.split(",")])
        required_job = globals()[command_info.pop("job")]
        thread = threading.Thread(target=required_job, args=(command_info,))
        thread.start()

        print(f"[Data] {command_info}")

    print(f"finished serving {conn}")
        # "job:sign_up,name:josh,password:cross,status:signup"

def sign_up(creds: dict):
    print(f"{creds['name']} has become one of us")

def sign_in(creds: dict):
    print(f"{creds['name']} has joined the lobby")

def update_game_position(player, game_id, new_game_position):
    pass

def start_game():
    pass


FORMAT = "utf-8"
HEADER = 64
PORT = 8080
HOST = socket.gethostbyname(socket.gethostname())

ADDR = (HOST, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
server_is_active = True

connect_to_fire().update({"server_addr": socket.gethostbyname(socket.gethostname())})
print("Server has started")
while server_is_active:
    conn, addr = server.accept()
    if not server_is_active:
        break
    thread = Thread(target=handle_client, args=(conn, addr))
    thread.start()
    server_closer = Thread(target=close_server)
    server_closer.start()
    print(f"Connected received by: {addr} \n")

print("Server is closed finally")

