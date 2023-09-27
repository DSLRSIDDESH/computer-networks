import pygame
import socket
import pickle
import random

# Initialize Pygame
pygame.init()

# Connect to the server
# IP = socket.gethostbyname(socket.gethostname())              # ip address
IP = ''
PORT = 8513
ADDR = (IP, PORT)                                           # address
SIZE = 4096

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 30
COIN_SIZE = 15
BACKGROUND = (0, 0, 0)
COIN_COLOR = (137, 207, 240)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Collector Game")

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


def main():
    # Connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect(ADDR)
    print(f"> Client connected to server at {IP}:{PORT}")

# Game loop
    connected = True
    while connected:
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
            connected = False
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