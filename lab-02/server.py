#socket programming using python
import socket
#socket object creation
s = socket.socket()
print("Socket successfully created")

port = 8005
#binding IP and port using bind function
s.bind(('', port))
print("socket is binded to %s" %(port))
#listening to the socket
s.listen(5)
print("socket is listening")

while True:
    #accepting the connection sent by client
    conn, address = s.accept()
    print("Got connection from", address)
    #sending message to client after connection is established
    conn.send("Thank you for connecting...".encode())
    conn.close()