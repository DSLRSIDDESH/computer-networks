import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 8025
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "UTF-8"
DISCONNECT_MSG = "disconnect"
clients = []

def find_conn(addr):
    conn = None
    for client in clients:
        if client[1] == addr:
            conn = client[0]
    return conn

def remove_conn(addr):
    for client in clients:
        if client[1] == addr:
            clients.remove(client)
            break

def handle_client(conn, addr):
    print(f"> New connection with {addr[0]}:{addr[1]} is connected.")

    connected = True
    while connected:
        recv_msg = conn.recv(SIZE).decode(FORMAT)
        if recv_msg != DISCONNECT_MSG:
            neigh_addr = recv_msg.split("&")[0]
            neigh_addr = (neigh_addr.split(":")[0], int(neigh_addr.split(":")[1]))

            send_msg = addr[0] + ':' + str(addr[1]) + '&' + recv_msg.split("&")[1] + '&' + recv_msg.split("&")[2]

            neigh_conn = find_conn(neigh_addr)
            if(neigh_conn == None):
                print(f">[Error] No connection with {neigh_addr} exists.")
            else:
                neigh_conn.send(send_msg.encode(FORMAT))
        else:
            remove_conn(addr)
            connected = False
    print(f">\n[Disconnect] Connection with {addr[0]}:{addr[1]} is closed.\n")
    conn.close()

def main():
    print("> Server is starting...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    server.listen()
    print(f"Server is listening on {IP}:{PORT}")

    print(f"> Current Active Connections : {threading.active_count() - 1}\n")

    while True:
        conn, addr = server.accept()
        clients.append((conn, addr))

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        print(f"> Current Active Connections : {threading.active_count() - 1}\n")

if __name__ == "__main__":
    main()