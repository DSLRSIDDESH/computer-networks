import pygame
import socket
import pickle
import time

# Initialize Pygame
pygame.init()
# Connect to the server
HOST = '127.0.0.1'
PORT = 12012
# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 30
COIN_SIZE = 15
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Collector Game")

# Function to send player input to the server
def send_player_input():
    keys = pygame.key.get_pressed()
    input_data = {
        'left': keys[pygame.K_LEFT],
        'right': keys[pygame.K_RIGHT],
        'up': keys[pygame.K_UP],
        'down': keys[pygame.K_DOWN],
    }
    client_socket.send(pickle.dumps(input_data))

# Function to receive game state from the server
def receive_game_state():
    try:
        data = client_socket.recv(4096)
        game_state = pickle.loads(data)
        return game_state
    except Exception as e:
        print(f"Error receiving game state: {e}")
        return None

def render_players_scores(players):
    # pass
    font = pygame.font.Font(None, 16)
    y_offset = 10
    for player_id, (player_x, player_y) in players.items():
        score = game_state['player_scores'].get(player_id, 0)
        text = font.render(f"Player {player_id}: {score}", True, YELLOW)
        screen.blit(text, (10, y_offset))
        y_offset += 40

# Connect to the server
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect((HOST, PORT))
            return client_socket
        except Exception as e:
            print("Server is not available. Retrying in 5 seconds...")
            time.sleep(5)

client_socket = connect_to_server()

# Game loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    send_player_input()  # Send player input to the server

    game_state = receive_game_state()

    if game_state is not None:
        players = game_state['players']
        coins = game_state['coins']

        # Clear the screen
        screen.fill(BLACK)

        # Draw players
        for player_id, (player_x, player_y) in players.items():
            pygame.draw.rect(screen, YELLOW, (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))

        # Draw coins
        for coin_x, coin_y in coins:
            pygame.draw.ellipse(screen, YELLOW, (coin_x, coin_y, COIN_SIZE, COIN_SIZE))

        # Display player scores
        render_players_scores(players)

        # Update the display
        pygame.display.flip()

# Quit Pygame
pygame.quit()