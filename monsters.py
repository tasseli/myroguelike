# monsters.py
# How creatures act on their turn (moods, pathfinding, fleeing, friends), and how a game turn is played.

import random
from map import OPEN_SPACE, WALL, CLOSE_STEPS, find_creature_at
from creatures import CHASE, WANDER, FLEE, FRIEND, RUN_RIGHT

# The 8 directions in order around a circle, so neighbours in the list are 45 degrees apart
DIRECTIONS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

# A chaser's step toward its goal along the shortest walkable way (around walls, e.g. through the
# corridor). Of the neighbouring tiles, in this order of preference:
# 1. a tile closer to the goal by walking that is free, or holds a creature it attacks (such as the goal)
# 2. a free tile just as close (a step sideways, to get around creatures in the way)
# 3. a closer tile with a creature it won't attack (not the player): the two swap places, so that
#    creatures can pass each other in the narrow corridor instead of getting stuck head-on.
#    Not with one chasing the same goal, though: that one is going the same way and moves on its own
#    turn; swapping with it would only make the two swap back and forth without getting anywhere.
# Returns where to move (after a swap: where it now stands). With no such tile, it stays put.
def path_step(map, creature, goal):
    distances = map.distances_to(goal)
    c_x, c_y = creature.get_position()
    here = distances.get((c_x, c_y))
    if here is None:
        return [c_x, c_y]
    closer, sideways, swaps = [], [], []
    for dx, dy in DIRECTIONS:
        tile = (c_x + dx, c_y + dy)
        steps = distances.get(tile)
        if steps is None or steps > here:
            continue
        sign = map.get_sign(tile[0], tile[1])
        if sign == OPEN_SPACE:
            (closer if steps < here else sideways).append((steps, tile))
        elif steps < here:
            blocker = map.creatures[find_creature_at(map.creatures, tile[0], tile[1])]
            if map.can_attack(creature, blocker):
                closer.append((steps, tile))
            elif blocker is not map.player and not (blocker.mood == CHASE and blocker.target is goal):
                swaps.append((steps, blocker))
    if closer or sideways:
        options = closer or sideways
        random.shuffle(options)     # equally close tiles: pick any
        options.sort(key=lambda option: option[0])
        return list(options[0][1])
    if swaps:
        swaps.sort(key=lambda option: option[0])
        map.swap_places(creature, swaps[0][1])
    return creature.get_position()

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

def steps_apart(a, b):
    return max(abs(a.position[0] - b.position[0]), abs(a.position[1] - b.position[1]))

# A friendly creature's move:
# 1. if creatures chasing its friend are close to the friend, or creatures chasing itself are close to
#    itself, go for the nearest of them (and attack it when next to it)
# 2. otherwise, if it's farther than CLOSE_STEPS from its friend, walk back toward the friend
# 3. otherwise move around randomly, or stay, without leaving the friend's close area
def friend_step(map, creature):
    friend = creature.target
    threats = map.threats_to(friend) + map.threats_to(creature)
    if threats:
        threat = min(threats, key=lambda t: steps_apart(creature, t))
        return path_step(map, creature, threat)
    if steps_apart(creature, friend) > CLOSE_STEPS:
        return path_step(map, creature, friend)
    c_x, c_y = creature.get_position()
    f_x, f_y = friend.get_position()
    options = [[c_x, c_y]]
    for dx, dy in DIRECTIONS:
        x, y = c_x + dx, c_y + dy
        if map.get_sign(x, y) == OPEN_SPACE and max(abs(x - f_x), abs(y - f_y)) <= CLOSE_STEPS:
            options.append([x, y])
    return random.choice(options)

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
        if creature.mood == FLEE and (creature.healed_enough_to_stop_fleeing() or not creature.target.alive):
            # healed enough (kobolds: full health, golems: half), or the one it fled from is dead:
            # stop fleeing, and wander or go back to the earlier mood
            creature.stop_fleeing()
        if creature.mood == FRIEND and not creature.target.alive:
            # its friend is dead: wander
            creature.mood = WANDER
            creature.target = None
        if creature.mood == CHASE:
            if creature.target.alive == False:
                creature.mood = WANDER
                creature.target = None
            else:
                new_position = path_step(map, creature, creature.target)
        if creature.mood == WANDER:
            new_position = creature.move_random()
        elif creature.mood == RUN_RIGHT:
            new_position = creature.move_right()
            # a wall ahead: running right can't go on, so start wandering from the next turn
            if map.get_sign(new_position[0], new_position[1]) == WALL:
                creature.mood = WANDER
        elif creature.mood == FLEE:
            new_position = flee_step(map, creature)
        elif creature.mood == FRIEND:
            new_position = friend_step(map, creature)
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
# then everyone still alive heals a little. Messages are added to game_map.messages, and to the
# game's history. Return True if the player died.
def play_turn(game_map, direction):
    first_new_message = len(game_map.messages)
    x, y = game_map.player.get_position()
    new_position = [x + direction[0], y + direction[1]]
    # move creature_0, the player
    if game_map.move_to(0, new_position):
        check_deaths(game_map, False)       # check if player killed anyone
    player_died = check_deaths(game_map, True)  # have all creatures move and check if they killed anyone
    if not player_died:
        for creature in game_map.creatures:
            creature.heal_slowly()
    game_map.record(game_map.messages[first_new_message:])
    return player_died

# Return a creature standing next to the player (in any of the 8 directions), or None.
# The player's friends don't count.
def creature_next_to_player(game_map):
    p_x, p_y = game_map.player.get_position()
    for creature in game_map.creatures[1:]:
        if creature.is_friend_of(game_map.player):
            continue
        x, y = creature.get_position()
        if max(abs(x - p_x), abs(y - p_y)) == 1:
            return creature
    return None
