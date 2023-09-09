# server.py
# CS21B2019 DEVARAKONDA SLR SIDDESH
import socket                                               # importing libraries
import threading

IP = socket.gethostbyname(socket.gethostname())             # getting ip address
PORT = 8002                                                 # port number
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

def handle_client(conn, addr):                              # handle client to receive and send file
    print_msg(f"> [New Connection] {addr[0]}:{addr[1]} is connected.")
    send_ms = "\r[Server] Successfully received "

    while True:
        recv_msg = conn.recv(SIZE).decode(FORMAT)           # receive message from a client

        if recv_msg == DISCONNECT_MSG:                      # disconnect client if client send disconnect message
            print_msg(f"> [Disconnected] {addr[0]}:{addr[1]} has disconnected.")
            clients.remove((conn, addr))
            break
            
        msg_type = recv_msg.split(';')[0]                   # msg type (file or acknowledgement)
        neigh_client = recv_msg.split(';')[1]               # the client we intend to send msg to (ip:port)

        neigh_ip = neigh_client.split(':')[0]
        neigh_port = int(neigh_client.split(':')[1])

        neigh_conn = find_conn((neigh_ip, neigh_port))

        curr_ip = addr[0]
        curr_port = str(addr[1])
        
        if msg_type == 'f':                                 # if msg type is file
            file_name = recv_msg.split(';')[2]              # file name

            send_msg = f"f;{curr_ip}:{curr_port};{file_name}"

            neigh_conn.send(send_msg.encode(FORMAT))        # send file name to intended client

            file_data = conn.recv(SIZE)                     # receive file data from client
            while file_data:                                # to receive and send file data as packets (1024 bytes at a time until EOF)
                neigh_conn.send(file_data)                  # send file data to intended client
                if file_data == b'EOF':
                    break
                file_data = conn.recv(SIZE)
        
        elif msg_type == 'w':                               # if msg type is acknowledgement
            msg = recv_msg.split(';')[2]

            send_msg = f"w;{curr_ip}:{curr_port};{msg}"
            neigh_conn.send(send_msg.encode(FORMAT))        # send acknowledgement to client
    
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
        client_thread.start()                                   # create thread to handle clients

        print_msg(f"> [Active Connections] {threading.active_count() - 1}")
        # print thread_count-1 because send_thread and client_thread is not client thread
    
if __name__ == "__main__":
    main()