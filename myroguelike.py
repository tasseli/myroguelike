# myroguelike.py
# consider renaming to gameloop.py

import pygame
from loop_utils import handle_events, handle_death_screen_keys
from draw import render_map, render_message_log, render_player_status, render_key_hints, render_look_cursor
from map import Map, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, GRAY, LOG_ROWS
from help_texts import KEY_HINTS, WAIT_KEY_HINTS, LOOK_KEY_HINTS, CHAT_KEY_HINTS, DIALOGUE_KEY_HINTS, DEATH_KEY_HINTS

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

# Play one game, from a new map to the death screen. Returns when the player wants to play again.
def play_game():
    # Generate the map with its creatures
    game_map = Map()

    # Main loop
    game_map.messages = ["Welcome to Myr!", "Move around with arrows or numpad.", "Moving towards an 'o'rc or other creatures attacks.", "Good luck!"]
    game_state = {"GAME_ON": True}
    while game_state["GAME_ON"]:
        handle_events(pygame, game_map, game_state)
        # the blinking cursor is on the creature looked at, chosen to talk to, or talked with
        looking_at = game_state.get("look_target") or game_state.get("chat_target") or game_state.get("dialogue")
        if game_state.get("waiting") is not None:
            key_hints = WAIT_KEY_HINTS
        elif game_state.get("look_target") is not None:
            key_hints = LOOK_KEY_HINTS
        elif game_state.get("chat_target") is not None:
            key_hints = CHAT_KEY_HINTS
        elif game_state.get("dialogue") is not None:
            key_hints = DIALOGUE_KEY_HINTS
        else:
            key_hints = KEY_HINTS
        draw_frame(game_map, game_map.messages, game_map.log_offset, key_hints, looking_at)

    # game_state is GAME_ON==False, player has died
    killer = game_map.killed_by
    article = "an" if killer[0] in "aeiou" else "a"     # an orc, a gnoll
    death_messages = ["You died gloriously on the battlefield!", "Killed by " + article + " " + killer + ".", "Thank you for playing. Better luck next time.", "Press 'r' to play again, 'l' to look around or 'q' to quit."]
    while True:
        if handle_death_screen_keys(pygame, game_map, game_state) == "restart":
            return
        looking_at = game_state.get("look_target")
        if looking_at is not None:
            draw_frame(game_map, game_map.messages, 0, LOOK_KEY_HINTS, looking_at)
        else:
            draw_frame(game_map, death_messages, 0, DEATH_KEY_HINTS)

# Play games until the player quits; quitting exits the program from inside the loops
while True:
    play_game()
