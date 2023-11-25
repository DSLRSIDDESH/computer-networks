import socket
import pickle
import sys
from PyQt6.QtCore import QThreadPool, QThread, pyqtSignal, QRunnable, pyqtSlot
from PyQt6.QtWidgets import QApplication
from client_gui import MainWindow, Video, LoginWindow
from communication import *

# Server IP and port
SERVER_IP = ''
MAIN_PORT = 2000
VIDEO_PORT = MAIN_PORT + 1
AUDIO_PORT = MAIN_PORT + 2

DISCONNECT_MSG = 'DISCONNECT'

# clients
class Client:
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.camera = None
        self.microphone = None

        self.video_frame = None
        self.audio_data = None

        if self.addr is None:
            self.camera = Video()
            # self.microphone = Microphone()

    def get_video(self):
        if self.camera is not None:
            return self.camera.get_frame()

        return self.video_frame
    
    def get_audio(self):
        # if self.microphone is not None:
        #     return self.microphone.get_data()

        return self.audio_data

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

    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()

        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connected = False

    def run(self):
        self.init_connection()
        self.start_conn_threads()
        self.start_broadcast_threads()

        self.add_client_signal.emit(client)

        while self.connected:
            pass
    
    def init_connection(self):
        self.main_socket.connect((SERVER_IP, MAIN_PORT))
        self.video_socket.connect((SERVER_IP, VIDEO_PORT))
        self.audio_socket.connect((SERVER_IP, AUDIO_PORT))

        self.connected = True

        self.name = input("> Enter your name: ")
        client.name = self.name

        self.main_socket.send_bytes(self.name.encode())
        self.video_socket.send_bytes(self.name.encode())
        self.audio_socket.send_bytes(self.name.encode())
    
    def start_conn_threads(self):
        self.main_thread = Worker(self.handle_connection, self.main_socket, 'text')
        self.threadpool.start(self.main_thread)

        self.video_thread = Worker(self.handle_connection, self.video_socket, 'video')
        self.threadpool.start(self.video_thread)

        self.audio_thread = Worker(self.handle_connection, self.audio_socket, 'audio')
        self.threadpool.start(self.audio_thread)

    def start_broadcast_threads(self):
        self.video_broadcast_thread = Worker(self.media_broadcast_loop, self.video_socket, 'video')
        self.threadpool.start(self.video_broadcast_thread)

        self.audio_broadcast_thread = Worker(self.media_broadcast_loop, self.audio_socket, 'audio')
        self.threadpool.start(self.audio_broadcast_thread)
    
    def send_msg(self, conn: socket.socket, msg: Message):
        # print("Sending..", msg)
        conn.send_bytes(pickle.dumps(msg))
    
    def media_broadcast_loop(self, conn, media):
        while self.connected:
            if media == 'video':
                data = client.get_video()
            elif media == 'audio':
                data = client.get_audio()
            else:
                print("Invalid media type")
                break
            msg = Message(self.name, 'post', media, data)
            self.send_msg(conn, msg)
    
    def handle_connection(self, conn, media):
        while self.connected:
            msg_bytes = conn.recv_bytes()
            if not msg_bytes:
                self.connected = False
                break
            try:
                msg = pickle.loads(msg_bytes)
            except pickle.UnpicklingError:
                print(f"[{self.name}] [{media}] [ERROR] UnpicklingError")
                continue

            if msg.request == DISCONNECT_MSG:
                self.connected = False
                break
            try:
                self.handle_msg(msg)
            except Exception as e:
                print(f"[{self.name}] [{media}] [ERROR] {e}")
                continue
    
    def handle_msg(self, msg):
        global all_clients
        client_name = msg.from_name
        if msg.request == 'post':
            if client_name not in all_clients:
                print(f"[{self.name}] [ERROR] Invalid client name")
                return
            if msg.data_type == 'video':
                all_clients[client_name].video_frame = msg.data
            elif msg.data_type == 'audio':
                all_clients[client_name].audio_data = msg.data
            else:
                print(f"[{self.name}] [ERROR] Invalid data type")
        elif msg.request == 'add':
            if client_name in all_clients:
                print(f"[{self.name}] [ERROR] Client already exists")
                return
            all_clients[client_name] = Client(client_name)
            self.add_client_signal.emit(all_clients[client_name])

client = Client('You', None)
all_clients = {}
show_main_window = False
def main():
    app = QApplication(sys.argv)

    server_conn = ServerConnection()
    window = MainWindow(client, server_conn)
    window.show()

    app.exec()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n> Disconnecting...")
        exit(0)