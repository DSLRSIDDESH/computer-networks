import socket                                               # importing libraries
import threading
from time import sleep

IP = socket.gethostbyname(socket.gethostname())             # getting ip address
PORT = 8007
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
    file_name = ''

    while True:
        recv_msg = client.recv(SIZE).decode(FORMAT)         # receive message from server

        msg_type = recv_msg.split(';')[0]
        neigh_client = recv_msg.split(';')[1]
        
        if msg_type == 'f':                                 # to receive file from client
            file_name = recv_msg.split(';')[2]

            print_msg(f"> Received file name from {neigh_client} successfully.")
            with open(f'server/{file_name}', 'wb') as file:        # create file with file name sent by client
                pass

            send_msg = f"w;{neigh_client};[Client] Received file name successfully."
            client.send(send_msg.encode(FORMAT))            # send message that file name is received

            file_data = client.recv(SIZE)
            while file_data != b'EOF':
                with open(f'server/{file_name}', 'ab') as file:
                    file.write(file_data)                   # write file data to file
                file_data = client.recv(SIZE)
            print_msg(f"> Received file data from {neigh_client} successfully.")

            send_msg = f'w;{neigh_client};[Client] Received the file data successfully.'
            client.send(send_msg.encode(FORMAT))            # send message to server that file is received

        elif msg_type == 'w':                               # print message received from client if msg is acknoledgement
            msg = recv_msg.split(';')[2]
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
        neigh_client = input_msg("Enter ip:port of the client to send : ")            # take ip address from user
        if neigh_client.lower() == DISCONNECT_MSG:
            client.send(DISCONNECT_MSG.encode(FORMAT))          # send disconnect message to server
            break

        file_name = input_msg("Enter the file name : ")         # take file name from user

        file = 'f;' + neigh_client + ';' + file_name            # create file name to send to server
        client.send(file.encode(FORMAT))                        # send file name to server

        with open(file_name, 'rb') as file:                     # check if file exists or not
            while True:
                file_data = file.read(SIZE)
                if not file_data:
                    sleep(0.1)
                    client.send(b"EOF")
                    break
                client.send(file_data)                          # send file data to server

    print_msg(f"> [Disconnect] disconnected from server.")
    client.close()                                              # close connection

if __name__ == "__main__":
    main()