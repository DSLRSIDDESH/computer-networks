import socket
import threading
import readline

IP = socket.gethostbyname(socket.gethostname())
PORT = 8205
ADDR = (IP, PORT)
SIZE, FORMAT = 1024, "UTF-8"
DISCONNECT_MSG = "disconnect"
file_status = 0

current_input = ""
def print_msg(msg):
    input_buffer = readline.get_line_buffer()
    print(f"\r{msg}\n{current_input}{input_buffer}",end="",flush=True)

def input_msg(input_str):
    global current_input
    current_input = input_str
    output = input(f"\r{input_str}")
    return output

def handle_server(client):
    file_path = ''
    send_ms  = "\r[Client] Successfully received "
    msg_type, msg = '', ''

    while True:
        recv_msg = client.recv(SIZE).decode(FORMAT)
        msg_type, msg = recv_msg.split(';')

        if msg == DISCONNECT_MSG:
            break
        
        if msg_type == 'f':
            file_path = recv_msg.split(';')[1]
            with open(f'client/{file_path}', 'w'):
                pass
            send_msg = 'w;' + send_ms + "file name."
            client.send(send_msg.encode(FORMAT))

            file_data = client.recv(SIZE).decode(FORMAT)
            file_data = file_data.split(';')[1]
            with open(f'client/{file_path}', 'w') as file:
                file.write(file_data)
            
            send_msg = 'w;' + send_ms + "file data."
            client.send(send_msg.encode(FORMAT))

        elif msg_type == 'w':
            msg = recv_msg.split(';')[1]
            print_msg(msg)

    client.close()


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect(ADDR)
    print_msg(f"> Client connected to {IP}:{PORT}")

    server_thread = threading.Thread(target=handle_server, args=(client,))
    server_thread.start()

    connected = True
    while connected:
        file_path = input_msg("\nEnter the file name : ")

        client.send(f'f;{file_path}'.encode(FORMAT))
        if file_path == DISCONNECT_MSG:
            break

        with open(f"client/{file_path}", 'r') as file:
            file_data = file.read()

        client.send(f'{file_data}'.encode(FORMAT))

    print_msg(f"> [Disconnect] disconnected from server.")
    client.close()

if __name__ == "__main__":
    main()