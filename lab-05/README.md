Write a socket program to transfer a file from server to client and vice versa.

## File Transfer: SERVER
#### The server performs the following functions:
- Create a TCP socket.
- Bind the IP address and PORT to the server socket.
- Listening for the clients.
- Accept the connection from the client.
- Receive the filename from the client and create a text file.
- Send a response back to the client.
- Receive the text data from the client.
- Write (save) the data into the text file.
- Send a response message back to the client.
- Close the text file.
- Close the connection.

## FIle Transfer: CLIENT
#### The client performs the following functions:
- Create a TCP socket for the client.
- Connect to the server.
- Read the data from the text file.
- Send the filename to the server.
- Receive the response from the server.
- Send the text file data to the server.
- Receive the response from the server.
- Close the file.
- Close the connection.