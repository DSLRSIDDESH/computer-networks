import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 8008
ADDR = (IP, PORT)
SIZE, FORMAT = 1024, "UTF-8"
DISCONNECT_MSG = "disconnect"
clients = []
file_status = 0

def find_conn(addr):
    for conn, client_addr in clients:
        if client_addr == addr:
            return conn
    return None

def handle_client(conn, addr):
    print(f"> [New Connection] {addr[0]}:{addr[1]} is connected.")

    file_path = ''
    num_recv = 2
    for i in range(num_recv):
        recv_msg = conn.recv(SIZE).decode(FORMAT)
        send_msg = "[Server] Successfully received "

        if recv_msg == DISCONNECT_MSG:
            print(f"> [Disconnected] {addr[0]}:{addr[1]} has disconnected.")
            conn.send(DISCONNECT_MSG.encode(FORMAT))
            clients.remove((conn, addr))
            break

        if i == 0:
            file_path = 'server/' + recv_msg
            with open(file_path, 'w'):
                pass

            send_msg = send_msg + "file path."
            conn.send(send_msg.encode(FORMAT))

        elif i == 1:
            file_data = recv_msg
            with open(file_path, 'a') as file:
                file.write(file_data + "\n")

            send_msg = send_msg + "file data."
            conn.send(send_msg.encode(FORMAT))
    
    conn.close()

def send_file():
    while True:
        if len(clients) == 0:
            continue
        
        ip, port = input("[Send file] Enter the ip:port : ").split(':')
        conn = find_conn((ip, int(port)))

        if conn == None:
            print("> [Error] Invalid ip:port")
            continue

        file_path = 'server/'
        if file_status == 0:
            file_path += input("Enter the file name : ")
            conn.send(file_path.encode(FORMAT))

            recv_msg = conn.recv(SIZE).decode(FORMAT)
            print(recv_msg)
            file_status = 1
        
        elif file_status == 1:
            with open(file_path, 'r') as file:
                file_data = file.read()
            conn.send(file_data.encode(FORMAT))

            recv_msg = conn.recv(SIZE).decode(FORMAT)
            print(recv_msg)
            file_status = 0

def main():
    print("> Server is starting...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    server.listen()
    print(f"> Server is listening on {IP}:{PORT}")
    print(f"> [Active Connections] {threading.active_count() - 1}\n")

    send_thread = threading.Thread(target=send_file, args=())
    send_thread.start()

    while True:
        conn, addr = server.accept()
        clients.append((conn, addr))

        client_thread = threading.Thread(target = handle_client, args=(conn, addr))
        client_thread.start()

        print(f"> [Active Connections] {threading.active_count() - 2}")
    
if __name__ == "__main__":
    main()