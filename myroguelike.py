# myroguelike.py

import pygame
import sys
from map import (Map, 
MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
OPEN_SPACE, WALL, PLAYER, ORC)
from map import (draw_and_blit_char,
WHITE, GRAY, DARK_GRAY, BLACK)
from keyboard import read_moves
from creatures import Player, Orc

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

def quit_app(reason):
    print(reason)
    pygame.quit()
    sys.exit()    

# Main loop

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("event.type == quit")
        if event.type == pygame.KEYDOWN:
            new_position = player.get_position().copy()
            outcome = read_moves(new_position, event.key, pygame)
            if outcome == "q":
                quit_app("q or x pressed")
            elif outcome == "o":
#               print("An unhandled key was pressed.")
                pass
            elif outcome == "m":
                pass

            # Make this into a function of the map, based on the creature and the new coord
            # Check if the new position is free (otherwise don't move)
            if game_map.my_map[new_position[0]][new_position[1]] == OPEN_SPACE:
                # Clear the old position
                current_pos = player.get_position()
                game_map.my_map[current_pos[0]][current_pos[1]] = OPEN_SPACE
                # Update the player position
                player.position = new_position
                # Mark the new position with PLAYER
                game_map.my_map[player.position[0]][player.position[1]] = PLAYER
                # dummy orc only moves right :)
                if game_map.my_map[orc.position[0]+1][orc.position[1]] == OPEN_SPACE:
                    orc_position_old = orc.get_position().copy()
                    orc.move()
                    game_map.my_map[orc.position[0]][orc.position[1]] = ORC
                    game_map.my_map[orc_position_old[0]][orc_position_old[1]] = OPEN_SPACE
                
    # Clear the screen
    screen.fill(GRAY)

    # Render the map
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if game_map.get_location(x,y) == WALL:
                draw_and_blit_char(pygame, screen, font, "#", x, y)
            elif game_map.get_location(x,y) == PLAYER:
                draw_and_blit_char(pygame, screen, font, "@", x, y)
            elif game_map.get_location(x,y) == ORC:
                draw_and_blit_char(pygame, screen, font, "o", x, y)

    # Update the display
    pygame.display.flip()
