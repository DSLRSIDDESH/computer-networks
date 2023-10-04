# CS21B2019
# DSLR SIDDESH
# client.py
import socket
import pygame
import pickle

import threading
import tkinter as tk
from tkinter import messagebox
from getmac import get_mac_address

# Initialize Pygame
pygame.init()

# Connect to the server

IP = ''
# IP = '192.168.12.135'
PORT = 8000
ADDR = (IP, PORT)                                           # address
SIZE = 4096
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"
CONNECTED = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Constants
WIDTH, HEIGHT = 600, 400
PLAYER_SIZE = 30
COIN_SIZE = 15
BACKGROUND = (0, 0, 0)
COIN_COLOR = (137, 207, 240)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Collector Game")

def game_entry():
    def register():
        mac = mac_entry.get()
        client.send(f"REGISTER/{mac};".encode(FORMAT))
        msg = recv_msg(client)
        if msg == "OK":
            print(f"Registered MAC Address: {mac}")
            messagebox.showinfo("Registration Successful", f"Registered MAC Address: {mac}")
        else:
            print(f"Registration Failed: {msg}")
            messagebox.showerror("Registration Failed", f"Registration Failed: {msg}")
    
    def login():
        mac = mac_entry.get()
        client.send(f"LOGIN/{mac};".encode(FORMAT))
        msg = recv_msg(client)
        if msg == "OK":
            print(f"Logged in with MAC Address: {mac}")
            start_tk.destroy()
        else:
            print(f"Login Failed: {msg}")
            messagebox.showerror("Login Failed", f"Login Failed: {msg}")
    
    def pay():
        mac = mac_entry.get()
        amount = amount_entry.get()
        client.send(f"PAY/{mac}/{amount};".encode(FORMAT))
        msg = recv_msg(client)
        if msg == "OK":
            print(f"Paid {amount} for MAC Address: {mac}")
            messagebox.showinfo("Payment Successful", f"Paid {amount} for MAC Address: {mac}")
        else:
            print(f"Payment Failed: {msg}")
            messagebox.showerror("Payment Failed", f"Payment Failed: {msg}")
    
    def end_tk():
        start_tk.destroy()
        disconnect_server(client, "client")
        

    start_tk = tk.Tk()
    start_tk.title("Game Registration/Login")

    # Create a label and entry widget for MAC Address
    mac_label = tk.Label(start_tk, text="MAC Address:")
    mac_label.grid(row=0, column=0)
    mac_entry = tk.Entry(start_tk)
    mac_entry.grid(row=0, column=1)

    mac_entry.insert(0, get_mac_address())

    # Create a label and entry widget for payment amount
    amount_label = tk.Label(start_tk, text="Amount (100/min):")
    amount_label.grid(row=2, column=0)
    amount_entry = tk.Entry(start_tk)
    amount_entry.grid(row=2, column=1)

    amount_entry.insert(0, "100")

    # Create Pay button
    pay_button = tk.Button(start_tk, text="Pay", command=pay)

    # Create Register and Login buttons
    register_button = tk.Button(start_tk, text="Register", command=register)
    login_button = tk.Button(start_tk, text="Login", command=login)

    register_button.grid(row=1, column=0, columnspan=2)
    pay_button.grid(row=3, column=0, columnspan=2)
    login_button.grid(row=4, column=0, columnspan=2)

    start_tk.protocol("WM_DELETE_WINDOW", end_tk)

    start_tk.mainloop()

# Function to send player input to the server
def send_player_input(client):
    keys = pygame.key.get_pressed()
    input_data = ({
        'left': keys[pygame.K_LEFT],
        'right': keys[pygame.K_RIGHT],
        'up': keys[pygame.K_UP],
        'down': keys[pygame.K_DOWN],
    })
    client.send(pickle.dumps(input_data))

# Function to receive game state from the server
def receive_game_state(client):
    try:
        data = client.recv(SIZE)
        game_state = pickle.loads(data)
        return game_state
    except Exception as e:
        print(f"Error receiving game state: {e}")
        return None

# Function to render player scores
def render_players_scores(game_state):
    font = pygame.font.Font('freesansbold.ttf', 24)
    y_offset = 10
    for player_id, (player_x, player_y) in game_state['players'].items():
        score = game_state['player_scores'].get(player_id, 0)
        text = font.render(f"Player-{player_id + 1}: {score}", True, game_state['color'][player_id])
        screen.blit(text, (10, y_offset))
        y_offset += 30

def disconnect_server(client: socket.socket, recv_from: str):
    global connected
    connected = False
    client.send(DISCONNECT_MESSAGE.encode(FORMAT))
    if recv_from == "client":
        print(f"[DISCONNECTED] Client disconnected from {IP}:{PORT}")
    elif recv_from == "server":
        print(f"[DISCONNECTED] Server disconnected from Client.")
    client.close()

def recv_msg(client: socket.socket, disconnect_info: str = ""):
    msg = client.recv(SIZE).decode(FORMAT)
    if msg == DISCONNECT_MESSAGE:
        print(disconnect_info)
        disconnect_server(client, "server")
    return msg

def main():
    global connected, client
    # Connect to the server
    client.connect(ADDR)
    print(f"> Client connected to server at {IP}:{PORT}")

    game_entry()

    connected = True
    while connected:    # Game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                connected = False

        send_player_input(client)  # Send player input to the server
        game_state = receive_game_state(client)  # Receive game state from the server
        player_id = 0
        # Check if the game_state type is str
        if type(game_state) == int:
            font = pygame.font.Font('freesansbold.ttf', 32)
            text = font.render(f'Player-{game_state + 1} Won!', True, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = (WIDTH // 2, HEIGHT // 2)
            screen.blit(text, textRect)
            pygame.display.flip()
            pygame.time.delay(50000)
            # connected = False
        else:
            if game_state != None:
                coins = game_state['coins']
                
                screen.fill(BACKGROUND) # Clear the screen

                for player_id, (player_x, player_y) in game_state['players'].items():     # Draw players
                    player_color = game_state['color'][player_id]
                    pygame.draw.rect(screen, player_color, (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))
                for coin_x, coin_y in coins:                                # Draw coins
                    pygame.draw.ellipse(screen, COIN_COLOR, (coin_x, coin_y, COIN_SIZE, COIN_SIZE))

                # Display player scores
                render_players_scores(game_state)

                # Update the display
                pygame.display.flip()

    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    main()