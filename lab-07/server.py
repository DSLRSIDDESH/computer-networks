import socket
import threading
import random
import pickle
import queue

# Server configuration
HOST = '127.0.0.1'
PORT = 12012

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 30
COIN_SIZE = 15
COIN_COUNT = 10
MAX_PLAYERS = 4
WINNING_SCORE = 10

# Create the game state
game_state = {
    'players': {},  # Store player positions as {'player_id': (x, y)}
    'player_scores': {}, # Store player scores as {'player_id': score}
    'coins': [(random.randint(0, WIDTH - COIN_SIZE), random.randint(0, HEIGHT - COIN_SIZE)) for _ in range(COIN_COUNT)],
}

coin_collection_queue = queue.Queue()

# Function to handle a client
def handle_client(client_socket, player_id):
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                continue

            # Update the game state for the player based on input
            input_data = pickle.loads(data)
            update_player_position(player_id, input_data)

            # Check for collisions with coins
            coins_to_remove = []
            for i, (coin_x, coin_y) in enumerate(game_state['coins']):
                player_x, player_y = game_state['players'][player_id]
                if (
                    player_x < coin_x + COIN_SIZE
                    and player_x + PLAYER_SIZE > coin_x
                    and player_y < coin_y + COIN_SIZE
                    and player_y + PLAYER_SIZE > coin_y
                ):
                    coins_to_remove.append(i)
                    game_state['player_scores'][player_id] = game_state['player_scores'].get(player_id, 0) + 1
                    # coin_collection_queue.put(i)

            for i in coins_to_remove:
                game_state['coins'].pop(i)
                new_coin_x = random.randint(0, WIDTH - COIN_SIZE)
                new_coin_y = random.randint(0, HEIGHT - COIN_SIZE)
                game_state['coins'].append((new_coin_x, new_coin_y))

            # Send the updated game state to all players
            game_update = pickle.dumps(game_state)
            for player_socket in client_sockets.values():
                player_socket.send(game_update)
            
            if(len(game_state['players']) > 1):
                if max(game_state['player_scores'].values()) >= WINNING_SCORE:
                    print(f"Player {max(game_state['player_scores'], key=game_state['player_scores'].get)} wins!")
                    return

        except Exception as e:
            print(f"Player {player_id} disconnected: {e}")
            break

    # Remove the player from the game state and close the socket
    del game_state['players'][player_id]
    client_sockets.pop(player_id)
    client_socket.close()

# def handle_coin_collection():
#     while True:
#         coin_index = coin_collection_queue.get()
#         game_state['coins'].pop(coin_index)
#         new_coin_x = random.randint(0, WIDTH - COIN_SIZE)
#         new_coin_y = random.randint(0, HEIGHT - COIN_SIZE)
#         game_state['coins'].append((new_coin_x, new_coin_y))
#         coin_collection_queue.task_done()


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

# Create the server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print(f"Server listening on {HOST}:{PORT}")

def initialize_player_scores():
    for player_id in game_state['players']:
        game_state['player_scores'][player_id] = 0

# Accept and handle client connections
client_sockets = {}
player_id_counter = 0
PLAYER_SPEED = 1  # Added player speed constant
initialize_player_scores()  # Initialize player scores

while True:
    client_socket, _ = server.accept()
    player_id = player_id_counter
    player_id_counter += 1
    client_sockets[player_id] = client_socket

    # Initialize player's position
    game_state['players'][player_id] = (random.randint(0, WIDTH - PLAYER_SIZE), random.randint(0, HEIGHT - PLAYER_SIZE))

    client_thread = threading.Thread(target=handle_client, args=(client_socket, player_id))
    client_thread.start()