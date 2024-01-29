import socket

from extra_functions import connect_to_server

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")

def test_connection():
    result = connect_to_server()
    if result == 200:
        print("Connection successful.")
    elif result == 404:
        print("Server is inactive.")
    else:
        print("Connection failed.")

if __name__ == "__main__":
    test_connection()

