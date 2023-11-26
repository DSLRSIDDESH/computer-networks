import cv2
import pyaudio
import time
from communication import *
from PyQt6.QtCore import Qt, QSize, QThread, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QDockWidget, \
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget, \
    QCheckBox, QFileDialog, QListWidget, QListWidgetItem, QMessageBox, \
    QDialog

FRAME_WIDTH = 1080
FRAME_HEIGHT = 810
pa = pyaudio.PyAudio()

ENABLE_VIDEO = True
ENABLE_AUDIO = True

NO_CAM = cv2.imread('images/cam.jpeg')
cam_h, cam_w = NO_CAM.shape[:2]
cam_w, cam_h = (cam_w - FRAME_WIDTH//3)//2, (cam_h - FRAME_HEIGHT//3)//2
NO_CAM = NO_CAM[cam_h:cam_h+FRAME_HEIGHT//3, cam_w:cam_w+FRAME_WIDTH//3]
NO_MIC = cv2.flip(cv2.imread('images/mic.jpeg'), 1)

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.name = None
    
    def init_ui(self):
        self.setWindowTitle("Login")

        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.h_layout = QHBoxLayout()

        self.name_label = QLabel("Name: ")
        self.name_textbox = QLineEdit()

        self.h_layout.addWidget(self.name_label)
        self.h_layout.addWidget(self.name_textbox)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_clicked)

        self.layout.addLayout(self.h_layout)
        self.layout.addWidget(self.login_button)
    
    def login_clicked(self):
        print(self.name_textbox.text())
        self.name = self.name_textbox.text()
        if self.name != '' and not self.name.isspace():
            self.accept()

    def close(self):
        self.reject()

class Audio:
    def __init__(self):
        self.audio_stream = pa.open(rate=48000, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=2048)

    def get_stream(self):
        if not ENABLE_AUDIO:
            return None
        self.audio = self.audio_stream.read(2048, exception_on_overflow=False)
        return self.audio

class PlayAudio(QThread):
    def __init__(self, client):
        super().__init__()
        self.connected = True
        self.client = client
        self.audio_stream = pa.open(rate=48000, channels=1, format=pyaudio.paInt16, output=True, frames_per_buffer=2048)

    def run(self):
        if self.client.audio is not None:
            return
        while self.connected:
            audio = self.client.get_audio()
            if audio is not None:
                self.audio_stream.write(audio)  

class Video:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
    
    def get_frame(self):
        global ENABLE_VIDEO, ENABLE_AUDIO
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH//3)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT//3)
        if not ENABLE_VIDEO:
            frame = cv2.resize(NO_CAM, (FRAME_WIDTH//3, FRAME_HEIGHT//3), interpolation=cv2.INTER_AREA)
        else:
            success, frame = self.capture.read()
            if success:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    # convert frame to RGB
                frame = cv2.resize(frame, (FRAME_WIDTH//3, FRAME_HEIGHT//3), interpolation=cv2.INTER_AREA)
                frame = cv2.flip(frame, 1)
        if not ENABLE_AUDIO:
                nomic_h, nomic_w, _ = NO_MIC.shape
                x, y = FRAME_WIDTH//3 -  2 * nomic_w, FRAME_HEIGHT//3 - 2 * nomic_h
                frame[y:y+nomic_h, x:x+nomic_w] = NO_MIC.copy()
        return frame

class SelectClients(QWidget):
    def __init__(self, client_list, msg_type, msg_data):
        super().__init__()
        self.client_list = client_list
        self.clients_checkbox = {}
        self.checked_clients = set()
        self.msg_type = msg_type
        self.msg_data = msg_data
        self.init_ui()
    
    def init_ui(self):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.setWindowTitle("Select Peers")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.h_layout = QHBoxLayout()
        self.layout.addLayout(self.h_layout)
        
        self.select_text = QLabel("Select Peers")
        self.select_all = QCheckBox("Select All")
        self.select_all.stateChanged.connect(self.select_all_clicked)

        self.h_layout.addWidget(self.select_text)
        self.h_layout.addWidget(self.select_all)

        for client in self.client_list:
            self.clients_checkbox[client] = QCheckBox(client)
            self.layout.addWidget(self.clients_checkbox[client])
        
        self.send_button = QPushButton("Send")
        self.layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.send_to_clients)
        
    def select_all_clicked(self):                    # to select all clients
        if self.select_all.isChecked():
            for client in self.client_list:
                self.clients_checkbox[client].setChecked(True)
        else:
            for client in self.client_list:
                self.clients_checkbox[client].setChecked(False)
    
    def send_to_clients(self):                      # to send message/file to selected clients
        atleast_one_checked = False
        for client in self.client_list:
            if self.clients_checkbox[client].isChecked():
                atleast_one_checked = True
                self.checked_clients.add(client)
        if atleast_one_checked:
            self.send_msg()
            self.close()
    
    def send_msg(self):
        print("sending message")
        msg = Message(None, 'post', self.msg_type, self.msg_data, self.checked_clients)
        set_current_msg(msg, True)

class SendPopup(QWidget):
    def __init__(self, **kwargs):
        super().__init__()
        self.init_ui(**kwargs)
    
    def init_ui(self, **kwargs):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.msg_type = kwargs.get('type', 'message')
        self.msg_path = kwargs.get('path', '')

        self.setWindowTitle(f"{self.msg_type} Sharing")

        self.button_text = self.msg_type + ' ' + self.msg_path
        self.label = QLabel(f"Enter {self.button_text}:")
        self.textbox = QLineEdit()

        if kwargs.get('file', False):                               # If file sharing
            self.textbox.setReadOnly(True)
            self.select_file_button = QPushButton("Select File")
            self.layout.addWidget(self.select_file_button)
            self.select_file_button.clicked.connect(self.select_file)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.label)
        horizontal_layout.addWidget(self.textbox)

        self.send_button = QPushButton(f"Send {self.msg_type}")

        self.layout.addLayout(horizontal_layout)
        self.layout.addWidget(self.send_button)

        self.send_button.clicked.connect(self.open_clients_list)

    def select_file(self):
        self.file_path = QFileDialog.getOpenFileName(self, 'Select File')[0]
        self.textbox.setText(self.file_path)
    
    def open_clients_list(self):
        msg = self.textbox.text()
        if msg != '' and not msg.isspace():
            self.close()
            self.cleints_list_widget = SelectClients(get_active_clients(), msg_type=self.msg_type, msg_data=msg)
            self.cleints_list_widget.show()

class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.chat_box = QTextEdit()                     # Chat box
        self.chat_box.setReadOnly(True)

        self.msg_button = QPushButton("Send Message")   # Send-message button
        self.file_button = QPushButton("Send File")     # Send-file button

        self.layout.addWidget(self.chat_box)
        self.layout.addWidget(self.msg_button)
        self.layout.addWidget(self.file_button)

        self.msg_button.clicked.connect(self.send_msg_clicked)
        self.file_button.clicked.connect(self.send_file_clicked)

    def send_msg_clicked(self):
        self.popup = SendPopup(type='message', file=False)
        self.popup.show()

    def send_file_clicked(self):
        self.popup = SendPopup(type='file', path='path', file=True)
        self.popup.show()

class VideoWidget(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video)
        self.timer.start(30)
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.name_label = QLabel(self.client.name)          # to display client name
        self.video_frame = QLabel()                         # to display client video

        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.video_frame)
        self.layout.addWidget(self.name_label)
    
    def update_video(self):
        frame = self.client.get_video()
        if frame is not None:
            height, width, channel = frame.shape
            bytes_per_line = channel * width
            image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            self.video_frame.setPixmap(QPixmap.fromImage(image))

class VideoListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.all_items = {}
        self.init_ui()

    def init_ui(self):
        # pass
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
    
    def add_video(self, client, frame=None):
        video_widget = VideoWidget(client)

        item = QListWidgetItem()
        item.setFlags(item.flags() & ~(Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled))
        self.addItem(item)
        item.setSizeHint(QSize(FRAME_WIDTH//3, FRAME_HEIGHT//3))
        self.setItemWidget(item, video_widget)
        self.all_items[client.name] = item
    
    def remove_video(self, name):
        self.removeItemWidget(self.all_items[name])
        self.all_items.pop(name)

class MainWindow(QMainWindow):
    def __init__(self, client, server_conn):
        super().__init__()
        self.client = client
        self.server_conn = server_conn
        self.audio_threads = {}

        self.server_conn.add_client_signal.connect(self.add_client)
        self.server_conn.remove_client_signal.connect(self.remove_client)
        self.server_conn.add_msg_signal.connect(self.add_msg)
        self.server_conn.start()

        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Video Conference")
        self.setGeometry(0, 0, 1920, 1000)

        login_window = LoginWindow()
        if not login_window.exec():
            print("Login cancelled")
            self.close()
            exit(0)
        else:
            self.client.name = login_window.name

        self.video_list = VideoListWidget()
        self.setCentralWidget(self.video_list)
        
        self.chatbar = QDockWidget("Chat", self)
        self.chat_widget = ChatWidget()
        self.chatbar.setWidget(self.chat_widget)
        self.chatbar.setFixedWidth(250)

        self.add_toggle_buttons()   # add video & audio on/off, end-call buttons

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.chatbar)
        self.chatbar.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    
    def add_toggle_buttons(self):
        self.enable_video = QCheckBox("Video")
        self.enable_video.setChecked(True)
        self.enable_video.stateChanged.connect(lambda: self.toggle_media('video'))

        self.enable_audio = QCheckBox("Audio")
        self.enable_audio.setChecked(True)
        self.enable_audio.stateChanged.connect(lambda: self.toggle_media('audio'))

        self.end_call = QPushButton("Leave Call")
        # change its color to red and round edges
        self.end_call.setStyleSheet("background-color: #F15A59;")
        self.end_call.clicked.connect(self.close)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.enable_video)
        h_layout.addWidget(self.enable_audio)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.end_call)

        self.chat_widget.layout.addLayout(v_layout)
    
    def toggle_media(self, media):
        global ENABLE_VIDEO, ENABLE_AUDIO
        if media == 'video':
            if self.enable_video.isChecked():
                ENABLE_VIDEO = True
            else:
                ENABLE_VIDEO = False
        elif media == 'audio':
            if self.enable_audio.isChecked():
                ENABLE_AUDIO = True
            else:
                ENABLE_AUDIO = False

    def add_client(self, client):
        self.video_list.add_video(client)
        self.audio_threads[client.name] = PlayAudio(client)
        self.audio_threads[client.name].start()
        msg = Message(client.name, 'join', 'message', 'joined the conference', None)
        self.add_msg(msg)
    
    def remove_client(self, client_name):
        self.video_list.remove_video(client_name)
        self.audio_threads[client_name].connected = False
        self.audio_threads[client_name].wait()
        self.audio_threads.pop(client_name)
        self.chat_widget.chat_box.append(f"{client_name} left the conference")

    def add_msg(self, msg):
        if self.client.name != msg.from_name:
            if msg.data_type == 'message':
                chat = f"{msg.from_name} : {msg.data}"
            elif msg.data_type == 'file' and msg.file_name is not None:
                chat = f"{msg.from_name } : {msg.file_name}"
        else:
            if msg.data_type == 'message':
                chat = f"You : {msg.data}"
            elif msg.data_type == 'file' and msg.file_name is not None:
                chat = f"You : {msg.file_name}"
            if msg.request != 'join':
                chat += '\n    sent to [ '
                for name in msg.to_names:
                    chat += name + ', '
                chat = chat[:-2] + ' ]'
        self.chat_widget.chat_box.append(chat)