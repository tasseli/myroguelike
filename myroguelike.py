# Example file showing a basic pygame "game loop"
import pygame
import sys

# Todo
# map generation
# agent knowledge
# agent communication (language, )
# agent faction
# faction knowledge
# faction communication
# cultures for groups?
# languages based on INT
# bartering based on language / abilities
# "Look at ..." "It doesn't make sense to you" / "you see another Dwarven healer with a spellbook of second circle on their backpack, probably"

# Define constants for tile types
OPEN_SPACE = 0
WALL = 1

# Define colors for tiles
WHITE = (255, 255, 255)  # Open space
GRAY = (128, 128, 128)   # Wall

# Define the dimensions of the map
MAP_WIDTH = 80
MAP_HEIGHT = 20
TILE_SIZE = 8

# Initialize an empty map
game_map = [[OPEN_SPACE for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

# Example: Set a wall at position (5, 5)
game_map[5][5] = WALL


# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE))
pygame.display.set_caption("Simple Roguelike Map")

# Initialize an empty map
game_map = [[OPEN_SPACE for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

# Set a wall at position (5, 5)
game_map[5][5] = WALL

#player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)


 # Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear the screen
    screen.fill(WHITE)

    # Render the map
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if game_map[x][y] == WALL:
                pygame.draw.rect(screen, GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Update the display
    pygame.display.flip()
