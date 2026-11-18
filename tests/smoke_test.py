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

# Press keys one after another; game_state is kept between them (e.g. an open wait prompt)
def press(game_map, *keys, game_state=None):
    if game_state is None:
        game_state = {"GAME_ON": True}
    for key in keys:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
        loop_utils.handle_events(pygame, game_map, game_state)

def check_help():
    from help_texts import COMMAND_LINES, HELP_LINES, KEY_HINTS, WAIT_KEY_HINTS, LOOK_KEY_HINTS, DEATH_KEY_HINTS
    game_map = empty_room_map()
    turns_until_heal = game_map.player.turns_until_heal

    # '?' is recognised by the character typed (here Shift + slash, as on a US keyboard)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SLASH, unicode="?"))
    loop_utils.handle_events(pygame, game_map, {"GAME_ON": True})
    assert game_map.messages == COMMAND_LINES, "? didn't show the commands"
    press(game_map, pygame.K_m)
    assert game_map.log_offset == 4, "m didn't page the commands"

    press(game_map, pygame.K_h)
    assert game_map.messages == HELP_LINES and game_map.log_offset == 0, "h didn't show the help from the start"
    press(game_map, pygame.K_m)
    assert game_map.log_offset == 4, "m didn't page the help"
    assert game_map.player.turns_until_heal == turns_until_heal, "showing the help used up a turn"

    # ? lists only the commands for any turn; how things work (healing, attacking, r after dying) is in h
    for topic in ("heal", "attack", "r plays again"):
        assert not any(topic in line.lower() for line in COMMAND_LINES), f"'{topic}' belongs in h, not ?"
        assert any(topic in line.lower() for line in HELP_LINES), f"h doesn't mention '{topic}'"

    # the texts fit: a line plus its row number must end before the More indicator
    for line in COMMAND_LINES + HELP_LINES:
        assert len(line) <= 52, f"help line too long ({len(line)} characters): {line}"
    for hints in (KEY_HINTS, WAIT_KEY_HINTS, LOOK_KEY_HINTS, DEATH_KEY_HINTS):
        assert len(hints) <= m.MAP_WIDTH - 2, f"key hints don't fit on one row ({len(hints)} characters)"
    print("OK rule checks: ? shows the commands, h the help, m pages them, no turn used")

def check_look():
    from creatures import Kobold, Gnoll, Golem
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    kobold = Kobold([0, 0], "toward", game_map.player)
    gnoll = Gnoll([0, 0])
    golem = Golem([0, 0])
    place(game_map, kobold, p_x + 3, p_y)       # nearest
    place(game_map, gnoll, p_x, p_y - 4)
    place(game_map, golem, min(p_x + 16, m.MAP_WIDTH - 2), p_y)    # too far away to see
    game_map.messages = ["before looking"]
    state = {"GAME_ON": True}
    turns_until_heal = game_map.player.turns_until_heal

    press(game_map, pygame.K_l, game_state=state)
    assert state["look_target"] is kobold, "look didn't start on the nearest monster"
    assert game_map.messages == ["Looking at: a kobold (k), 3 steps away.",
                                 "Health " + str(kobold.health) + "/" + str(kobold.health_max) + ". It is chasing you."], game_map.messages
    press(game_map, pygame.K_RIGHT, game_state=state)
    assert state["look_target"] is kobold, "jumped to a creature the player can't see"
    press(game_map, pygame.K_LEFT, game_state=state)
    assert state["look_target"] is game_map.player and game_map.messages[0] == "Looking at: you (@)."
    press(game_map, pygame.K_KP8, game_state=state)
    assert state["look_target"] is gnoll and "wandering" in game_map.messages[1], game_map.messages
    press(game_map, pygame.K_KP3, game_state=state)     # down-right from the gnoll: the kobold
    assert state["look_target"] is kobold

    press(game_map, pygame.K_ESCAPE, game_state=state)
    assert state["look_target"] is None and game_map.messages == ["before looking"], "log not put back"
    assert game_map.player.turns_until_heal == turns_until_heal, "looking used up a turn"
    assert kobold.position == [p_x + 3, p_y], "creatures moved while looking"

    # with no monster in sight, looking starts on the player; l also stops looking
    lonely = empty_room_map()
    press(lonely, pygame.K_l, game_state=state)
    assert state["look_target"] is lonely.player
    press(lonely, pygame.K_l, game_state=state)
    assert state["look_target"] is None
    print("OK rule checks: l looks at visible creatures, direction keys jump between them")

def check_mood_colors():
    import draw
    from creatures import Kobold, Gnoll
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    chaser = Kobold([0, 0], "toward", game_map.player)
    wanderer = Gnoll([0, 0])
    orc_chasing_orc = Orc([0, 0], "toward", wanderer)
    place(game_map, chaser, p_x + 2, p_y)
    place(game_map, wanderer, p_x - 2, p_y)
    place(game_map, orc_chasing_orc, p_x, p_y + 2)
    assert draw.creature_color(chaser, game_map.player) == m.RED
    assert draw.creature_color(wanderer, game_map.player) == m.DARK_GRAY
    assert draw.creature_color(orc_chasing_orc, game_map.player) == m.DARK_GRAY
    assert draw.creature_color(game_map.player, game_map.player) == m.DARK_GRAY

    # on screen: the corner pixel of each tile has the tile's background color
    screen = pygame.display.set_mode((m.MAP_WIDTH * m.TILE_SIZE, m.MAP_HEIGHT * m.TILE_SIZE))
    draw.render_map(game_map, pygame, screen, pygame.font.SysFont(None, 22), game_map.player)
    def tile_color(c):
        return tuple(screen.get_at((c.position[0] * m.TILE_SIZE, c.position[1] * m.TILE_SIZE)))[:3]
    assert tile_color(chaser) == m.RED, tile_color(chaser)
    assert tile_color(wanderer) == m.DARK_GRAY and tile_color(orc_chasing_orc) == m.DARK_GRAY
    print("OK rule checks: monsters chasing the player are drawn on red, others on grey")

def check_provoke():
    import draw
    from creatures import Kobold, Golem
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    golem = Golem([0, 0])                                   # wandering, tough enough to survive a hit
    chaser = Kobold([0, 0], "toward", game_map.player)
    place(game_map, golem, p_x + 1, p_y)
    place(game_map, chaser, p_x - 1, p_y)

    game_map.messages = []
    game_map.move_to(0, [p_x + 1, p_y])                     # the player hits the golem
    assert golem.mood == "toward" and golem.target is game_map.player, "hit golem didn't start chasing"
    assert draw.creature_color(golem, game_map.player) == m.RED
    assert game_map.messages[-1] == "The golem turns to chase you!", game_map.messages

    game_map.messages = []
    game_map.move_to(0, [p_x - 1, p_y])                     # hitting a chaser changes nothing
    assert chaser.target is game_map.player
    assert not any("turns to chase" in s for s in game_map.messages), game_map.messages
    # a grey monster bumping into the player doesn't hit, but turns to chase the player
    from creatures import Gnoll
    wanderer = Gnoll([0, 0])
    place(game_map, wanderer, p_x, p_y + 1)
    health = game_map.player.health
    game_map.messages = []
    game_map.move_to(game_map.creatures.index(wanderer), [p_x, p_y])
    assert game_map.player.health == health, "a grey monster hit the player"
    assert wanderer.mood == "toward" and wanderer.target is game_map.player
    assert game_map.messages == ["The gnoll turns to chase you!"], game_map.messages
    # now it chases the player, so the next bump is a hit
    game_map.move_to(game_map.creatures.index(wanderer), [p_x, p_y])
    assert game_map.player.health == health - wanderer.damage, "the now red gnoll didn't hit"
    print("OK rule checks: a grey monster hit by or bumping into the player starts chasing instead of hitting")

# Run game frames with no keys pressed, like the game loop does, until waiting ends. Return the frame count.
def run_frames_while_waiting(game_map, game_state):
    frames = 0
    while game_state.get("waiting") is not None and frames < 100000:
        loop_utils.handle_events(pygame, game_map, game_state)
        frames += 1
    return frames

def check_flee():
    import draw
    from look import describe
    from creatures import Kobold
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    kobold = Kobold([0, 0], "toward", game_map.player)
    place(game_map, kobold, p_x + 1, p_y)
    kobold.health = kobold.health_max = 5

    game_map.messages = []
    game_map.move_to(0, [p_x + 1, p_y])         # the player hits it for 4: 1 health left
    assert kobold.health == 1 and kobold.mood == "flee" and kobold.target is game_map.player, \
        f"kobold at {kobold.health} health has mood {kobold.mood}"
    assert game_map.messages[-1] == "The kobold flees from you!", game_map.messages
    assert draw.creature_color(kobold, game_map.player) == m.YELLOW
    assert describe(kobold, game_map)[1].endswith("It is fleeing from you."), describe(kobold, game_map)

    # it moves away from the player every turn
    i = game_map.creatures.index(kobold)
    def squared_distance():
        return (kobold.position[0] - p_x)**2 + (kobold.position[1] - p_y)**2
    for turn in range(3):
        before = squared_distance()
        loop_utils.move_moodily(game_map, i)
        assert squared_distance() > before, f"fleeing kobold didn't get farther: {before} -> {squared_distance()}"
    assert kobold.mood == "flee", "stopped fleeing before full health"

    # back at full health it starts wandering
    kobold.health = kobold.health_max
    loop_utils.move_moodily(game_map, i)
    assert kobold.mood == "ambulate" and kobold.target is None, kobold.mood

    # a kobold left at 2 health flees too
    kobold2 = Kobold([0, 0], "toward", game_map.player)
    place(game_map, kobold2, p_x, p_y + 1)
    kobold2.health = kobold2.health_max = 6
    game_map.move_to(0, [p_x, p_y + 1])
    assert kobold2.health == 2 and kobold2.mood == "flee", f"kobold at 2 health has mood {kobold2.mood}"

    # other monsters don't flee: an orc left at 1 health turns to chase the player instead
    orc = Orc([0, 0])
    place(game_map, orc, p_x - 1, p_y)
    orc.health = 5
    game_map.move_to(0, [p_x - 1, p_y])
    assert orc.health == 1 and orc.mood == "toward" and orc.target is game_map.player, orc.mood
    print("OK rule checks: kobolds at 2 health or less flee (yellow) until healed, then wander")

def check_wait():
    from creatures import Kobold
    gap = loop_utils.wait_frames_before_turn
    start = loop_utils.WAIT_START_FRAMES

    # the pace: starts at WAIT_START_FRAMES between turns, never slows down, gets clearly faster
    gaps = [gap(turn) for turn in range(2, 101)]
    assert gaps[0] == start, gaps[:3]
    assert all(later <= earlier for earlier, later in zip(gaps, gaps[1:])), "waiting slowed down"
    assert gaps[-1] == loop_utils.WAIT_MIN_FRAMES, "long waits never reach full speed"

    # nobody around: wait the full 20 turns and heal 1
    game_map = empty_room_map()
    state = {"GAME_ON": True}
    game_map.player.health = 5
    press(game_map, pygame.K_w, pygame.K_2, pygame.K_KP0, pygame.K_RETURN, game_state=state)
    assert state["wait_input"] is None, "the prompt stayed open"
    # the first turn is played on the same frame as Enter, and shown
    assert game_map.messages[0] == "Waiting: 1/20 turns", game_map.messages
    frames = run_frames_while_waiting(game_map, state)
    expected = sum(gap(turn) for turn in range(2, 21))
    assert frames == expected, f"the other 19 turns took {frames} frames, not {expected}"
    assert frames < 19 * start, "waiting didn't speed up"
    assert game_map.messages[0] == "You wait 20 turns.", game_map.messages

    # the next wait starts at the original pace again: turn 2 comes after WAIT_START_FRAMES frames
    press(game_map, pygame.K_w, pygame.K_5, pygame.K_RETURN, game_state=state)
    for frame in range(start - 1):
        loop_utils.handle_events(pygame, game_map, state)
    assert game_map.messages[0] == "Waiting: 1/5 turns", game_map.messages
    loop_utils.handle_events(pygame, game_map, state)
    assert game_map.messages[0] == "Waiting: 2/5 turns", game_map.messages
    run_frames_while_waiting(game_map, state)
    assert game_map.player.health == 6, "didn't heal while waiting 20 turns"

    # started below full health: stop when full health is reached (1 health short heals in 20 turns)
    full_map = empty_room_map()
    full_state = {"GAME_ON": True}
    full_map.player.health = full_map.player.health_max - 1
    press(full_map, pygame.K_w, pygame.K_5, pygame.K_0, pygame.K_RETURN, game_state=full_state)
    run_frames_while_waiting(full_map, full_state)
    assert full_map.messages[0] == "You stop waiting after 20 turns: you are at full health.", full_map.messages
    # started at full health: wait as long as asked
    press(full_map, pygame.K_w, pygame.K_2, pygame.K_5, pygame.K_RETURN, game_state=full_state)
    run_frames_while_waiting(full_map, full_state)
    assert full_map.messages[0] == "You wait 25 turns.", full_map.messages

    # typing: backspace removes a digit, Esc cancels without using a turn
    press(game_map, pygame.K_w, pygame.K_1, pygame.K_2, pygame.K_BACKSPACE, game_state=state)
    assert state["wait_input"] == "1", state
    turns_until_heal = game_map.player.turns_until_heal
    press(game_map, pygame.K_ESCAPE, game_state=state)
    assert state["wait_input"] is None and game_map.messages == ["You decide not to wait."]
    assert game_map.player.turns_until_heal == turns_until_heal, "cancelling used up a turn"

    # a kobold comes: stop right when it's next to the player, before it can hit
    p_x, p_y = game_map.player.position
    kobold = Kobold([0, 0], "toward", game_map.player)
    place(game_map, kobold, p_x - 5, p_y)
    health = game_map.player.health
    press(game_map, pygame.K_w, pygame.K_5, pygame.K_0, pygame.K_RETURN, game_state=state)
    run_frames_while_waiting(game_map, state)
    assert game_map.messages[0] == "You stop waiting after 4 turns: the kobold is next to you.", game_map.messages
    assert loop_utils.creature_next_to_player(game_map) is kobold
    assert game_map.player.health == health, "the kobold got to hit while the player waited"

    # someone already next to the player: don't wait at all
    kobold_position = list(kobold.position)
    press(game_map, pygame.K_w, pygame.K_9, pygame.K_RETURN, game_state=state)
    assert game_map.messages == ["You can't wait with the kobold next to you."], game_map.messages
    assert kobold.position == kobold_position, "a turn passed although waiting was refused"
    assert state.get("waiting") is None, "waiting started although it was refused"

    # any key stops waiting, and that key does nothing else
    game_map = empty_room_map()
    state = {"GAME_ON": True}
    press(game_map, pygame.K_w, pygame.K_9, pygame.K_9, pygame.K_RETURN, game_state=state)    # turn 1
    for frame in range(gap(2) + gap(3)):                                                      # turns 2 and 3
        loop_utils.handle_events(pygame, game_map, state)
    assert game_map.messages[0] == "Waiting: 3/99 turns", game_map.messages
    position = list(game_map.player.position)
    press(game_map, pygame.K_LEFT, game_state=state)
    assert state["waiting"] is None and game_map.messages[0] == "You stop waiting after 3 turns.", game_map.messages
    assert game_map.player.position == position, "the key that stopped waiting also moved the player"
    assert game_map.player.turns_until_heal == game_map.player.heal_interval - 3, "more turns passed than shown"
    print("OK rule checks: w starts at about 3 turns a second and speeds up, heals, stops when someone comes next or a key is pressed")

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

def check_starting_creatures(game_map):
    kobolds = [c for c in game_map.creatures if c.name == "kobold"]
    hostile = [k for k in kobolds if k.mood == "toward" and k.target is game_map.player]
    wandering = [k for k in kobolds if k.mood == "ambulate"]
    assert len(kobolds) == 4 and len(hostile) == 2 and len(wandering) == 2, \
        f"{len(kobolds)} kobolds: {len(hostile)} hostile, {len(wandering)} wandering"

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
        check_starting_creatures(game_map)
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
check_wait()
check_help()
check_look()
check_mood_colors()
check_provoke()
check_flee()
play_random_games()
run_real_game()     # last, because quitting the game shuts pygame down
print("All checks passed.")
