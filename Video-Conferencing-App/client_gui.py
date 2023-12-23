import cv2
import pyaudio
import time
from communication import *
from PyQt6.QtCore import Qt, QSize, QThread, QTimer
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QDockWidget, \
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget, \
    QCheckBox, QFileDialog, QListWidget, QListWidgetItem, QMessageBox, \
    QDialog

frame_size = {
    '240p': [352, 240],
    '360p': [480, 360],
    '480p': [640, 480],
    '720p': [1080, 720],
    '900p': [1600, 900],
    '1080p': [1920, 1080]
}

FRAME_WIDTH = 1080
FRAME_HEIGHT = 810
pa = pyaudio.PyAudio()

ENABLE_VIDEO = True
ENABLE_AUDIO = True
ENCODE_PARAM = [int(cv2.IMWRITE_JPEG_QUALITY), 90]


NO_CAM = cv2.imread('images/cam.jpeg')
cam_h, cam_w = NO_CAM.shape[:2]
cam_w, cam_h = (cam_w - FRAME_WIDTH//3)//2, (cam_h - FRAME_HEIGHT//3)//2
NO_CAM = NO_CAM[cam_h:cam_h+FRAME_HEIGHT//3, cam_w:cam_w+FRAME_WIDTH//3]
NO_MIC = cv2.imread('images/microphone-slash-solid.jpeg')

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
        self.audio_stream = pa.open(rate=44100, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=2048)

    def get_stream(self):
        global ENABLE_AUDIO
        if not ENABLE_AUDIO:
            self.audio = None
            return None
        if ENABLE_AUDIO:
            self.audio = self.audio_stream.read(2048)
            return self.audio

class PlayAudio(QThread):
    def __init__(self, client):
        super().__init__()
        self.connected = True
        self.client = client
        self.audio_stream = pa.open(rate=44100, channels=1, format=pyaudio.paInt16, output=True, frames_per_buffer=2048)

    def run(self):
        if self.client.audio is not None:
            return
        while self.connected:
            audio = self.client.get_audio()
            if audio is not None:
                self.audio_stream.write(audio)  

class Video:
    def __init__(self):
        self.capture = cv2.VideoCapture(2)
        if not self.capture.isOpened():
            self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 352)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
    def get_frame(self):
        global ENABLE_VIDEO, ENABLE_AUDIO
        if not ENABLE_VIDEO:
            frame = cv2.resize(NO_CAM, (352, 240), interpolation=cv2.INTER_AREA)
        else:
            success, frame = self.capture.read()
            if success:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    # convert frame to RGB
                frame = cv2.resize(frame, (352, 240), interpolation=cv2.INTER_AREA)
                # frame = cv2.flip(frame, 1)
            else:
                return None
        if not ENABLE_AUDIO:
                nomic_h, nomic_w, _ = NO_MIC.shape
                x, y = 352 -  2 * nomic_w, 240 - 2 * nomic_h
                frame[y:y+nomic_h, x:x+nomic_w] = NO_MIC.copy()

        _, frame = cv2.imencode('.jpg', frame, ENCODE_PARAM)
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
        self.file_path = QFileDialog.getOpenFileName(self, 'Select File', options= QFileDialog.Option.DontUseNativeDialog)[0]
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
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT), interpolation=cv2.INTER_AREA)
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
        item.setSizeHint(QSize(FRAME_WIDTH, FRAME_HEIGHT))
        self.setItemWidget(item, video_widget)
        self.all_items[client.name] = item
    
    def remove_video(self, name):
        self.takeItem(self.row(self.all_items[name]))
        self.all_items.pop(name)
    
    def update_size(self):
        global FRAME_WIDTH, FRAME_HEIGHT
        n = len(self.all_items)
        if n <= 1:
            res = '900p'
        elif n <= 4:
            res = '480p'
        elif n <= 6:
            res = '360p'
        else:
            res = '240p'
        FRAME_WIDTH, FRAME_HEIGHT = frame_size[res]
        for item in self.all_items.values():
            item.setSizeHint(QSize(FRAME_WIDTH, FRAME_HEIGHT))


class ImageCheckBox(QCheckBox):
    def __init__(self, checked_image_path, unchecked_image_path, size, parent=None):
        super().__init__(parent)
        self.checked_image_path = checked_image_path
        self.unchecked_image_path = unchecked_image_path
        self.size = size
        self.update_checkbox_image()

        self.setStyleSheet("QCheckBox::indicator { width:0px; height:0px; }")
        self.stateChanged.connect(self.update_checkbox_image)

    def update_checkbox_image(self):
        pixmap = QPixmap(self.checked_image_path) if self.isChecked() else QPixmap(self.unchecked_image_path)

        pixmap = pixmap.scaledToWidth(self.size, Qt.TransformationMode.SmoothTransformation)

        self.setIcon(QIcon(pixmap))
        self.setIconSize(pixmap.size())

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

        layout = QHBoxLayout(self.video_list)
        
        self.enable_cam = ImageCheckBox('images/video-solid.png', 'images/video-slash-solid.png',40)
        self.enable_cam.setChecked(True)
        self.enable_cam.stateChanged.connect(lambda: self.toggle_media('video'))

        self.enable_mic = ImageCheckBox('images/microphone-solid.png', 'images/microphone-slash-solid.png',40)
        self.enable_mic.setChecked(True)
        self.enable_mic.stateChanged.connect(lambda: self.toggle_media('audio'))

        self.open_chat = ImageCheckBox('images/comment-solid.png', 'images/comment-slash-solid.png',40)
        self.open_chat.setChecked(False)
        self.open_chat.stateChanged.connect(self.toggle_chat)

        self.end_call = ImageCheckBox('images/hangup.png', 'images/hangup.png', 60)
        self.end_call.setChecked(False)
        # self.end_call.setStyleSheet("background-color: #F15A59;")
        self.end_call.stateChanged.connect(self.close)

        layout.addWidget(self.enable_cam)
        layout.addWidget(self.enable_mic)
        layout.addWidget(self.open_chat)
        layout.addWidget(self.end_call)

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        
        
        self.chatbar = QDockWidget("Chat", self)
        self.chat_widget = ChatWidget()
        self.chatbar.setWidget(self.chat_widget)
        self.chatbar.setFixedWidth(250)
        self.chatbar.setHidden(True)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.chatbar)
        self.chatbar.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

    def toggle_chat(self):
        if self.open_chat.isChecked():
            self.chatbar.setHidden(False)
        else:
            self.chatbar.setHidden(True)
    
    def toggle_media(self, media):
        global ENABLE_VIDEO, ENABLE_AUDIO
        if media == 'video':
            if self.enable_cam.isChecked():
                ENABLE_VIDEO = True
            else:
                ENABLE_VIDEO = False
        elif media == 'audio':
            if self.enable_mic.isChecked():
                ENABLE_AUDIO = True
            else:
                ENABLE_AUDIO = False

    def add_client(self, client):
        self.video_list.add_video(client)
        self.audio_threads[client.name] = PlayAudio(client)
        self.audio_threads[client.name].start()
        msg = Message(client.name, 'join', 'message', 'joined the conference', None)
        self.add_msg(msg)
        self.video_list.update_size()
    
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