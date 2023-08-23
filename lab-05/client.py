import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 8008
ADDR = (IP, PORT)
SIZE, FORMAT = 1024, "UTF-8"
DISCONNECT_MSG = "disconnect"
file_status = 0

def handle_server(client):
    file_path = 'client/'
    send_msg = "[Client] Successfully received "

    while True:
        recv_msg = client.recv(SIZE).decode(FORMAT)
        if recv_msg == DISCONNECT_MSG:
            break

        if file_status == 0:
            file_path += recv_msg
            with open(file_path, 'w'):
                pass

            send_msg = send_msg + "file path."
            client.send(send_msg.encode(FORMAT))
            file_status = 1
        
        elif file_status == 1:
            file_data = recv_msg
            with open(file_path, 'r') as file:
                file.write(file_data + "\n")

            send_msg = send_msg + "file data."
            client.send(send_msg.encode(FORMAT))
            file_status = 0

    client.close()


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect(ADDR)
    print(f"> Client connected to {IP}:{PORT}")

    server_thread = threading.Thread(target=handle_server, args=(client,))
    server_thread.start()

    file_path = 'client/'
    num_send = 2
    for i in range(num_send):
        if i == 0:
            file_path += input("Enter the file name : ")
            client.send(file_path.encode(FORMAT))

            recv_msg = client.recv(SIZE).decode(FORMAT)
            if recv_msg == DISCONNECT_MSG:
                break
            print(recv_msg)

        elif i == 1:
            with open(file_path, 'r') as file:
                file_data = file.read()
            client.send(file_data.encode(FORMAT))

            recv_msg = client.recv(SIZE).decode(FORMAT)
            if recv_msg == DISCONNECT_MSG:
                break
            print(recv_msg)

    print(f"> [Disconnect] disconnected from server.")
    client.close()

if __name__ == "__main__":
    main()