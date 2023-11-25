import cv2
import pyaudio
from PyQt6.QtCore import Qt, QSize, QThread, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QDockWidget, \
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget, \
    QCheckBox, QFileDialog, QListWidget, QListWidgetItem, QMessageBox

active_clients = ['client-1', 'client-2', 'client-3', 'client-4', 'client-5']
name_list = ['sid']
FRAME_WIDTH = 480
FRAME_HEIGHT = 360

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 100)

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
        self.name = self.name_textbox.text()
        if self.name not in name_list:
            name_list.append(self.name)
            self.close()
        else:
            self.message_box = QMessageBox()
            self.message_box.setWindowTitle("Error")
            self.message_box.setText("Name already exists")
            self.message_box.exec()

class Video:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    def get_frame(self):
        success, frame = self.capture.read()
        if success:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    # convert frame to RGB
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT), interpolation=cv2.INTER_AREA)
            return cv2.flip(frame, 1)

class SelectClients(QWidget):
    def __init__(self):
        super().__init__()
        self.clients = {}
        self.checked_clients = []
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

        for client in active_clients:
            self.clients[client] = QCheckBox(client)
            self.layout.addWidget(self.clients[client])
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_to_clients)
        self.layout.addWidget(self.send_button)
        
    def select_all_clicked(self):                    # to select all clients
        if self.select_all.isChecked():
            for client in active_clients:
                self.clients[client].setChecked(True)
        else:
            for client in active_clients:
                self.clients[client].setChecked(False)
    
    def send_to_clients(self):                      # to send message/file to selected clients
        atleast_one_checked = False
        for client in active_clients:
            if self.clients[client].isChecked():
                atleast_one_checked = True
                self.checked_clients.append(client)
        if atleast_one_checked:
            print(self.checked_clients)
            self.close()

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

    def select_file(self):
        self.file_path = QFileDialog.getOpenFileName(self, 'Select File')[0]
        self.textbox.setText(self.file_path)

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

        self.popup.send_button.clicked.connect(self.open_clients_list)

    def send_file_clicked(self):
        self.popup = SendPopup(type='file', path='path', file=True)
        self.popup.show()

        self.popup.send_button.clicked.connect(self.open_clients_list)
    
    def open_clients_list(self):
        self.popup.close()
        self.cleints_list = SelectClients()
        self.cleints_list.show()

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

        self.name_label = QLabel(self.client.name)           # to display client name
        self.video_frame = QLabel()                     # to display client video

        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.video_frame)
    
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
        self.setFlow(QListWidget.Flow.LeftToRight)           # to display icons from left to right
        self.setWrapping(True)                          # to wrap icons
        self.setResizeMode(QListWidget.ResizeMode.Adjust)          # to adjust icon size
        self.setMovement(QListWidget.Movement.Static)            # to disable drag and drop
    
    def add_video(self, client, frame=None):
        video_widget = VideoWidget(client)

        item = QListWidgetItem()
        item.setFlags(item.flags() & ~(Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled))
        self.addItem(item)
        item.setSizeHint(QSize(FRAME_WIDTH, FRAME_HEIGHT))
        self.setItemWidget(item, video_widget)
        self.all_items[client.name] = item


class MainWindow(QMainWindow):
    def __init__(self, client, server_conn):
        super().__init__()
        self.client = client
        self.server_conn = server_conn

        self.server_conn.add_client_signal.connect(self.add_client)
        self.server_conn.remove_client_signal.connect(self.remove_client)
        self.server_conn.start()

        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Video Conference")
        self.setGeometry(0, 0, 1920, 1000)

        self.video_list = VideoListWidget()
        self.setCentralWidget(self.video_list)
        
        self.chatbar = QDockWidget("Chat", self)
        self.chat_widget = ChatWidget()
        self.chatbar.setWidget(self.chat_widget)
        self.chatbar.setFixedWidth(250)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.chatbar)
        self.chatbar.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        # for client in active_clients:
        #     self.add_client(client)
    
    def add_client(self, client):
        self.video_list.add_video(client)
    
    def remove_client(self, client):
        pass

    def add_msg(self, msg):
        self.chat_widget.chat_box.append(f"{msg.from_name}: {msg.data}")