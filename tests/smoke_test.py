# tests/smoke_test.py
#
# A quick check that the game still basically works. Run it from anywhere with:
#     python tests/smoke_test.py
# It prints OK lines and totals, or stops with an AssertionError that says what broke.
#
# 1. rule checks:  small exact checks of single rules (healing)
# 2. random games: 200 games of random key presses through the real handle_events,
#                  checking after every turn that the game state still makes sense
# 3. real game:    runs myroguelike.py itself for a moment without a window

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
import loop_utils
from creatures import Player, Orc

KEYS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_KP1,
        pygame.K_KP3, pygame.K_KP7, pygame.K_KP9, pygame.K_KP5, pygame.K_a]


# 1. rule checks

def check_healing():
    player = Player([1, 1])
    player.health = 5
    health_each_turn = []
    for turn in range(60):
        player.heal_slowly()
        health_each_turn.append(player.health)
    # turn 20 is index 19
    assert health_each_turn[18] == 5 and health_each_turn[19] == 6, health_each_turn
    assert health_each_turn[39] == 7 and health_each_turn[59] == 8, health_each_turn

    player.health = player.health_max
    for turn in range(40):
        player.heal_slowly()
    assert player.health == player.health_max, "healed above max"

    orc = Orc([1, 1])
    orc.health = 0
    for turn in range(40):
        orc.heal_slowly()
    assert orc.health == 0, "a dead creature healed"
    print("OK rule checks: healing")


# 2. random games

# Things that must always be true between turns
def check_consistency(game_map):
    assert game_map.creatures[0] is game_map.player, "the player is not first in the list"
    positions = [tuple(c.position) for c in game_map.creatures]
    assert len(set(positions)) == len(positions), "two creatures share a tile"
    for c in game_map.creatures:
        x, y = c.position
        assert game_map.my_map[x][y] == c.sign, f"{c.name} at {x},{y} but map has {game_map.my_map[x][y]!r}"
        assert c.alive, f"a dead {c.name} is still in the list"
        assert c.health <= c.health_max, f"{c.name} has more than max health"
    creature_tiles = sum(1 for column in game_map.my_map for tile in column
                         if tile not in (m.OPEN_SPACE, m.WALL))
    assert creature_tiles == len(game_map.creatures), \
        f"{creature_tiles} creature tiles on the map, but {len(game_map.creatures)} creatures"

def check_spawns(game_map):
    left, top, right, bottom = game_map.room
    assert right - left >= 8 and bottom - top >= 8, "room smaller than 8x8"
    for c in game_map.creatures:
        x, y = c.position
        assert left <= x < right and top <= y < bottom, f"{c.name} spawned outside the room"
    # monsters start at least MIN_SPAWN_DISTANCE moves away, if the room has enough such tiles
    px, py = game_map.player.position
    far_tiles = sum(1 for x in range(left, right) for y in range(top, bottom)
                    if max(abs(x - px), abs(y - py)) >= m.MIN_SPAWN_DISTANCE)
    if far_tiles >= len(game_map.creatures) - 1:
        for c in game_map.creatures[1:]:
            distance = max(abs(c.position[0] - px), abs(c.position[1] - py))
            assert distance >= m.MIN_SPAWN_DISTANCE, f"{c.name} spawned {distance} moves from the player"

def check_hit_messages(messages):
    for message in messages:
        if " hit for " in message:
            victim = message.split(" hit for ")[0]
            attacker = message.split(" damage by ")[1]
            # only orcs have non-player targets (other orcs)
            assert "player" in (victim, attacker) or (victim, attacker) == ("orc", "orc"), \
                "attack against the rules: " + message

def play_random_games(games=200, max_turns=300):
    totals = {"turns": 0, "hits": 0, "deaths": 0, "heals": 0, "player deaths": 0}
    for game in range(games):
        random.seed(game)       # same games every run, so results can be compared and repeated
        game_map = m.Map()
        check_spawns(game_map)
        check_consistency(game_map)
        game_state = {"GAME_ON": True}
        for turn in range(max_turns):
            health_before = {id(c): c.health for c in game_map.creatures}
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=random.choice(KEYS)))
            loop_utils.handle_events(pygame, game_map, game_state)
            totals["turns"] += 1
            totals["hits"] += sum(" hit for " in s for s in game_map.messages)
            totals["deaths"] += sum("dies!" in s for s in game_map.messages)
            check_hit_messages(game_map.messages)
            if not game_state["GAME_ON"]:
                assert game_map.player.health < 1, "game ended but the player is alive"
                killers = {"orc", "uruk", "kobold", "gnoll", "goblin", "golem"}
                assert game_map.killed_by in killers, f"killed_by is {game_map.killed_by!r}"
                totals["player deaths"] += 1
                break
            assert game_map.player.health >= 1, "player at 0 health but the game goes on"
            for c in game_map.creatures:
                if c.health > health_before.get(id(c), c.health):
                    assert c.health == health_before[id(c)] + 1, f"{c.name} healed more than 1"
                    totals["heals"] += 1
            check_consistency(game_map)
    print(f"OK random games: {games} games, " + ", ".join(f"{v} {k}" for k, v in totals.items()))


# 3. real game

def run_real_game(seconds=1.5):
    # press 5 (wait) every 50 ms, then close the window
    pygame.time.set_timer(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_KP5), 50)
    pygame.time.set_timer(pygame.event.Event(pygame.QUIT), int(seconds * 1000), 1)
    os.chdir(REPO)
    try:
        runpy.run_path(os.path.join(REPO, "myroguelike.py"), run_name="__main__")
    except SystemExit:
        pass    # quit_app() exits the program, which is what should happen
    print("OK real game: started, played and quit")


check_healing()
play_random_games()
run_real_game()     # last, because quitting the game shuts pygame down
print("All checks passed.")
