import socket
from threading import Thread

players_online = {}

def handle_client(conn, addr, *args):
    print()
    while True:
        data = conn.recv(HEADER).decode(FORMAT)
        if not data:
            continue
        data_length = int(data)
        actual_data = conn.recv(data_length).decode(FORMAT)

        # "job:sign_up/name:josh,password:cross,status:signup"

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
server_is_active = False

while server_is_active:
    conn, addr = server.accept()
    thread = Thread(target=handle_client, args=(conn, addr))
    thread.start()


