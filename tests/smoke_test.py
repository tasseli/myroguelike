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

def check_hit_message_texts():
    from creatures import Uruk
    player, orc, orc2, uruk = Player([1, 1]), Orc([1, 1]), Orc([1, 1]), Uruk([1, 1])
    orc.health = orc2.health = 5
    assert player.hit(orc) == ["You hit the orc for 4. It has 1 health left."], player.hit
    assert uruk.hit(player) == ["The uruk hits you for 4. You have 8 health left."]
    assert orc2.hit(orc) == ["The orc hits another orc for 3."], "killing hit should leave out health"
    assert orc.check_death() == "The orc dies!"
    print("OK rule checks: hit and death messages")

def check_run_right_stops_at_wall():
    random.seed(0)
    game_map = m.Map()
    runner = next(c for c in game_map.creatures if c.mood == "run right")
    right_wall_x = game_map.room[2]     # the room's right edge is exclusive: that column is wall
    for turn in range(m.MAP_WIDTH):
        loop_utils.move_moodily(game_map, game_map.creatures.index(runner))
        if runner.mood != "run right":
            break
    assert runner.mood == "ambulate", "the runner never stopped running right"
    assert runner.position[0] == right_wall_x - 1, f"runner stopped at x={runner.position[0]}, not by the wall"
    print("OK rule checks: the 'run right' orc starts wandering at a wall")

# A map with only the player on it, standing in the middle of the room
def empty_room_map():
    random.seed(0)
    game_map = m.Map()
    for c in game_map.creatures:
        game_map.my_map[c.position[0]][c.position[1]] = m.OPEN_SPACE
    game_map.creatures = []
    left, top, right, bottom = game_map.room
    place(game_map, game_map.player, (left + right) // 2, (top + bottom) // 2)
    return game_map

def place(game_map, creature, x, y):
    creature.position = [x, y]
    game_map.my_map[x][y] = creature.sign
    game_map.creatures.append(creature)

def check_step_around():
    from creatures import Kobold, Gnoll
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    # kobold three tiles left of the player, gnoll right in its way
    kobold = Kobold([0, 0], "toward", game_map.player)
    gnoll = Gnoll([0, 0])
    place(game_map, kobold, p_x - 3, p_y)
    place(game_map, gnoll, p_x - 2, p_y)
    gnoll_health = gnoll.health
    loop_utils.move_moodily(game_map, game_map.creatures.index(kobold))
    k_x, k_y = kobold.position
    assert k_x == p_x - 2 and abs(k_y - p_y) == 1, f"kobold went to {kobold.position}, not around the gnoll"
    assert gnoll.health == gnoll_health, "kobold hit the gnoll"
    print("OK rule checks: a chaser steps around a creature in its way")

def press(game_map, key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
    loop_utils.handle_events(pygame, game_map, {"GAME_ON": True})

def check_more_key():
    random.seed(0)
    game_map = m.Map()
    messages = ["message " + str(i) for i in range(1, 10)]     # 9 messages: pages 1-4, 5-8, 9
    game_map.messages = list(messages)
    positions = [list(c.position) for c in game_map.creatures]
    offsets = []
    for i in range(4):
        press(game_map, pygame.K_m)
        offsets.append(game_map.log_offset)
    assert offsets == [4, 8, 0, 4], f"More went through offsets {offsets}"
    assert game_map.messages == messages, "More changed the messages"
    assert [list(c.position) for c in game_map.creatures] == positions, "More used up a turn"

    # every page draws without errors
    import draw
    font = pygame.font.SysFont(None, 22)
    for offset in (0, 4, 8):
        draw.render_message_log(messages, offset, pygame, pygame.display.get_surface(), font)

    # a new turn starts the log from its first row
    press(game_map, pygame.K_KP5)
    assert game_map.log_offset == 0, "a new turn didn't reset the log to the first row"

    # with no more messages than rows, More does nothing
    game_map.messages = ["a", "b", "c", "d"]
    press(game_map, pygame.K_m)
    assert game_map.log_offset == 0, "More moved a log that fits on the screen"
    print("OK rule checks: the More key pages through the log without using a turn")


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

def is_hit_message(message):
    return message.startswith("You hit ") or " hits " in message

def check_hit_messages(messages):
    for message in messages:
        if is_hit_message(message):
            # the player is in every hit, except orcs hitting their target orc
            assert message.startswith("You hit ") or " hits you " in message \
                or message.startswith("The orc hits another orc "), "attack against the rules: " + message

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
            totals["hits"] += sum(is_hit_message(s) for s in game_map.messages)
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

def run_real_game(seconds=3):
    # count the games started: myroguelike.py creates a new Map for each game
    games_started = [0]
    original_map = m.Map
    def counting_map():
        games_started[0] += 1
        return original_map()
    m.Map = counting_map

    # after each drawn frame, press 5 (wait); every 10th frame press r (play again) instead;
    # close the window after the given time (the game runs at 30 frames per second)
    frames = [0]
    original_flip = pygame.display.flip
    def flip_and_press_keys():
        original_flip()
        frames[0] += 1
        if frames[0] >= seconds * 30:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif frames[0] % 10 == 0:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
        else:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_KP5))
    pygame.display.flip = flip_and_press_keys

    random.seed(1)
    os.chdir(REPO)
    try:
        runpy.run_path(os.path.join(REPO, "myroguelike.py"), run_name="__main__")
    except SystemExit:
        pass    # quit_app() exits the program, which is what should happen
    m.Map = original_map
    pygame.display.flip = original_flip
    assert games_started[0] >= 2, f"only {games_started[0]} game started; pressing r on the death screen didn't restart"
    print(f"OK real game: played {games_started[0]} games in a row (r restarts) and quit")


check_healing()
check_hit_message_texts()
check_run_right_stops_at_wall()
check_more_key()
check_step_around()
play_random_games()
run_real_game()     # last, because quitting the game shuts pygame down
print("All checks passed.")
