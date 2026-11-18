# myroguelike.py
# consider renaming to gameloop.py

import pygame
from modes import handle_events, new_game_state, PLAY, WAIT_PROMPT, WAITING, LOOK, CHOOSE_CHAT, DIALOGUE, CONFIRM_ATTACK, DEAD
from draw import render_map, render_message_log, render_player_status, render_key_hints, render_look_cursor
from map import Map, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, GRAY, LOG_ROWS
from help_texts import KEY_HINTS, WAIT_KEY_HINTS, LOOK_KEY_HINTS, CHAT_KEY_HINTS, DIALOGUE_KEY_HINTS, CONFIRM_KEY_HINTS, DEATH_KEY_HINTS

BOTTOM_UI_HEIGHT = LOG_ROWS + 1     # the message log, and a row of key hints under it
FPS = 30

# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, (MAP_HEIGHT + BOTTOM_UI_HEIGHT) * TILE_SIZE))
pygame.display.set_caption("MYRoguelike")
clock = pygame.time.Clock()

# Initialize a font
font = pygame.font.SysFont(None, 22)

# Draw the message log (from row log_offset on), the key hints and the map, then wait for the next frame.
# look_target is the creature selected in look mode, or None.
def draw_frame(game_map, messages, log_offset, key_hints, look_target=None):
    screen.fill(GRAY)
    render_message_log(messages, log_offset, pygame, screen, font)
    render_player_status(game_map.player, pygame, screen, font)
    render_key_hints(key_hints, pygame, screen, font)
    render_map(game_map, pygame, screen, font, game_map.player)
    if look_target is not None:
        render_look_cursor(look_target, pygame, screen, font)
    pygame.display.flip()
    clock.tick(FPS)

# The key hint row shown in each mode
KEY_HINTS_FOR_MODE = {
    PLAY: KEY_HINTS,
    WAIT_PROMPT: KEY_HINTS,
    WAITING: WAIT_KEY_HINTS,
    LOOK: LOOK_KEY_HINTS,
    CHOOSE_CHAT: CHAT_KEY_HINTS,
    DIALOGUE: DIALOGUE_KEY_HINTS,
    CONFIRM_ATTACK: CONFIRM_KEY_HINTS,
    DEAD: DEATH_KEY_HINTS,
}

# The creature the blinking cursor is on: the one looked at, chosen to talk to, or talked with
def cursor_creature(game_state):
    mode = game_state["mode"]
    if mode == LOOK:
        return game_state["look_target"]
    if mode == CHOOSE_CHAT:
        return game_state["chat_target"]
    if mode == DIALOGUE:
        return game_state["dialogue"]
    return None

# Play one game, from a new map to the death screen. Returns when the player wants to play again.
def play_game():
    # Generate the map with its creatures
    game_map = Map()
    game_map.messages = ["Welcome to Myr!", "Move around with arrows or numpad.", "Moving towards an 'o'rc or other creatures attacks.", "Good luck!"]
    game_state = new_game_state()

    # Main loop: dying switches to the DEAD mode, where r plays again
    while True:
        if handle_events(pygame, game_map, game_state) == "restart":
            return
        draw_frame(game_map, game_map.messages, game_map.log_offset,
                   KEY_HINTS_FOR_MODE[game_state["mode"]], cursor_creature(game_state))

# Play games until the player quits; quitting exits the program from inside the loop
while True:
    play_game()
