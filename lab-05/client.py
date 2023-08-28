import socket                                               # importing libraries
import threading
import readline

IP = socket.gethostbyname(socket.gethostname())             # getting ip address
PORT = 8304
ADDR = (IP, PORT)                                           # address
SIZE, FORMAT = 1024, "UTF-8"
DISCONNECT_MSG = "disconnect"
file_status = 0

current_input = ""
def print_msg(msg):                                         # to print exact statement in same line in terminal
    print(f"\r{msg}\n{current_input}",end="",flush=True)

def input_msg(input_str):                                   # to take input from user in same line in terminal
    global current_input
    current_input = input_str
    output = input(f"\r{input_str}")
    return output

def handle_server(client):                                  # handle server to send and receive file
    file_path = ''
    send_ms  = "\r[Client] Successfully received "
    msg_type, msg = '', ''

    while True:
        recv_msg = client.recv(SIZE).decode(FORMAT)         # receive message from server
        msg_type, msg = recv_msg.split(';')

        if msg == DISCONNECT_MSG:                           # disconnect client if client send disconnect message
            break
        
        if msg_type == 'f':                                 # to receive file from client
            print_msg("> Received file name from server.")
            file_path = recv_msg.split(';')[1]
            with open(f'client/{file_path}', 'w'):          # create file with file name sent by client
                pass
            send_msg = 'w;' + send_ms + "file name."
            client.send(send_msg.encode(FORMAT))            # send message to client that file name is received

            file_data = client.recv(SIZE).decode(FORMAT)    # receive file data from client
            print_msg("> Received file data from server.")
            file_data = file_data.split(';')[1]
            with open(f'client/{file_path}', 'w') as file:  # write file data to file
                file.write(file_data)
            print_msg("> File is saved in client successfully.")
            
            send_msg = 'w;' + send_ms + "file data."
            client.send(send_msg.encode(FORMAT))            # send message to client that file data is received

        elif msg_type == 'w':                               # print message received from client if msg is acknoledgement
            msg = recv_msg.split(';')[1]
            print_msg(msg)

    client.close()


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket

    client.connect(ADDR)                                        # connect to server
    print_msg(f"> Client connected to {IP}:{PORT}")             

    server_thread = threading.Thread(target=handle_server, args=(client,))
    server_thread.start()                                       # start thread to handle server

    connected = True
    while connected:
        file_path = input_msg("Enter the file name : ")       # take file name from user

        client.send(f'f;{file_path}'.encode(FORMAT))            # send file name to server
        if file_path == DISCONNECT_MSG:
            break

        with open(f"client/{file_path}", 'r') as file:          # read file data from file
            file_data = file.read()

        client.send(f'{file_data}'.encode(FORMAT))              # send file data to server

    print_msg(f"> [Disconnect] disconnected from server.")
    client.close()                                              # close connection

if __name__ == "__main__":
    main()