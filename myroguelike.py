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

def init_orc(coords, mood, target, creatures):
    orc = Orc(coords, mood, target)
    game_map.set_sign_with_creature(orc)
    creatures.append(orc)
    return orc

def quit_app(reason):
    print(reason)
    pygame.quit()
    sys.exit()    

player = init_player([3,6])

creatures = []
orc = init_orc([5,12], "run right", None, creatures)
orc2 = init_orc([1,3], None, None, creatures)
orc3 = init_orc([72,33], "toward", player, creatures)
orc4 = init_orc([37,23], "toward", orc3, creatures)
orc5 = init_orc([6,38], "toward", orc4, creatures)

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
                    for i in range(0, len(creatures)):
                        game_map.move_if_available_naturally(creatures[i])

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
