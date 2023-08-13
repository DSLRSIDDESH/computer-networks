import socket

# IP = socket.gethostbyname(socket.gethostname())
IP = '192.168.2.24'
PORT = 53536
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "UTF-8"
DISCONNECT_MSG = "disconnect"

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"> Client connected to {IP}:{PORT}")

    connected = True
    while connected:
        msg = input("Enter a message: ")
        client.send(msg.encode(FORMAT))
        if msg.lower() == DISCONNECT_MSG:
            connected = False
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"> {msg}")

if __name__ == "__main__":
    main()