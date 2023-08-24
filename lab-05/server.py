import socket
import threading
import readline

IP = socket.gethostbyname(socket.gethostname())
PORT = 8205
ADDR = (IP, PORT)
SIZE, FORMAT = 1024, "UTF-8"
DISCONNECT_MSG = "disconnect"
clients = []

current_input = ""
def print_msg(msg):
    input_buffer = readline.get_line_buffer()
    print(f"\r{msg}\n{current_input}{input_buffer}",end="",flush=True)

def input_msg(input_str):
    global current_input
    current_input = input_str
    output = input(f"\r{input_str}")
    return output

def find_conn(addr):
    for conn, client_addr in clients:
        if client_addr == addr:
            return conn
    return None

def handle_client(conn, addr):
    print_msg(f"> [New Connection] {addr[0]}:{addr[1]} is connected.")
    send_ms = "\r[Server] Successfully received "

    file_path = ''
    while True:
        recv_msg = conn.recv(SIZE).decode(FORMAT)
        msg_type, msg = recv_msg.split(';')

        if msg == DISCONNECT_MSG:
            print_msg(f"> [Disconnected] {addr[0]}:{addr[1]} has disconnected.")
            clients.remove((conn, addr))
            break
        
        if msg_type == 'f':
            file_path = recv_msg.split(';')[1]
            with open(f'server/{file_path}', 'w'):
                pass
            send_msg = 'w;' + send_ms + "file name."
            conn.send(send_msg.encode(FORMAT))

            file_data = conn.recv(SIZE).decode(FORMAT)
            with open(f'server/{file_path}', 'w') as file:
                file.write(file_data)
            
            send_msg = 'w;' + send_ms + "file data."
            conn.send(send_msg.encode(FORMAT))
        
        elif msg_type == 'w':
            msg = recv_msg.split(';')[1]
            print_msg(msg)
    
    conn.close()

def send_file():
    while True:
        if len(clients) == 0:
            continue
        
        ip, port = input_msg("\n[Send file] Enter the ip:port : ").split(':')
        conn = find_conn((ip, int(port)))

        if conn == None:
            print_msg("> [Error] Invalid ip:port")
            continue
        file_path = input_msg("Enter the file name : ")

        conn.send(f"f;{file_path}".encode(FORMAT))
        if file_path.split('/')[0] == DISCONNECT_MSG:
            break

        with open( f"server/{file_path}", 'r') as file:
            file_data = file.read()
        conn.send(f"f;{file_data}".encode(FORMAT))

def main():
    print_msg("> Server is starting...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    server.listen()
    print_msg(f"> Server is listening on {IP}:{PORT}")
    print_msg(f"> [Active Connections] {threading.active_count() - 1}\n")

    send_thread = threading.Thread(target=send_file, args=())
    send_thread.start()

    while True:
        conn, addr = server.accept()
        clients.append((conn, addr))

        client_thread = threading.Thread(target = handle_client, args=(conn, addr))
        client_thread.start()

        print_msg(f"> [Active Connections] {threading.active_count() - 2}")
    
if __name__ == "__main__":
    main()