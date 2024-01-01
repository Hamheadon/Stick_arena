import socket
import pyrebase

HEADER_LENGTH = 64
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

def grab_server_address():
    return connect_to_fire().child("server_addr").get().val()

def connect_to_server():
    port = 8080
    HOST = grab_server_address()
    if HOST == "inactive":
        print("Server is inactive")
        return 404
    ADDR = (HOST, port)
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(ADDR)
    return 200

def send_command(msg):
    message = msg.encode("utf-8")
    msg_length = len(message)
    send_length = str(msg_length).encode("utf-8")
    if not server_socket:
        connection_attempt = connect_to_server()
    else:
        connection_attempt = 200
    if connection_attempt == 200:
        server_socket.send(send_length + (b" " * (HEADER_LENGTH - len(send_length))))
        server_socket.send(message)
    return connection_attempt


server_socket = None
"""
curr_command = None
while curr_command != "leave":
    curr_command = input("Enter your command: ")
    send_command(curr_command)

print("Byee!")
"""

