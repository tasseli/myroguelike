# loop_utils.py

import sys
import random
from keyboard import read_moves, read_q_only
from map import OPEN_SPACE, WALL, LOG_ROWS, find_creature_at

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

def handle_events(pygame, game_map, game_state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("", pygame)
        if event.type == pygame.KEYDOWN:
            outcome, direction = read_moves(event.key, pygame)
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
                x, y =game_map.player.get_position()
                new_position = [x + direction[0], y + direction[1]]
                # move creature_0, the player
                if game_map.move_to(0, new_position): # 0 refers to the player ## so if player moved, pass the changed new position and work with it
                    check_deaths(game_map, False)       # check if player killed anyone
                if check_deaths(game_map, True):        # have all creatures move and check if they killed anyone
                    game_state["GAME_ON"] = False
                    return                              # ignore any further keys pressed in the same frame
                # a turn has passed: everyone still alive heals a little
                for creature in game_map.creatures:
                    creature.heal_slowly()

def handle_quit_key(pygame):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("event.type == quit", pygame)
        if event.type == pygame.KEYDOWN:
            outcome = read_q_only(event.key, pygame)
            if outcome == "q":
                quit_app("q or x pressed", pygame)
