import socket
import pickle
import sys, time, os
from PyQt6.QtCore import QThreadPool, QThread, pyqtSignal, QRunnable, pyqtSlot
from PyQt6.QtWidgets import QApplication
from client_gui import MainWindow, Video, Audio
from communication import *

# Server IP and port
SERVER_IP = '192.168.141.239'
# SERVER_IP = ''
MAIN_PORT = 7000
VIDEO_PORT = MAIN_PORT + 1
AUDIO_PORT = MAIN_PORT + 2

VIDEO_ADDR = (SERVER_IP, VIDEO_PORT)
AUDIO_ADDR = (SERVER_IP, AUDIO_PORT)
MEDIA_SIZE = {'video': 25000, 'audio': 4500}


DISCONNECT_MSG = 'disconnect'
name_list = []

# clients
class Client:
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.video = None
        self.audio = None

        self.video_frame = None
        self.audio_stream = None

        if self.addr is None:
            self.video = Video()
            self.audio = Audio()

    def get_video(self):
        if self.video is not None:
            return self.video.get_frame()

        return self.video_frame
    
    def get_audio(self):
        if self.audio is not None:
            return self.audio.get_stream()

        return self.audio_stream

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)

class ServerConnection(QThread):
    add_client_signal = pyqtSignal(Client)
    remove_client_signal = pyqtSignal(str)
    add_msg_signal = pyqtSignal(Message)

    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()

        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.connected = False

    def run(self):
        while client.name == 'You':
            pass

        self.init_connection()
        self.start_conn_threads()
        self.start_broadcast_threads()

        self.add_client_signal.emit(client)

        while self.connected:
            pass
    
    def init_connection(self):

        self.main_socket.connect((SERVER_IP, MAIN_PORT))



        self.connected = True

        print("Sending name: ", client.name)
        self.main_socket.send_bytes(client.name.encode())
        time.sleep(1)

        self.video_socket.sendto(pickle.dumps(Message(client.name, 'add', 'video')), VIDEO_ADDR)
        self.audio_socket.sendto(pickle.dumps(Message(client.name, 'add', 'audio')), AUDIO_ADDR)
    
    def start_conn_threads(self):
        self.main_thread = Worker(self.handle_main, self.main_socket)
        self.threadpool.start(self.main_thread)

        self.video_thread = Worker(self.handle_media, self.video_socket, 'video')
        self.threadpool.start(self.video_thread)

        self.audio_thread = Worker(self.handle_media, self.audio_socket, 'audio')
        self.threadpool.start(self.audio_thread)

    def start_broadcast_threads(self):
        self.msg_multicast_thread = Worker(self.multicast_msg, self.main_socket, 'msg')
        self.threadpool.start(self.msg_multicast_thread)

        self.video_broadcast_thread = Worker(self.broadcast_media, self.video_socket, 'video')
        self.threadpool.start(self.video_broadcast_thread)

        self.audio_broadcast_thread = Worker(self.broadcast_media, self.audio_socket, 'audio')
        self.threadpool.start(self.audio_broadcast_thread)
    
    def disconnect_all(self):
        msg = Message(client.name, DISCONNECT_MSG)
        self.main_socket.send_bytes(pickle.dumps(msg))
        self.main_socket.disconnect()
        
    def handle_main(self, conn):
        global all_clients, active_clients
        while self.connected:
            msg_bytes = conn.recv_bytes()
            if not msg_bytes:
                self.connected = False
                break
            msg = pickle.loads(msg_bytes) 
            # if type(msg) != Message:
            #     print("Clients: ", msg)conn
            if msg.request == DISCONNECT_MSG:
                self.connected = False
                break
            elif msg.request == 'add':
                client_name = msg.from_name
                all_clients[client_name] = Client(client_name, "addr")
                active_clients.add(client_name)
                self.add_client_signal.emit(all_clients[client_name])
                print("Added client: ", client_name)
            elif msg.request == 'rm':
                client_name = msg.from_name
                self.remove_client_signal.emit(client_name)
                all_clients.pop(client_name)
            elif msg.request == 'post':
                if msg.data_type == 'file':
                    file_name = msg.file_name
                    with open(file_name, 'wb') as file:
                        file.write(msg.data)
                self.add_msg_signal.emit(msg)
            else:
                print("Invalid request: ", msg.request)

    def handle_media(self, conn, media):
        global all_clients
        while self.connected:
            msg_bytes, _ = conn.recvfrom(MEDIA_SIZE[media])
            if not msg_bytes:
                self.connected = False
                break
            msg = pickle.loads(msg_bytes)
            # if type(msg) != Message:
            #     msg = pickle.loads(msg)
            #     print(msg.from_name, msg.data_type)
            if msg.request == DISCONNECT_MSG:
                self.connected = False
                break
            if msg.request == 'post':
                client_name = msg.from_name
                if client_name not in all_clients:
                    continue
                if msg.data_type == 'video':
                    all_clients[client_name].video_frame = msg.data
                elif msg.data_type == 'audio':
                    all_clients[client_name].audio_stream = msg.data
    
    def multicast_msg(self, conn, msg):
        global SEND_MSG
        while self.connected:
            proceed = get_send_msg()
            if not proceed:
                continue
            print("Sending message...")
            current_msg = get_current_msg()
            current_msg.from_name = client.name
            if current_msg.data_type == 'file':
                file_path = current_msg.data
                current_msg.file_name = current_msg.data.split('/')[-1]
                with open(file_path, 'rb') as file:
                    current_msg.data = file.read()
            msg = pickle.dumps(current_msg)
            self.add_msg_signal.emit(current_msg)
            conn.send_bytes(msg)
    
    def broadcast_media(self, conn, media):
        while self.connected:
            if media == 'video':
                addr = VIDEO_ADDR
                data = client.get_video()
            elif media == 'audio':
                addr = AUDIO_ADDR
                data = client.get_audio()
            else:
                print("Invalid media type")
                break
            msg = Message(client.name, 'post', media, data)
            conn.sendto(pickle.dumps(msg), addr)

client = Client('You', None)
all_clients = {}
def main():
    app = QApplication(sys.argv)

    server = ServerConnection()
    window = MainWindow(client, server)
    window.show()

    app.exec()
    server.disconnect_all()
    os._exit(0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n> Disconnecting...")
        exit(0)