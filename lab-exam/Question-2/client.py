# client.py
# CS21B2019
# DEVARAKONDA SLR SIDDESH
import socket
import threading
import random

IP = ''
PORT = 9100
SIZE, FORMAT = 1024, "UTF-8"
DISCONNECT_MSG = "disconnect"

S0_PORT = PORT

final_port = 3000

def main():
    client_id = input("Enter your ID : ")

    # while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket

    ADDR = (IP, PORT)
    client.connect(ADDR)

    client.send(client_id.encode(FORMAT))
    msg = client.recv(1024).decode(FORMAT)
    if 'NO' in msg:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
        p = int(msg.split(':')[1])
        client.connect((IP, p))


if __name__ == "__main__":
    main()