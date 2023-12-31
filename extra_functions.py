import socket
import pyrebase

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
    ADDR = (HOST, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(ADDR)
    return s

def send_command(msg):
    message = msg.encode("utf-8")
    msg_length = len(message)
    send_length = str(msg_length).encode("utf-8")
    client = connect_to_server()
    client.send(send_length)
    client.send(message)

send_command("Hello")