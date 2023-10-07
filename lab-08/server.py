# CS21B2019 DSLR SIDDESH
# server.py
import socket
import threading
import random
import pickle
import time
import os
from dataclasses import dataclass

IP = socket.gethostbyname(socket.gethostname())
PORT = 8085
ADDR = (IP, PORT)
SIZE = 4096

clients = {}
players = []
queue = []

logged_in_macs = []
active_clients = 0
max_players = 4
game_price = 60/100

WIDTH, HEIGHT = 600, 400
PLAYER_SPEED = 1.5
PLAYER_SIZE = 30
COIN_SIZE = 15
COIN_COUNT = 10
MAX_PLAYERS = 4
WINNING_SCORE = 10

game_state = {
    'players': {},          
    'player_scores': {},    
    'coins': [(random.randint(0, WIDTH - COIN_SIZE), random.randint(0, HEIGHT - COIN_SIZE)) for _ in range(COIN_COUNT)],
    'color': {}             
}

@dataclass
class Client:
    '''Client class to store client information'''
    conn: socket.socket
    addr: str
    player: int
    mac: str = None
    time: float = 0.0
    connected: bool = True

def get_next_player():
    all_players = sorted([c.player for c in players])
    player = 1
    for p in all_players:
        if p == player:
            player += 1
        else:
            break
    return player

def disconnect_client(client: Client):
    global active_clients
    print(f"[DISCONNECT CLIENT] {client.addr} disconnected.")

    active_clients -= 1
    print(f"[ACTIVE CLIENTS] {active_clients}")

    if client in players:
        players.remove(client)
        game_state['players'].pop(client.player)
        game_state['player_scores'].pop(client.player)
        game_state['color'].pop(client.player)
        # initialize_player_scores()
    else:
        queue.remove(client)
    client.connected = False
    try:
        logged_in_macs.remove(client.mac)
        client.conn.close()
    except:
        pass

def player_timer(client: Client):
    while client.connected:
        client.time -= 1
        if client.time <= 0:
            client.conn.send(pickle.dumps("TIMEOUT"))
            time.sleep(0.1)
            disconnect_client(client)
            break
        time.sleep(1)

def add_player(client: Client):
    logged_in_macs.append(client.mac)

    if len(players) > max_players:  # If players are full
        client.player = -1
        queue.append(client)
    else:
        client.player = get_next_player()
        players.append(client)
        # Initialize player's position
        player_x = random.randint(0, WIDTH - PLAYER_SIZE)
        player_y = random.randint(0, HEIGHT - PLAYER_SIZE)
        game_state['players'][client.player] = (player_x, player_y)

        
        display_color = (random.randint(10, 255) for _ in range(3))
        game_state['color'][client.player] = tuple(display_color)
        game_state['player_scores'][client.player] = game_state['player_scores'].get(client.player, 0)
        timer_thread = threading.Thread(target=player_timer, args=(client,))
        timer_thread.start()
    
    client.conn.send(pickle.dumps(client.player))
    time.sleep(0.1)

def update_player_position(player_id, input_data):
    global game_state
    # print(game_state['players'])
    player_x, player_y = game_state['players'][player_id]
    if input_data['left']:
        player_x -= PLAYER_SPEED
    if input_data['right']:
        player_x += PLAYER_SPEED
    if input_data['up']:
        player_y -= PLAYER_SPEED
    if input_data['down']:
        player_y += PLAYER_SPEED
    player_x = max(0, min(player_x, WIDTH - PLAYER_SIZE))
    player_y = max(0, min(player_y, HEIGHT - PLAYER_SIZE))

    game_state['players'][player_id] = (player_x, player_y)

def handle_client(client: Client):
    addr = client.addr
    conn = client.conn
    print(f"> [NEW CONNECTION] {addr} connected.")

    while True:
        data = conn.recv(SIZE)
        if not data:
            break
        input_data = pickle.loads(data)
        msg = input_data
        if type(msg) == str:
            print(msg)
            if "REGISTER" in msg:
                _, mac = msg.split("/")
                if mac in clients:
                    conn.send(pickle.dumps("MAC already registered"))
                else:
                    clients[mac] = client
                    client.mac = mac
                    conn.send(pickle.dumps("OK"))
            elif "PAY" in msg:
                _, mac, amount = msg.split("/")
                if mac in clients:
                    clients[mac].time += int(amount) * game_price
                    print(f"Client paid {clients[mac].time} seconds")
                    conn.send(pickle.dumps("OK"))
                else:
                    conn.send(pickle.dumps("MAC not registered"))
            elif "LOGIN" in msg:
                _, mac = msg.split("/")
                if mac in logged_in_macs:
                    conn.send(pickle.dumps("MAC already logged in"))
                elif mac in clients:
                    client.mac = mac
                    client.time = clients[mac].time
                    clients[mac] = client
                    conn.send(pickle.dumps("OK"))
                    time.sleep(0.1)
                    add_player(client)
                else:
                    conn.send(pickle.dumps("MAC not registered"))
        else:
            update_player_position(client.player, input_data)
            
            coins_to_remove = []
            for i, (coin_x, coin_y) in enumerate(game_state['coins']):
                player_x, player_y = game_state['players'][client.player]
                if player_x < coin_x + COIN_SIZE and player_x + PLAYER_SIZE > coin_x and player_y < coin_y + COIN_SIZE and player_y + PLAYER_SIZE > coin_y:
                    coins_to_remove.append(i)
                    game_state['player_scores'][client.player] = game_state['player_scores'].get(client.player, 0) + 1
            
            for i in coins_to_remove:
                game_state['coins'].pop(i)
                new_coin_x = random.randint(0, WIDTH - COIN_SIZE)
                new_coin_y = random.randint(0, HEIGHT - COIN_SIZE)
                game_state['coins'].append((new_coin_x, new_coin_y))
            
            game_update = pickle.dumps(game_state)
            for connection in players:
                connection.conn.send(game_update)
    
    del game_state['players'][client.player]
    clients.pop(client.player)
    conn.close()

def server_loop():
    global active_clients
    print("> Server is starting...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    server.listen()
    print(f"> Server is listening on {IP}:{PORT}")
    print(f"> [Active Connections] {active_clients}")
    
    player_id_counter = 0

    while True:
        conn, addr = server.accept()
        addr = "{addr[0]}:{addr[1]}"

        current_client = Client(conn, addr, 0)
        active_clients += 1

        client_thread = threading.Thread(target=handle_client, args=(current_client, ))
        client_thread.start()

        print(f"> [Active Connections] {threading.active_count() - 1}")

def main():
    
    server_thread = threading.Thread(target=server_loop)
    server_thread.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n> Server stopped.")
        os._exit(0)