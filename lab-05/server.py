import socket                                               # importing libraries
import threading

IP = socket.gethostbyname(socket.gethostname())             # getting ip address
PORT = 8305                                                 # port number
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

    file_path = ''
    while True:
        recv_msg = conn.recv(SIZE).decode(FORMAT)
        msg_type, msg = recv_msg.split(';')

        if msg == DISCONNECT_MSG:                           # disconnect client if client send disconnect message
            print_msg(f"> [Disconnected] {addr[0]}:{addr[1]} has disconnected.")
            clients.remove((conn, addr))
            break
        
        if msg_type == 'f':                                 # to receive file from client
            print_msg("> Received file name from client.")
            file_path = recv_msg.split(';')[1]
            with open(f'server/{file_path}', 'w'):          # create file with file name sent by client
                pass
            send_msg = 'w;' + send_ms + "file name."
            conn.send(send_msg.encode(FORMAT))              # send message to client that file name is received

            file_data = conn.recv(SIZE).decode(FORMAT)      # receive file data from client
            print_msg("> Received file data from client.")
            with open(f'server/{file_path}', 'w') as file:
                file.write(file_data)                       # write file data to file
            print_msg("> File is saved in server successfully.")
            
            send_msg = 'w;' + send_ms + "file data."
            conn.send(send_msg.encode(FORMAT))              # send message to client that file data is received
        
        elif msg_type == 'w':                               # print message received from client if msg is acknoledgement
            msg = recv_msg.split(';')[1]
            print_msg(msg)
    
    conn.close()

def send_file():                                            # to send file to client
    while True:
        if len(clients) == 0:
            continue
        
        ip, port = input_msg("[Send file] Enter the ip:port : ").split(':')   # get ip address and port number from user
        conn = find_conn((ip, int(port)))                   # find connection from clients using ip address

        if conn == None:                                    # if connection is not found, print error message
            print_msg("> [Error] Invalid ip:port")
            continue
        file_path = input_msg("Enter the file name : ")     # get file name from user

        conn.send(f"f;{file_path}".encode(FORMAT))          # send file name to client
        if file_path.split('/')[0] == DISCONNECT_MSG:
            break

        with open( f"server/{file_path}", 'r') as file:     # read file data from file
            file_data = file.read()
        conn.send(f"f;{file_data}".encode(FORMAT))          # send file data to client

def main():
    print_msg("> Server is starting...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
    server.bind(ADDR)                                           # bind socket to address = (ip, port)

    server.listen()                                             # listen to socket
    print_msg(f"> Server is listening on {IP}:{PORT}")
    # print_msg(f"> [Active Connections] {threading.active_count() - 1}")

    send_thread = threading.Thread(target=send_file, args=())   # create thread to send file
    send_thread.start()                                         

    while True:
        conn, addr = server.accept()                            # accept connection from client
        clients.append((conn, addr))                            # add client to clients list

        client_thread = threading.Thread(target = handle_client, args=(conn, addr))
        client_thread.start()                                   # create thread to handle client

        print_msg(f"> [Active Connections] {threading.active_count() - 2}")
        # print thread_count-2 because send_thread and client_thread is not client thread
    
if __name__ == "__main__":
    main()