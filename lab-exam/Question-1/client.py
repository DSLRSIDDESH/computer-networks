# client.py
# CS21B2019
# DEVARAKONDA SLR SIDDESH
import socket
import threading
import random

IP = ''
PORT = 4000
SIZE, FORMAT = 1024, "UTF-8"
DISCONNECT_MSG = "disconnect"

S0_PORT = PORT
S1_PORT = PORT + 1
S2_PORT = PORT + 2
S3_PORT = PORT + 3
S4_PORT = PORT + 4

final_port = 8000

def main():
    client_id = input("Enter your ID : ")

    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
        server_num = int(input("Enter the server number you want to connect (0 to 4 only) : "))

        if server_num == 0:
            final_port = S0_PORT
        elif server_num == 1:
            final_port = S1_PORT
        elif server_num == 2:
            final_port = S2_PORT
        elif server_num == 3:
            final_port = S3_PORT
        elif server_num == 4:
            final_port = S4_PORT
        else:
            print("Please enter a correct server number")
            continue
        ADDR = (IP, final_port)

        client.connect(ADDR)
        client.send(client_id.encode(FORMAT))

if __name__ == "__main__":
    main()