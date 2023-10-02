import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants for window dimensions
WIDTH, HEIGHT = 400, 300
WINDOW_SIZE = (WIDTH, HEIGHT)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Create a window
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Button Click Example")

# Initialize your variable that will become True
PAID = False

# Define the button properties
button_rect = pygame.Rect(WIDTH//2, HEIGHT//2, 100, 50)
button_color = (0, 128, 255)

# Create a font
font = pygame.font.Font(None, 36)

# Create text to display on the button
button_text = font.render("Click Me", True, WHITE)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Check for mouse button click events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                PAID = True

    # Clear the screen
    screen.fill(BLACK)

    # Draw the button
    pygame.draw.rect(screen, button_color, button_rect)
    screen.blit(button_text, (165, 110))

    # Update the display
    pygame.display.flip()
