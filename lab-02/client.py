import socket

# socket object creation
s = socket.socket()
port = 53530

# connecting to the server
s.connect(('192.168.137.177', port))
# receiving message from server
print(s.recv(1024).decode())
s.close()