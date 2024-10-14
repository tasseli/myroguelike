#myroguelike.py

import pygame
import sys
from map import (Map, 
MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
OPEN_SPACE, WALL, PLAYER, ORC)

class Player:
    def __init__(self):
        self.position = [3, 6]

    def get_position(self):
        return self.position

class Orc:
    def __init__(self):
        self.position = [62, 30]

    def get_position(self):
        return self.position

    def move(self):
        self.position[0] = self.position[0] + 1

# Define colors for tiles
WHITE = (255, 255, 255)  # Open space
GRAY = (128, 128, 128)   # Wall
DARK_GRAY = (64, 64, 64)
BLACK = (0, 0, 0)        # Text color

# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE))
pygame.display.set_caption("Simple Roguelike Map")

# Initialize an empty map
game_map = Map()

# Initialize a font
font = pygame.font.SysFont(None, 22)
    
player = Player()
current_pos = player.get_position()
game_map.set_location(current_pos, 2)

orc = Orc()
orc_pos = orc.get_position()
game_map.set_location(orc_pos, 3)

def draw_and_blit_char(my_char, x, y):
    pygame.draw.rect(screen, DARK_GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Render the my_char ('#'/'@') character on top of the background color
    text_surface = font.render(my_char, True, BLACK)
    text_rect = text_surface.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
    screen.blit(text_surface, text_rect)

 # Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            new_position = player.get_position().copy()
            if event.key == pygame.K_q or event.key == pygame.K_x:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4:
                new_position[0] -= 1
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6:
                new_position[0] += 1
            elif event.key == pygame.K_UP or event.key == pygame.K_KP8:
                new_position[1] -= 1
            elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2:
                new_position[1] += 1
            elif event.key == pygame.K_1 or event.key == pygame.K_KP1:
                new_position[0] -= 1
                new_position[1] += 1
            elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                new_position[0] += 1
                new_position[1] += 1
            elif event.key == pygame.K_7 or event.key == pygame.K_KP7:
                new_position[0] -= 1
                new_position[1] -= 1
            elif event.key == pygame.K_9 or event.key == pygame.K_KP9:
                new_position[0] += 1
                new_position[1] -= 1
            else:
                continue

            # Check if the new position is not a wall
            if game_map.my_map[new_position[0]][new_position[1]] == OPEN_SPACE:
                # Clear the old position
                current_pos = player.get_position()
                game_map.my_map[current_pos[0]][current_pos[1]] = OPEN_SPACE
                # Update the player position
                player.position = new_position
                # Mark the new position with PLAYER
                game_map.my_map[player.position[0]][player.position[1]] = PLAYER
                orc.move()
                game_map.my_map[orc.position[0]][orc.position[1]] = ORC
                
    # Clear the screen
    screen.fill(GRAY)

    # Render the map
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if game_map.get_location(x,y) == WALL:
                draw_and_blit_char("#", x, y)
            elif game_map.get_location(x,y) == PLAYER:
                draw_and_blit_char("@", x, y)
            elif game_map.get_location(x,y) == ORC:
                draw_and_blit_char("o", x, y)

    # Update the display
    pygame.display.flip()
