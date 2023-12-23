import socket
import struct
import pickle

active_clients = set()
SEND_MSG = False
CURRENT_MSG = None

class Message:
    def __init__(self, from_name: str, request: str, data_type: str = None, data: any = None, to_names: set[str] = set()):
        self.from_name = from_name
        self.request = request
        self.data_type = data_type
        self.data = data
        self.to_names = to_names
        self.file_name = None


def send_bytes(self, msg):
    msg = struct.pack('>I', len(msg)) + msg
    try:
        self.sendall(msg)
    except (OSError, ConnectionResetError):
        print("Connection lost")

def recv_bytes(self):
    raw_msglen = self.recvall(4)
    if not raw_msglen:
        return b''
    msglen = struct.unpack('>I', raw_msglen)[0]
    return self.recvall(msglen)

def recvall(self, n):
    data = bytearray()
    while len(data) < n:
        try:
            packet = self.recv(n - len(data))
            if not packet:
                return b''
            data.extend(packet)
        except (OSError, ConnectionResetError):
            print("Connection lost")
            return b''
    return data

def disconnect(self):
    msg = Message('SERVER', 'disconnect')
    self.send_bytes(pickle.dumps(msg))
    self.close()

def set_current_msg(msg: Message, send: bool = False):
    global CURRENT_MSG, SEND_MSG
    CURRENT_MSG = msg
    SEND_MSG = True

def get_send_msg():
    global SEND_MSG
    curr = SEND_MSG
    SEND_MSG = False
    return curr

def get_current_msg():
    global CURRENT_MSG
    return CURRENT_MSG

def get_active_clients():
    return active_clients

socket.socket.send_bytes = send_bytes
socket.socket.recv_bytes = recv_bytes
socket.socket.recvall = recvall
socket.socket.disconnect = disconnect