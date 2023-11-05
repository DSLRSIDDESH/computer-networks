# connection.py
# CS21B2019 
# DEVARAKONDA SLR SIDDESH
import socket
import threading
import pickle

IP = ''
PORT = 9100
SIZE, FORMAT = 1024, 'UTF-8'
DISCONNECT_MSG = "disconnect"
clients = []
connect_sr = False
client_id = ''

server_0_clients = []
server_clients = dict()

for i in range(0, 5):
    server_clients[i] = {}

def server_s(server, server_num):
    global connect_sr, client_id
    server.bind((IP, PORT + server_num))
    server.listen()
    conn = ''
    client_count = 1
    while True:
        if client_count <= 5 and client_id not in server_clients[0]:
            conn, addr = server.accept()
            client_id = conn.recv(1024).decode(FORMAT)
            client_count += 1
            print(f">client-{client_id} connected to server-s")
        else:
            conn.send(f'NO:{PORT + 1}'.encode(FORMAT))
            conn, addr = server.accept()
            client_id = conn.recv(1024).decode(FORMAT)
            conn.send(f'YES'.encode(FORMAT))
            print(f">client-{client_id} not connected to server-s and redirected to server-sr")
            conn.close()

def server_sr(server, server_num):
    global connect_sr
    server.bind((IP, PORT + server_num))
    server.listen()

    while True:
        conn, addr = server.accept()
        client_id = conn.recv(1024).decode(FORMAT)
        print(f">{client_id} connected to server-sr")
    



def main():
    print("> Servers are starting...")

    server0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server0.bind((IP, PORT + 0))

    server1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server1.bind((IP, PORT + 1))

    server0 = threading.Thread(target = server_s, args = (server0, 0))
    server0.start()
    print("> Server-0 Started...")

    server1 = threading.Thread(target = server_sr, args = (server1, 1))
    server1.start()
    print("> Server-1 Started...")

if __name__ == "__main__":
    main()