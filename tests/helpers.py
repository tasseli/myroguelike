# tests/helpers.py
# Shared setup and helpers for the smoke test: runs pygame without a window, imports the
# game's modules, and has helpers to build test situations and press keys.

import os
import sys
import random
import runpy

# run without a window and without pygame's greeting
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# the game's modules are in the folder above tests/
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

import map as m
import modes
import monsters
from creatures import Player, Orc, CHASE, WANDER, FLEE, FRIEND, RUN_RIGHT

KEYS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_KP1,
        pygame.K_KP3, pygame.K_KP7, pygame.K_KP9, pygame.K_KP5, pygame.K_a]


# A map with only the player on it, standing in the middle of one big room (30 x 24), so that the
# rule checks have room around the player whatever the dungeon generation makes
def empty_room_map():
    random.seed(0)
    game_map = m.Map()
    game_map.my_map = [[m.WALL for y in range(m.MAP_HEIGHT)] for x in range(m.MAP_WIDTH)]
    room = (25, 8, 55, 32)
    for x in range(room[0], room[2]):
        for y in range(room[1], room[3]):
            game_map.my_map[x][y] = m.OPEN_SPACE
    game_map.rooms, game_map.corridor = [room], []
    game_map.distance_cache = {}        # the walls changed
    game_map.view_cache = {}
    game_map.creatures = []
    place(game_map, game_map.player, 40, 20)
    return game_map

def place(game_map, creature, x, y):
    creature.position = [x, y]
    game_map.my_map[x][y] = creature.sign
    game_map.creatures.append(creature)

def press(game_map, *keys, game_state=None):
    if game_state is None:
        game_state = modes.new_game_state()
    for key in keys:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
        modes.handle_events(pygame, game_map, game_state)

# Run game frames with no keys pressed, like the game loop does, until waiting ends. Return the frame count.
def run_frames_while_waiting(game_map, game_state):
    frames = 0
    while game_state.get("waiting") is not None and frames < 100000:
        modes.handle_events(pygame, game_map, game_state)
        frames += 1
    return frames
