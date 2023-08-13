import socket
import threading
import sys
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 8308
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "UTF-8"
DISCONNECT_MSG = "!DISCONNECT"

def handleServer(client):
    connected = True
    while connected:
        try:
            msg = client.recv(SIZE).decode(FORMAT)
        except OSError:
            return
        if msg.lower() == DISCONNECT_MSG:
            connected = False
        else:
            print(f"\rMessage from server : {msg}")
            print("Enter a message: ", end="")
            sys.stdout.flush()

    print("\rDisconnected from server")
    client.close()
    os._exit(0)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"> Client connected to {IP}:{PORT}")

    thread = threading.Thread(target=handleServer, args=(client,))
    thread.start()

    connected = True
    while connected:
        msg = input("Enter a message: ")
        try:
            client.send(msg.encode(FORMAT))
        except OSError:
            return
        if msg.lower() == DISCONNECT_MSG:
            connected = False

    client.close()

if __name__ == "__main__":
    main()