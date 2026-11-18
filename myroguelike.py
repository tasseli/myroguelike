# myroguelike.py
# consider renaming to gameloop.py

import pygame
from loop_utils import handle_events, handle_quit_key
from draw import render_map, render_message_log, render_player_status
from map import Map, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, GRAY, LOG_ROWS

BOTTOM_UI_HEIGHT = LOG_ROWS
FPS = 30

# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, (MAP_HEIGHT + BOTTOM_UI_HEIGHT) * TILE_SIZE))
pygame.display.set_caption("MYRoguelike")
clock = pygame.time.Clock()

# Initialize a font
font = pygame.font.SysFont(None, 22)

# Generate the map with its creatures
game_map = Map()

# Draw the message log (from row log_offset on) and the map, then wait for the next frame
def draw_frame(messages, log_offset):
    screen.fill(GRAY)
    render_message_log(messages, log_offset, pygame, screen, font)
    render_player_status(game_map.player, pygame, screen, font)
    render_map(game_map, pygame, screen, font, game_map.player)
    pygame.display.flip()
    clock.tick(FPS)

# Main loop
game_map.messages = ["Welcome to Myr!", "Move around with arrows or numpad.", "Moving towards an 'o'rc or other creatures attacks.", "Good luck!"]
game_state = {"GAME_ON": True}
while game_state["GAME_ON"]:
    handle_events(pygame, game_map, game_state)
    draw_frame(game_map.messages, game_map.log_offset)

# game_state is GAME_ON==False, player has died
killer = game_map.killed_by
article = "an" if killer[0] in "aeiou" else "a"     # an orc, a gnoll
death_messages = ["You died gloriously on the battlefield!", "Killed by " + article + " " + killer + ".", "Thank you for playing. Better luck next time.", "Press 'q' to quit."]
while True:
    handle_quit_key(pygame)
    draw_frame(death_messages, 0)
