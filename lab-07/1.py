import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 30
COIN_SIZE = 15
PLAYER_SPEED = 1
COIN_SPEED = 1
COIN_COUNT = 10
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Collector Game")

# Player setup
player_x = WIDTH // 2 - PLAYER_SIZE // 2
player_y = HEIGHT - PLAYER_SIZE - 10

# Coin setup
coins = []
for _ in range(COIN_COUNT):
    coin_x = random.randint(0, WIDTH - COIN_SIZE)
    coin_y = random.randint(0, HEIGHT - COIN_SIZE)
    coins.append((coin_x, coin_y))

# Game loop
running = True
score = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        player_x += PLAYER_SPEED
    if keys[pygame.K_UP]:
        player_y -= PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        player_y += PLAYER_SPEED

    # Update player position
    player_x = max(0, min(player_x, WIDTH - PLAYER_SIZE))
    player_y = max(0, min(player_y, HEIGHT - PLAYER_SIZE))

    # Check for collisions with coins
    coins_to_remove = []
    for i, (coin_x, coin_y) in enumerate(coins):
        if (
            player_x < coin_x + COIN_SIZE
            and player_x + PLAYER_SIZE > coin_x
            and player_y < coin_y + COIN_SIZE
            and player_y + PLAYER_SIZE > coin_y
        ):
            coins_to_remove.append(i)
            score += 1

    for i in coins_to_remove:
        coins.pop(i)
        new_coin_x = random.randint(0, WIDTH - COIN_SIZE)
        new_coin_y = random.randint(0, HEIGHT - COIN_SIZE)
        coins.append((new_coin_x, new_coin_y))

    # Clear the screen
    screen.fill(BLACK)

    # Draw player
    pygame.draw.rect(screen, YELLOW, (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))

    # Draw coins
    for coin_x, coin_y in coins:
        pygame.draw.ellipse(screen, YELLOW, (coin_x, coin_y, COIN_SIZE, COIN_SIZE))

    # Display score
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, YELLOW)
    screen.blit(text, (10, 10))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()