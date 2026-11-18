# loop_utils.py

import sys
import random
from keyboard import read_moves, read_death_screen_key, read_digit
from map import OPEN_SPACE, WALL, LOG_ROWS, find_creature_at
from help_texts import COMMAND_LINES, HELP_LINES
from look import visible_creatures, first_look_target, next_in_direction, describe

# The 8 directions in order around a circle, so neighbours in the list are 45 degrees apart
DIRECTIONS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

def quit_app(reason, pygame):
    print(reason)
    pygame.quit()
    sys.exit()

# A chaser's straight step toward its target may be blocked by a wall, or by a creature it won't attack.
# Then try the two directions next to the straight one, the one closer to the target first,
# and return the first open one. If both are blocked too, return the straight step (which then does nothing).
def step_around_blocker(map, creature, new_position):
    x, y = new_position
    sign = map.get_sign(x, y)
    if sign == OPEN_SPACE:
        return new_position
    if sign != WALL:
        blocker = map.creatures[find_creature_at(map.creatures, x, y)]
        if map.can_attack(creature, blocker):
            return new_position
    c_x, c_y = creature.get_position()
    t_x, t_y = creature.target.get_position()
    straight = DIRECTIONS.index((x - c_x, y - c_y))
    options = []
    for turn in (-1, 1):
        dx, dy = DIRECTIONS[(straight + turn) % len(DIRECTIONS)]
        options.append([c_x + dx, c_y + dy])
    random.shuffle(options)     # if both are equally close, pick either
    options.sort(key=lambda p: max(abs(p[0] - t_x), abs(p[1] - t_y)))
    for option in options:
        if map.get_sign(option[0], option[1]) == OPEN_SPACE:
            return option
    return new_position

# A fleeing creature steps to the free neighbouring tile farthest from the one it flees from.
# If no free tile is farther away than where it stands, it stays put.
def flee_step(map, creature):
    c_x, c_y = creature.get_position()
    t_x, t_y = creature.target.get_position()
    def distance(tile):
        return (tile[0] - t_x)**2 + (tile[1] - t_y)**2
    best = [c_x, c_y]
    options = [[c_x + dx, c_y + dy] for dx, dy in DIRECTIONS]
    random.shuffle(options)     # equally far tiles: pick any
    for option in options:
        if map.get_sign(option[0], option[1]) == OPEN_SPACE and distance(option) > distance(best):
            best = option
    return best

#   An idea for solving moving a whole array of creatures: implement calling each creature's type of movement by their mood.
def move_moodily(map, creature_i):
    creatures = map.creatures
    creature = creatures[creature_i]
    new_position = creature.get_position()
    death_note = creature.check_death()
    # handle possible creature index of a neighboring death. -1 stands for "no creature killed", otherwise pass the index of the creature to later kill in calling function.
    creature_index = -1
    neighbor_death_note = ""
    if death_note == "":
        if creature.mood == "flee" and (creature.health >= creature.health_max or not creature.target.alive):
            # back at full health, or the one it fled from is dead: stop fleeing and wander
            creature.mood = "ambulate"
            creature.target = None
        if creature.mood == "toward":
            if creature.target.alive == False:
                creature.mood = "ambulate"
            else:
                new_position = creature.move_toward(creature.target)
                new_position = step_around_blocker(map, creature, new_position)
        if creature.mood == "ambulate":
            new_position = creature.move_random()
        elif creature.mood == "run right":
            new_position = creature.move_right()
            # a wall ahead: running right can't go on, so start wandering from the next turn
            if map.get_sign(new_position[0], new_position[1]) == WALL:
                creature.mood = "ambulate"
        elif creature.mood == "flee":
            new_position = flee_step(map, creature)
        map.move_to(creature_i, new_position)
        #I need to check here if the hit creature died, and return the data if they did
        neighbor_death_note, creature_index = map.check_death_for_coords(new_position[0], new_position[1])
    return death_note, neighbor_death_note, creature_index

# Check every creature for death and remove the dead from the map.
# If other_creatures_move is True, the non-player creatures take their turn first.
# Death notes are added to game_map.messages. Return True if the player died.
def check_deaths(game_map, other_creatures_move):
    dying = []
    player_died = False

    def mark_dead(i, death_note):
        nonlocal player_died
        if i == 0:
            player_died = True
        elif i not in dying:
            dying.append(i)
            game_map.creatures[i].alive = False
            game_map.messages.append(death_note)

    if other_creatures_move:
        for i in range(1, len(game_map.creatures)):                     # don't move the player in a loop
            death_note, neighbor_death_note, neighbor_creature_index = move_moodily(game_map, i)
            if neighbor_death_note != "":
                if neighbor_creature_index == 0:
                    game_map.killed_by = game_map.creatures[i].name
                mark_dead(neighbor_creature_index, neighbor_death_note)
            if death_note != "":
                mark_dead(i, death_note)
            if player_died:
                break
    else:
        for i in range(0, len(game_map.creatures)):
            death_note = game_map.creatures[i].check_death()
            if death_note != "":
                mark_dead(i, death_note)

    # remove from the highest index down, so removing one doesn't shift the indexes of the rest
    for i in sorted(dying, reverse=True):
        death_location = game_map.creatures[i].get_position()
        game_map.my_map[death_location[0]][death_location[1]] = OPEN_SPACE
        game_map.creatures.pop(i)
    return player_died

# One game turn: the player moves (or stays, with direction (0, 0)), then the other creatures move,
# then everyone still alive heals a little. Messages are added to game_map.messages.
# Return True if the player died.
def play_turn(game_map, direction):
    x, y = game_map.player.get_position()
    new_position = [x + direction[0], y + direction[1]]
    # move creature_0, the player
    if game_map.move_to(0, new_position):
        check_deaths(game_map, False)       # check if player killed anyone
    if check_deaths(game_map, True):        # have all creatures move and check if they killed anyone
        return True
    for creature in game_map.creatures:
        creature.heal_slowly()
    return False

# Return a creature standing next to the player (in any of the 8 directions), or None
def creature_next_to_player(game_map):
    p_x, p_y = game_map.player.get_position()
    for creature in game_map.creatures[1:]:
        x, y = creature.get_position()
        if max(abs(x - p_x), abs(y - p_y)) == 1:
            return creature
    return None

def turns_text(turns):
    return str(turns) + (" turn" if turns == 1 else " turns")

# Waiting plays the turns a few frames apart, so each turn can be seen, and speeds up as it goes on.
# The game draws 30 frames a second. Every wait starts with WAIT_START_FRAMES between turns
# (about 3 turns a second); each later gap is WAIT_SPEEDUP times shorter, down to WAIT_MIN_FRAMES.
WAIT_START_FRAMES = 10
WAIT_SPEEDUP = 1.1
WAIT_MIN_FRAMES = 1

# How many frames to wait before playing the given turn of a wait (turn 1 is the first)
def wait_frames_before_turn(turn_number):
    if turn_number <= 2:
        return WAIT_START_FRAMES
    return max(WAIT_MIN_FRAMES, round(WAIT_START_FRAMES / WAIT_SPEEDUP ** (turn_number - 2)))

# Start waiting up to the given number of turns. game_state["waiting"] keeps track of it;
# None means not waiting. Waiting doesn't start if a creature is already next to the player.
def start_waiting(game_map, game_state, turns):
    game_map.log_offset = 0
    nearby = creature_next_to_player(game_map)
    if nearby is not None:
        game_map.messages = ["You can't wait with " + nearby.called() + " next to you."]
        return
    # frames starts one short, so the first turn is played on the very next frame.
    # stop_at_full_health: waiting started below full health, so stop when full health is reached;
    # waiting started at full health goes on as long as asked.
    player = game_map.player
    game_state["waiting"] = {"turns": turns, "waited": 0, "frames": wait_frames_before_turn(1) - 1, "log": [],
                             "stop_at_full_health": player.health < player.health_max}
    game_map.messages = ["Waiting: 0/" + str(turns) + " turns"]

# End waiting: the log gets the summary first, then the messages of all the waited turns
def finish_waiting(game_map, game_state, summary):
    game_map.messages = [summary] + game_state["waiting"]["log"]
    game_map.log_offset = 0
    game_state["waiting"] = None

# Called once a frame while waiting. When enough frames have passed, play the next turn; stop when
# all turns are waited, or a creature comes next to the player, or the player reaches full health
# (if waiting started below it), or the player dies.
def continue_waiting(game_map, game_state):
    waiting = game_state["waiting"]
    waiting["frames"] += 1
    if waiting["frames"] < wait_frames_before_turn(waiting["waited"] + 1):
        return
    waiting["frames"] = 0
    waiting["waited"] += 1
    game_map.messages = []
    if play_turn(game_map, (0, 0)):
        game_state["waiting"] = None
        game_state["GAME_ON"] = False
        return
    turn_messages = game_map.messages
    waiting["log"] += turn_messages
    waited = turns_text(waiting["waited"])
    nearby = creature_next_to_player(game_map)
    player = game_map.player
    if nearby is not None:
        finish_waiting(game_map, game_state, "You stop waiting after " + waited + ": " + nearby.called() + " is next to you.")
    elif waiting["stop_at_full_health"] and player.health >= player.health_max:
        finish_waiting(game_map, game_state, "You stop waiting after " + waited + ": you are at full health.")
    elif waiting["waited"] >= waiting["turns"]:
        finish_waiting(game_map, game_state, "You wait " + waited + ".")
    else:
        # show the progress and this turn's messages
        game_map.messages = ["Waiting: " + str(waiting["waited"]) + "/" + str(waiting["turns"]) + " turns"] + turn_messages
        game_map.log_offset = 0

WAIT_PROMPT = "Wait how many turns? "
WAIT_HELP = "   (Enter: wait, Esc: cancel)"

# While the wait prompt is open, keys type the number of turns instead of moving.
# game_state["wait_input"] holds the digits typed so far; None means the prompt is closed.
def handle_wait_input(event_key, pygame, game_map, game_state):
    typed = game_state["wait_input"]
    digit = read_digit(event_key, pygame)
    if digit is not None and len(typed) < 3:
        typed += digit
    elif event_key == pygame.K_BACKSPACE:
        typed = typed[:-1]
    elif event_key == pygame.K_ESCAPE:
        game_state["wait_input"] = None
        game_map.messages = ["You decide not to wait."]
        return
    elif event_key == pygame.K_RETURN or event_key == pygame.K_KP_ENTER:
        game_state["wait_input"] = None
        if typed == "" or int(typed) == 0:
            game_map.messages = ["You decide not to wait."]
        else:
            start_waiting(game_map, game_state, int(typed))
        return
    game_state["wait_input"] = typed
    game_map.messages = [WAIT_PROMPT + typed + "_" + WAIT_HELP]

# Look mode: game_state["look_target"] is the selected creature; None means not looking.
# The log shows the description while looking, and what it showed before afterwards.
def start_looking(game_map, game_state):
    game_state["look_saved_log"] = (game_map.messages, game_map.log_offset)
    target = first_look_target(game_map)
    game_state["look_target"] = target
    game_map.messages = describe(target, game_map)
    game_map.log_offset = 0

def stop_looking(game_map, game_state):
    game_map.messages, game_map.log_offset = game_state["look_saved_log"]
    game_state["look_target"] = None

# While looking, direction keys jump to the next visible creature in that direction; no turns pass
def handle_look_input(event_key, typed_char, pygame, game_map, game_state):
    if event_key == pygame.K_l or event_key == pygame.K_ESCAPE:
        stop_looking(game_map, game_state)
        return
    outcome, direction = read_moves(event_key, pygame, typed_char)
    if outcome == "q":
        quit_app("", pygame)
    elif outcome == "m":
        next_target = next_in_direction(game_state["look_target"], visible_creatures(game_map), direction)
        if next_target is not None:
            game_state["look_target"] = next_target
            game_map.messages = describe(next_target, game_map)

# Called once a frame: handle the keys pressed, and play the next waited turn when it's time
def handle_events(pygame, game_map, game_state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("", pygame)
        if event.type == pygame.KEYDOWN and game_state.get("waiting") is not None:
            # any key stops waiting
            finish_waiting(game_map, game_state, "You stop waiting after " + turns_text(game_state["waiting"]["waited"]) + ".")
        elif event.type == pygame.KEYDOWN and game_state.get("look_target") is not None:
            handle_look_input(event.key, getattr(event, "unicode", ""), pygame, game_map, game_state)
        elif event.type == pygame.KEYDOWN and game_state.get("wait_input") is not None:
            handle_wait_input(event.key, pygame, game_map, game_state)
        elif event.type == pygame.KEYDOWN:
            outcome, direction = read_moves(event.key, pygame, getattr(event, "unicode", ""))
            if outcome == "q":
                quit_app("", pygame)
            elif outcome == "o":
#               An unhandled key was pressed
                pass
            elif outcome == "more":
                # show the next rows of this turn's messages, back to the first after the last; no turn passes
                if len(game_map.messages) > LOG_ROWS:
                    game_map.log_offset += LOG_ROWS
                    if game_map.log_offset >= len(game_map.messages):
                        game_map.log_offset = 0
            elif outcome == "m" or outcome == "s": # if moving happened
#               Move key or stand still key
                game_map.messages = []
                game_map.log_offset = 0
                if play_turn(game_map, direction):
                    game_state["GAME_ON"] = False
                    return                              # ignore any further keys pressed in the same frame
            elif outcome == "commands" or outcome == "help":
                # show the commands (?) or the help (h) in the log, m pages through it; no turn passes
                game_map.messages = list(COMMAND_LINES if outcome == "commands" else HELP_LINES)
                game_map.log_offset = 0
            elif outcome == "look":
                start_looking(game_map, game_state)
            elif outcome == "wait":
                # open the prompt for how many turns to wait; no turn passes yet
                game_state["wait_input"] = ""
                game_map.log_offset = 0
                game_map.messages = [WAIT_PROMPT + "_" + WAIT_HELP]
    if game_state.get("waiting") is not None:
        continue_waiting(game_map, game_state)

# Return "restart" if the player wants to play again; quitting exits the program.
def handle_death_screen_keys(pygame):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("event.type == quit", pygame)
        if event.type == pygame.KEYDOWN:
            outcome = read_death_screen_key(event.key, pygame)
            if outcome == "q":
                quit_app("q or x pressed", pygame)
            elif outcome == "r":
                return "restart"
    return None
