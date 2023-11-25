import socket
import struct
import pickle
from dataclasses import dataclass

def send_bytes(self, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    self.sendall(msg)

def recv_bytes(self):
    # Read message length and unpack it into an integer
    raw_msglen = self.recvall(4)
    if not raw_msglen:
        return b''
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return self.recvall(msglen)

def recvall(self, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = self.recv(n - len(data))
        if not packet:
            return b''
        data.extend(packet)
    return data

def disconnect(self):
    msg = Message('SERVER', 'disconnect')
    self.send_bytes(pickle.dumps(msg))
    self.close()

socket.socket.send_bytes = send_bytes
socket.socket.recv_bytes = recv_bytes
socket.socket.recvall = recvall
socket.socket.disconnect = disconnect

@dataclass
class Message:
    def __init__(self, from_name: str, request: str, data_type: str = None, data: any = None):
        self.from_name = from_name
        self.request = request
        self.data_type = data_type
        self.data = data
        self.to_names = set()