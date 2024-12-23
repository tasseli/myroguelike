# myroguelike.py

import pygame
import sys
from death import check_deaths
from draw import render_map, render_message_log
from map import (Map, 
MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
OPEN_SPACE, WALL, PLAYER, ORC)
from map import (draw_and_blit_char,
WHITE, GRAY, DARK_GRAY, BLACK)
from keyboard import read_moves
BOTTOM_UI_HEIGHT = 4

# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, (MAP_HEIGHT + BOTTOM_UI_HEIGHT) * TILE_SIZE))
pygame.display.set_caption("MYRoguelike")

# Initialize a font
font = pygame.font.SysFont(None, 22)

def quit_app(reason):
    print(reason)
    pygame.quit()
    sys.exit()    

# Initialize an empty map
game_map = Map()

# Main loop

messages = ["Welcome to Myr!", "Move around with arrows or numpad.", "Moving towards an 'o'rc attacks.", "Good luck!"]
while True:
    # Clear the screen
    screen.fill(GRAY)

    # print message log
    render_message_log(messages, pygame, screen, font)
    
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("event.type == quit")
        if event.type == pygame.KEYDOWN:
            new_position = game_map.player.get_position().copy()
            outcome = read_moves(new_position, event.key, pygame)
            if outcome == "q":
                quit_app("q or x pressed")
            elif outcome == "o":
#               An unhandled key was pressed
                pass
            elif outcome == "m" or outcome == "s":
#               Move key or stand still key
                messages = [""]
                death_notes1 = []
                if game_map.move_to(0, new_position, game_map.creatures): # 0 refers to the player
                    death_notes1 = check_deaths(game_map, False)   # check if player killed anyone
                death_notes2 = check_deaths(game_map, True)    # have all creatures move and check if they killed anyone
                if len(death_notes1) > 0:
                    messages = death_notes1
                if len(death_notes1) > 0:
                    messages += death_notes2

    # Render the map
    render_map(game_map, pygame, screen, font)
    
    # Update the display
    pygame.display.flip()

