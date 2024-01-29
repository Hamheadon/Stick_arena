import json
import os.path
import pickle
import socket
import threading
import time
from threading import Thread
import pyrebase
players_online = {}
active_games = {}
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
    # jobs_data holds all the required data dictionaries for all the assigned job_funcs
    jobs_data = {}
    while True:
        print(f"Currently serving {addr}")
        data = conn.recv(HEADER).decode(FORMAT)
        if not data:
            #print("No data")
            time.sleep(.1)
            continue
        data_length = int(data)
        actual_data = conn.recv(data_length).decode(FORMAT)
        if actual_data == DISCONNECT_MESSAGE:
            break
        command_info = dict([command_pair.split(":") for command_pair in actual_data.split(",")])  # the data user has sent to us
        job = command_info.pop("job")
        job_func = globals()[job]  # job_func is the received function (found via the string held by job variable) the user wants us to serve them with
        command_info.update({"still_connected": True})
        jobs_data[job] = command_info
        thread = threading.Thread(target=job_func, args=(command_info, conn, addr))
        thread.start()

    for val in jobs_data.values():
        val["still_connected"] = False
    conn.close()
    print(f"finished serving {conn}")
        # "job:sign_up,name:josh,password:cross,status:signup"

def sign_in(creds: dict, conn: socket.socket, *args):
    print("attempting sign in...")
    curr_players = {}
    with open("players.json", "r") as players_file:
        curr_players = json.load(players_file)

    if creds["name"] in curr_players:
        if creds["password"] == curr_players[creds["name"]]["password"]:
            send_data({"success_message": "Successfully signed up! Welcome", "status": "success"}, conn)
            players_online.update({creds["name"]: curr_players[creds["name"]]})
            send_lobby_data(conn, creds)
        else:
            send_data({"fail_message": "The password is incorrect", "status": "fail"}, conn)
    else:
        send_data({"fail_message": "That username does not exist", "status": "fail"}, conn)

    print(f"{creds['name']} has joined the lobby")

def sign_up(creds: dict, conn: socket.socket, addr=None, *args):
    print(f"{creds['name']} has become one of us")
    current_players = {}
    if os.path.exists("players.json"):
        with open("players.json", "r") as players_file:
            current_players = json.load(players_file)
    fresh_stats = {"kills": 0, "deaths": 0, "wins": 0, "losses": 0, "win_rate": 0,
                                            "spinners": []}
    current_players.update({creds["name"]: fresh_stats})
    with open("players.json", "w") as players_file:
        json.dump(current_players, players_file)
    players_online[creds["name"]] = fresh_stats
    send_lobby_data(conn, creds)

def send_data(data: dict, conn: socket.socket, *args):
    bytes_data = pickle.dumps(data)
    data_len = len(bytes_data)
    send_length = str(data_len).encode(FORMAT)
    print(f"sending to {conn.getsockname()}")
    conn.send(send_length + (b" " * (HEADER - len(send_length))))
    conn.send(bytes_data)

def send_lobby_data(conn: socket.socket, creds: dict, *args):
    while creds["still_connected"]:
        lobby_data = {"players": players_online, "games": active_games}
        send_data(lobby_data, conn)
        time.sleep(1)




def update_game_position(player, game_id, new_game_position):
    pass

def join_game(creds: dict, *args):
    pass

def start_game(info: dict, *args):
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

