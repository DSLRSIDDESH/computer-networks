import socket
import threading
import sys

IP = socket.gethostbyname(socket.gethostname())
PORT = 8308
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "UTF-8"
DISCONNECT_MSG = "disconnect"
clients = []

def send_message(msg, client):
    conn = None
    for c in clients:
        if c[1] == client:
            conn = c[0]
            break
    if conn is None:
        return False
    try:
        conn.send(msg.encode(FORMAT))
    except OSError:
        return False
    return True

def handleClient(conn, addr):
    print(f"\r> New connection {addr[0]}:{addr[1]} is connected.")

    connected = True
    while connected:
        recv_msg = conn.recv(SIZE).decode(FORMAT)
        if not recv_msg:
            print(f"\r> Client {addr[0]}:{addr[1]} is disconnected.")
            print("\nSend message to (ip:port) : ", end="")
            sys.stdout.flush()
            break

        print(f"\r> Message from client {addr[0]}:{addr[1]} : {recv_msg}")
        send_msg = f"MSG was received by server"

        if recv_msg.lower() == DISCONNECT_MSG:
            send_msg += f"\n\t - Server is disconnected"
            connected = False
            for c in clients:
                if c[1] == addr:
                    clients.remove(c)
                    break

        try:
            conn.send(send_msg.encode(FORMAT))
        except BrokenPipeError:
            print(f"\r> Client {addr[0]}:{addr[1]} is disconnected.")
            connected = False
        print("\nSend message to (ip:port) : ", end="")
        sys.stdout.flush()

    conn.close()

def sendMsg():
    while True:
        client_addr = input("\nSend message to (ip:port) : ")
        client_addr = (client_addr.split(":")[0], int(client_addr.split(":")[1]))

        msg_input = input("Enter your message : ")

        if not send_message(msg_input, client_addr):
            print(f"Message was not sent to {client_addr[0]}:{client_addr[1]}")

def main():
    print("> Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(ADDR)

    server.listen()
    print(f"Server is listening on {IP}:{PORT}")

    thread1 = threading.Thread(target=sendMsg, args=())
    thread1.start()

    while True:
        conn, addr = server.accept()
        clients.append((conn, addr))

        thread2 = threading.Thread(target=handleClient, args=(conn, addr))
        thread2.start()

        print(f"> Current Active Connections : {threading.active_count() - 2}")
        print("\nSend message to (ip:port) : ", end="")
        sys.stdout.flush()

if __name__ == "__main__":
    main()