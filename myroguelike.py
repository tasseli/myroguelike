# myroguelike.py
# consider renaming to gameloop.py

import pygame
from loop_utils import handle_events, handle_quit_key
from draw import render_map, render_message_log
from map import (Map, 
MAP_WIDTH, MAP_HEIGHT, TILE_SIZE)
from map import (WHITE, GRAY, DARK_GRAY, BLACK)
BOTTOM_UI_HEIGHT = 4
from loop_utils import quit_app

# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, (MAP_HEIGHT + BOTTOM_UI_HEIGHT) * TILE_SIZE))
pygame.display.set_caption("MYRoguelike")

# Initialize a font
font = pygame.font.SysFont(None, 22)

# Initialize an empty map
game_map = Map()

# Main loop

messages = ["Welcome to Myr!", "Move around with arrows or numpad.", "Moving towards an 'o'rc or other creatures attacks.", "Good luck!"]
game_state = {"GAME_ON": True}
while game_state["GAME_ON"]:
    # Clear the screen
    screen.fill(GRAY)

    # print message log
    render_message_log(messages, pygame, screen, font)
    
    # handle events
    messages = handle_events(pygame, game_map, messages, game_state)

    # Render the map
    render_map(game_map, pygame, screen, font)
    
    # Update the display
    pygame.display.flip()

# game_state is GAME_ON==False, player has died
messages = ["You died gloriously on the battlefield!", "Thank you for playing. Better luck next time.", "Press 'q' to quit."]
while True:
    # Clear the screen
    screen.fill(GRAY)

    # print message log
    render_message_log(messages, pygame, screen, font)
    
    # handle events
    messages = handle_quit_key(pygame, game_map, messages, game_state)

    # Render the map
    render_map(game_map, pygame, screen, font)
    
    # Update the display
    pygame.display.flip()