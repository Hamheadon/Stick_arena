import socket


def connect_to_server():
    port = 8080
    HOST = socket.gethostbyname(socket.gethostname())
    ADDR = (HOST, port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
