import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 8007
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "UTF-8"
DISCONNECT_MSG = "disconnect"

def handleClient(conn, addr):
    print(f"> New connection with {addr[0]}:{addr[1]} is connected.")
    connected = True
    while connected:
        recv_msg = conn.recv(SIZE).decode(FORMAT)
        print(f"> Message from client {addr[0]}:{addr[1]} : {recv_msg}")
        send_msg = f"MSG was received by server"
        if recv_msg.lower() == DISCONNECT_MSG:
            send_msg += f"\n\t - Server is disconnected"
            connected = False

        conn.send(send_msg.encode(FORMAT))
    conn.close()

def main():
    print("> Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handleClient, args=(conn, addr))
        thread.start()
        print(f"> Current Active Connections : {threading.active_count() - 1}")

if __name__ == "__main__":
    main()