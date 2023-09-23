import pygame

# Initialize Pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Set window dimensions
WINDOW_WIDTH = 360
WINDOW_HEIGHT = 480
SELECTION_WIDTH = 120

# Set block dimensions
BLOCK_WIDTH = 40
BLOCK_HEIGHT = 40

# Set block types
BLOCK_TYPES = [
    [(2, 1)],  # 2 long block
    [(3, 1)],  # 3 long block
    [(2, 1)]   # 2 long red block
]

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Unblock Me Level Creator")

clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the window
    window.fill(WHITE)

    # Draw the block selection area
    pygame.draw.rect(window, GRAY, (WINDOW_WIDTH - SELECTION_WIDTH, 0, SELECTION_WIDTH, WINDOW_HEIGHT))

    # Draw the block types in the selection area
    selection_x = WINDOW_WIDTH - SELECTION_WIDTH + 10
    selection_y = 20
    for i, block_type in enumerate(BLOCK_TYPES):
        block_width = block_type[0][0] * BLOCK_WIDTH
        block_height = block_type[0][1] * BLOCK_HEIGHT
        block_x = selection_x + (SELECTION_WIDTH - block_width) // 2
        block_y = selection_y + (BLOCK_HEIGHT + block_height) * i
        pygame.draw.rect(window, GRAY, (block_x, block_y, block_width, block_height))

    # Update the display
    pygame.display.update()
    clock.tick(60)

# Quit the game
pygame.quit()
