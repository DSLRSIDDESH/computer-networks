# connection.py
# CS21B2019 
# DEVARAKONDA SLR SIDDESH
import socket
import threading
import pickle

IP = ''
PORT = 4000
SIZE, FORMAT = 1024, 'UTF-8'
DISCONNECT_MSG = "disconnect"
clients = []

server_0_clients = []
server_clients = dict()

for i in range(0, 5):
    server_clients[i] = {}

def not_in_any_server(client_id):
    if client_id in server_clients[4]:
        return False
    return True

def check_acceptance(server_num, client_id):
    if client_id in server_clients[1] and not_in_any_server(client_id) and server_num != 1:
        if server_num in {2, 3}:
            return 'Accept'
        elif server_num == 0:
            for i in [2, 3]:
                if client_id in server_clients[i]:
                    conn_obj = server_clients[i][client_id]
                    print(f'> Server-{i} disconnecting client-{client_id}')
                    conn_obj.close()
            return 'Accept'
        elif server_num == 4:
            return 'Reject'

    elif client_id in server_clients[4] and server_num != 4:
        if server_num in {1, 2, 3}:
            return 'Accept'
        if server_num == 0:
            for i in [1, 2, 3]:
                if client_id in server_clients[i]:
                    conn_obj = server_clients[i][client_id]
                    server_clients[i].pop(client_id)
                    print(f'> Server-{i} disconnecting client-{client_id}')
                    conn_obj.close()
            return 'Accept'
    
    elif server_num != 0:
        if client_id in server_0_clients:
            return 'Reject'
        else:
            return 'Accept'

    else:
        if server_num == 0:
            server_0_clients.append(client_id)
        return 'Accept'

def handle_connection(server, server_num):
    server.bind((IP, PORT + server_num))
    server.listen()
    # servers[server_num] = server
    while True:
        conn, addr = server.accept()
        client_id = conn.recv(1024).decode(FORMAT)

        response = check_acceptance(server_num, client_id)

        if response == 'Reject':
            conn.close()
            print(f'> Server-{server_num} rejected request from client-{client_id}')
        elif response == 'Accept':
            server_clients[server_num][client_id] = conn
            print(f'> Server-{server_num} accepted request from client-{client_id}')
        # elif type(response) == tuple:
        #     print(f'> Server-{response[0]} disconnecting client-{client_id}')
        #     response[1].close()
        else:
            print('Something wrong happened')

def main():
    print("> Servers are starting...")

    server0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server0.bind((IP, PORT + 0))

    server1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server1.bind((IP, PORT + 1))

    server2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server2.bind((IP, PORT + 2))

    server3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server3.bind((IP, PORT + 3))

    server4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server4.bind((IP, PORT + 4))

    # server0.listen()
    # server1.listen()
    # server2.listen()
    # server3.listen()
    # server4.listen()

    server0 = threading.Thread(target = handle_connection, args = (server0, 0))
    server0.start()
    print("> Server-0 Started...")

    server1 = threading.Thread(target = handle_connection, args = (server1, 1))
    server1.start()
    print("> Server-1 Started...")

    server2 = threading.Thread(target = handle_connection, args = (server2, 2))
    server2.start()
    print("> Server-2 Started...")

    server3 = threading.Thread(target = handle_connection, args = (server3, 3))
    server3.start()
    print("> Server-3 Started...")

    server4 = threading.Thread(target = handle_connection, args = (server4, 4))
    server4.start()
    print("> Server-4 Started...")

if __name__ == "__main__":
    main()