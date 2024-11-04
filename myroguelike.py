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
BOTTOM_UI_HEIGHT = 2

# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, (MAP_HEIGHT+BOTTOM_UI_HEIGHT) * TILE_SIZE))
pygame.display.set_caption("MYRoguelike")

# Initialize an empty map
game_map = Map()

# Initialize a font
font = pygame.font.SysFont(None, 22)

def init_player(coords):
    player = Player(coords)
    current_pos = player.get_position()
    game_map.set_sign_with_creature(player)
    return player

def init_orc(coords, mood, target):
    orc = Orc(coords, mood, target)
    game_map.set_sign_with_creature(orc)
    return orc

def quit_app(reason):
    print(reason)
    pygame.quit()
    sys.exit()    

creatures = []
player = init_player([3,6])
creatures.append(player)
orc = init_orc([5,12], "run East", None)
creatures.append(orc)
orc2 = init_orc([1,3], None, None)
creatures.append(orc2)
orc3 = init_orc([72,33], "toward", player)
creatures.append(orc3)
orc4 = init_orc([37,23], "toward", orc3)
creatures.append(orc4)
orc5 = init_orc([6,38], "toward", orc4)
creatures.append(orc5)

# Main loop

while True:
    y = 0
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
            elif outcome == "m" or outcome == "s":
#               print("Move key or stand still key")
                if game_map.move_if_available(player, new_position):
#                    game_map.move_if_available_naturally(creatures[0])
                    game_map.move_if_available(orc, orc.move_right())
                    game_map.move_if_available(orc2, orc2.move_random())
                    game_map.move_if_available(orc3, orc3.move_toward(player.get_position()))
                    game_map.move_if_available(orc4, orc4.move_toward(orc3.get_position()))
                    game_map.move_if_available(orc5, orc5.move_toward(orc4.get_position()))

    # Clear the screen
    screen.fill(GRAY)

    # Render the map
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if game_map.get_sign(x,y) == OPEN_SPACE:
                pass
            else:
                draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y)

    for y in range(y, y+BOTTOM_UI_HEIGHT):
        for x in range(MAP_WIDTH):
            if y==MAP_HEIGHT:
                draw_and_blit_char(pygame, screen, font, "-", x,y)

    # Update the display
    pygame.display.flip()
