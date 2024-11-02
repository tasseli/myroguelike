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
game_map.set_location(current_pos, player.sign)

def init_orc(coords):
    orc = Orc(coords)
    orc_pos = orc.get_position()
    game_map.set_location(orc_pos, orc.sign)
    return orc

#orc = Orc([5,12])
orc = init_orc([5,12])
orc2 = Orc([1,3])
orc3 = Orc([72,33])
orc4 = Orc([37,23])
orc5 = Orc([6,38])
orc2_pos = orc2.get_position()
orc3_pos = orc3.get_position()
orc4_pos = orc4.get_position()
orc5_pos = orc5.get_position()
game_map.set_location(orc2_pos, orc2.sign)
game_map.set_location(orc3_pos, orc3.sign)
game_map.set_location(orc4_pos, orc4.sign)
game_map.set_location(orc5_pos, orc5.sign)

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
#               print("Move key selected")
                pass
            elif outcome == "s":
#               print("Stay still key selected")
                pass
            if game_map.move_if_available(new_position, player):
                game_map.move_if_available(orc.move_right(), orc)
                game_map.move_if_available(orc2.move_random(), orc2)
                game_map.move_if_available(orc3.move_toward(player.get_position()), orc3)
                game_map.move_if_available(orc4.move_toward(orc3.get_position()), orc4)
                game_map.move_if_available(orc5.move_toward(orc4.get_position()), orc5)

    # Clear the screen
    screen.fill(GRAY)

    # Render the map
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if game_map.get_location(x,y) == OPEN_SPACE:
                pass
            else:
                draw_and_blit_char(pygame, screen, font, game_map.get_location(x,y), x, y)

    # Update the display
    pygame.display.flip()
