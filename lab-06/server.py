import socket                                               # importing libraries
import threading

IP = socket.gethostbyname(socket.gethostname())             # getting ip address
PORT = 8006                                                 # port number
ADDR = (IP, PORT)
SIZE, FORMAT = 1024, "UTF-8"
DISCONNECT_MSG = "disconnect"
clients = []

current_input = ""
def print_msg(msg):                                         # to print exact statement in same line in terminal
    print(f"\r{msg}\n{current_input}",end="",flush=True)

def input_msg(input_str):                                   # to take input from user in same line in terminal
    global current_input
    current_input = input_str
    output = input(f"\r{input_str}")
    current_input = ""
    return output

def find_conn(addr):                                        # find connection from clients using ip address
    for conn, client_addr in clients:
        if client_addr == addr:
            return conn
    return None

def handle_client(conn, addr):                              # handle client to eceive file
    print_msg(f"> [New Connection] {addr[0]}:{addr[1]} is connected.")
    send_ms = "\r[Server] Successfully received "

    while True:
        recv_msg = conn.recv(SIZE).decode(FORMAT)           # receive message from server

        if recv_msg == DISCONNECT_MSG:                           # disconnect client if client send disconnect message
            print_msg(f"> [Disconnected] {addr[0]}:{addr[1]} has disconnected.")
            clients.remove((conn, addr))
            break
            
        msg_type = recv_msg.split(';')[0]
        neigh_client = recv_msg.split(';')[1]

        neigh_ip = neigh_client.split(':')[0]
        neigh_port = int(neigh_client.split(':')[1])

        neigh_conn = find_conn((neigh_ip, neigh_port))

        curr_ip = addr[0]
        curr_port = str(addr[1])
        
        if msg_type == 'f':                                 # to receive file from client
            file_name = recv_msg.split(';')[2]

            send_msg = f"f;{curr_ip}:{curr_port};{file_name}"

            neigh_conn.send(send_msg.encode(FORMAT))        # send file to intended client

            file_data = conn.recv(SIZE)
            while file_data:
                neigh_conn.send(file_data)   # write file data to file
                if file_data == b'EOF':
                    break
                file_data = conn.recv(SIZE)
        
        elif msg_type == 'w':                               # print message received from client if msg is acknoledgement
            msg = recv_msg.split(';')[2]

            send_msg = f"w;{curr_ip}:{curr_port};{msg}"
            neigh_conn.send(send_msg.encode(FORMAT))
    
    conn.close()

def main():
    print_msg("> Server is starting...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
    server.bind(ADDR)                                           # bind socket to address = (ip, port)

    server.listen()                                             # listen to socket
    print_msg(f"> Server is listening on {IP}:{PORT}")
    print_msg(f"> [Active Connections] {threading.active_count() - 1}")                                         

    while True:
        conn, addr = server.accept()                            # accept connection from client
        clients.append((conn, addr))                            # add client to clients list

        client_thread = threading.Thread(target = handle_client, args=(conn, addr))
        client_thread.start()                                   # create thread to handle client

        print_msg(f"> [Active Connections] {threading.active_count() - 1}")
        # print thread_count-2 because send_thread and client_thread is not client thread
    
if __name__ == "__main__":
    main()