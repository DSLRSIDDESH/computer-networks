import socket
import threading
import random
import pickle
import queue

# Server configuration
# IP = socket.gethostbyname(socket.gethostname())
IP = ''
PORT = 8513
ADDR = (IP, PORT)
SIZE = 4096
clients = {}

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SPEED = 1
PLAYER_SIZE = 30
COIN_SIZE = 15
COIN_COUNT = 10
MAX_PLAYERS = 4
WINNING_SCORE = 5

# Create the game state
game_state = {
    'players': {},          # Store player positions as {player_id: (x, y)}
    'player_scores': {},    # Store player scores as {player_id: score}
    'coins': [(random.randint(0, WIDTH - COIN_SIZE), random.randint(0, HEIGHT - COIN_SIZE)) for _ in range(COIN_COUNT)],
    'color': {}             # Store player color as {'player_id': (R, G, B)}
}

# Function to update player position based on input
def update_player_position(player_id, input_data):
    player_x, player_y = game_state['players'][player_id]
    if input_data['left']:
        player_x -= PLAYER_SPEED
    if input_data['right']:
        player_x += PLAYER_SPEED
    if input_data['up']:
        player_y -= PLAYER_SPEED
    if input_data['down']:
        player_y += PLAYER_SPEED

    # Ensure the player stays within the game bounds
    player_x = max(0, min(player_x, WIDTH - PLAYER_SIZE))
    player_y = max(0, min(player_y, HEIGHT - PLAYER_SIZE))

    game_state['players'][player_id] = (player_x, player_y)

# Function to handle a client
def handle_client(conn, player_id):
    while True:
        data = conn.recv(SIZE)
        if not data:
            break
        # Update the game state for the player based on input
        input_data = pickle.loads(data)
        update_player_position(player_id, input_data)

        # Check for collisions with coins
        coins_to_remove = []
        for i, (coin_x, coin_y) in enumerate(game_state['coins']):
            player_x, player_y = game_state['players'][player_id]
            if player_x < coin_x + COIN_SIZE and player_x + PLAYER_SIZE > coin_x and player_y < coin_y + COIN_SIZE and player_y + PLAYER_SIZE > coin_y:
                coins_to_remove.append(i)
                game_state['player_scores'][player_id] = game_state['player_scores'].get(player_id, 0) + 1

        # Remove the coins that were collected and add new one
        for i in coins_to_remove:
            game_state['coins'].pop(i)
            new_coin_x = random.randint(0, WIDTH - COIN_SIZE)
            new_coin_y = random.randint(0, HEIGHT - COIN_SIZE)
            game_state['coins'].append((new_coin_x, new_coin_y))

        # Send the updated game state to all players
        game_update = pickle.dumps(game_state)
        for connection in clients.values():
            connection.send(game_update)
        
        # Check if any player has won
        if len(game_state['players']) > 1:
            if max(game_state['player_scores'].values()) >= WINNING_SCORE:
                for player_id, score in game_state['player_scores'].items():
                    if score >= WINNING_SCORE:
                        break
                for connection in clients.values():
                    connection.send(pickle.dumps(player_id))

    # Remove the player from the game state and close the socket
    del game_state['players'][player_id]
    clients.pop(player_id)
    conn.close()

def initialize_player_scores():
        for player_id in game_state['players']:
            game_state['player_scores'][player_id] = 0

def main():
    print("> Server is starting...")
    
    # Create the server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    server.listen()
    print(f"> Server is listening on {IP}:{PORT}")
    print(f"> [Active Connections] {threading.active_count() - 1}")

    # Accept and handle client connections
    player_id_counter = 0
    # initialize_player_scores()  # Initialize player scores

    while True:
        conn, addr = server.accept()

        player_id = player_id_counter
        clients[player_id] = conn
        player_id_counter += 1

        # Initialize player's position
        player_x = random.randint(0, WIDTH - PLAYER_SIZE)
        player_y = random.randint(0, HEIGHT - PLAYER_SIZE)
        game_state['players'][player_id] = (player_x, player_y)

        
        display_color = (random.randint(10, 255) for _ in range(3))
        game_state['color'][player_id] = tuple(display_color)
        game_state['player_scores'][player_id] = game_state['player_scores'].get(player_id, 0)

        client_thread = threading.Thread(target=handle_client, args=(conn, player_id))
        client_thread.start()

        print(f"> [Active Connections] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()