import socket
import threading
import sys

IP = socket.gethostbyname(socket.gethostname())
PORT = 8026
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "UTF-8"
DISCONNECT_MSG = "disconnect"

def handle_client(client):
    connected = True
    while connected:
        try:
            msg = client.recv(SIZE).decode(FORMAT)
        except OSError:
            return
        sender_client = msg.split("&")[0]
        type = msg.split("&")[2]
        msg = msg.split("&")[1]

        print(f"\r[Client - {sender_client}] : {msg}\n")
        print("Enter ip:addr : ", end="")
        sys.stdout.flush()

        if type != 'ack':
            ack = f"Message recieved]\n"
            send_msg = sender_client + "&" + ack + '&ack'

            client.send(send_msg.encode(FORMAT))

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect(ADDR)
    print(f"> Client connected to {IP}:{PORT}")

    client_thread = threading.Thread(target = handle_client, args = (client,))
    client_thread.start()

    connected = True
    while connected:
        neigh_client = input("Enter ip:port : ")
        if neigh_client.lower() != DISCONNECT_MSG:
            msg = input("Enter a message: ")
            msg = neigh_client + "&" + msg + '&msg'
            client.send(msg.encode(FORMAT))
        else:
            client.send(DISCONNECT_MSG.encode(FORMAT))
            connected = False
    client.close()

if __name__ == "__main__":
    main()