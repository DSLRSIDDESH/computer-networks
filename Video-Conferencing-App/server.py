import socket
import threading
import time
import os
import pickle
from dataclasses import dataclass, field
from communication import *

# Server IP and port
IP = ''
MAIN_PORT = 7000
VIDEO_PORT = MAIN_PORT + 1
AUDIO_PORT = MAIN_PORT + 2

# Server address
MAIN_ADDR = (IP, MAIN_PORT)
VIDEO_ADDR = (IP, VIDEO_PORT)
AUDIO_ADDR = (IP, AUDIO_PORT)

VIDEO = 'video'
AUDIO = 'audio'
ADD = 'add'
RM = 'rm'
DISCONNECT_MSG = 'disconnect'
MEDIA_SIZE = {VIDEO: 25000, AUDIO: 4500}


clients = {} # list of clients connected to the server
video_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
audio_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
media_conns = {VIDEO: video_conn, AUDIO: audio_conn}

@dataclass
class Client:
    name: str
    main_conn: socket.socket
    addr: str
    connected: bool
    media_addrs: dict = field(default_factory= lambda: {VIDEO: None, AUDIO: None})
    

def disconnect_client(client: Client):
    global clients
    print(f"[DISCONNECTING] {client.name} disconnected from Main Server")
    client.media_addrs[VIDEO] = None
    client.media_addrs[AUDIO] = None
    msg = Message(client.name, RM)
    for client_name in clients:
        if client_name != client.name:
            client_conn = clients[client_name].main_conn
            client_conn.send_bytes(pickle.dumps(msg))

    client.connected = False
    client.main_conn.disconnect()
    
    clients.pop(client.name)

# def handle_media(name: str, media: str):
#     client = clients[name]
#     if media == VIDEO:
#         conn = client.video_conn
#     elif media == AUDIO:
#         conn = client.audio_conn

#     while client.connected:
#         msg_bytes = conn.recv_bytes()
#         if not msg_bytes:
#             break
#         msg = pickle.loads(msg_bytes)
#         if msg.request == DISCONNECT_MSG:
#             break
#         # send media to all clients
#         msg = Message(name, msg.request, media, msg.data)
#         for client_name in clients:
#             if client_name != name:
#                 client_conn = None
#                 if media == VIDEO:
#                     client_conn = clients[client_name].video_conn
#                 elif media == AUDIO:
#                     client_conn = clients[client_name].audio_conn
#                 else:
#                     print(f"[ERROR] Invalid media type: {media}")
#                     continue
#                 if client_conn:
#                     client_conn.send_bytes(pickle.dumps(msg))

#     conn.disconnect()
#     if media == VIDEO:
#         client.video_conn = None
#     elif media == AUDIO:
#         client.audio_conn = None

def handle_client(name: str):
    client = clients[name]
    conn = client.main_conn

    # Add all clients to current client
    for client_name in clients:
        msg = Message(client_name, ADD)
        if client_name != name:
            conn.send_bytes(pickle.dumps(msg))
    
    # Add current client to all clients
    msg = Message(name, ADD)
    for client_name in clients:
        if client_name != name:
            client_conn = clients[client_name].main_conn
            client_conn.send_bytes(pickle.dumps(msg))

    while client.connected:
        msg_bytes = conn.recv_bytes()
        if not msg_bytes:
            break
        msg = pickle.loads(msg_bytes)
        if msg.request == DISCONNECT_MSG:
            break
        for name in msg.to_names:
            if name not in clients:
                continue
            client_conn = clients[name].main_conn
            client_conn.send_bytes(pickle.dumps(msg))
    
    disconnect_client(client)

def media_server(media: str):
    if media == VIDEO:
        PORT = VIDEO_PORT
    elif media == AUDIO:
        PORT = AUDIO_PORT

    conn = media_conns[media]
    conn.bind((IP, PORT))

    print(f"[LISTENING] {media} Server is listening on {IP}:{PORT}")

    while True:
        msg_bytes, addr = conn.recvfrom(MEDIA_SIZE[media])
        
        msg = pickle.loads(msg_bytes)
        name = msg.from_name
        if msg.request == ADD:
            clients[name].media_addrs[media] = addr
            print(f"[CONNECTING] {name} connected to {media} Server")
        else:
            for client_name, client in clients.items():
                if client_name != name:
                    addr = client.media_addrs[media]
                    if addr is not None:
                        conn.sendto(msg_bytes, addr)
        

def main():
    global clients
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.bind((IP, MAIN_PORT))

    main_socket.listen()
    print(f"[LISTENING] Main Server is listening on {IP}:{MAIN_PORT}")

    video_thread = threading.Thread(target=media_server, args=(VIDEO,))
    video_thread.start()

    audio_thread = threading.Thread(target=media_server, args=(AUDIO,))
    audio_thread.start()

    while True:
        conn, addr = main_socket.accept()

        # send names of all clients to new client
        # names_list = list(clients.keys())
        # conn.send_bytes(pickle.dumps(names_list))

        # receive name of the new client
        name = conn.recv_bytes().decode()
        clients[name] = Client(name, conn, addr, True)
        print(f"[NEW CONNECTION] {name} connected to Main Server")

        client_thread = threading.Thread(target=handle_client, args=(name,))
        client_thread.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"[EXITING] Keyboard Interrupt")
        for client in clients.values():
            disconnect_client(client)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        os._exit(0)