# look.py
# The look command (l): a cursor that selects visible creatures and describes them.

import math
from draw import VIEW_RADIUS

# Moves between two tiles; diagonal steps are allowed, so it's the larger of the two distances
def steps_between(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

# The creatures the player can see: the player first, then the others from nearest to farthest.
# Uses the same distance check as the fog of war in draw.py.
def visible_creatures(game_map):
    p_x, p_y = game_map.player.get_position()
    seen = []
    for creature in game_map.creatures[1:]:
        x, y = creature.get_position()
        if (x - p_x)**2 + (y - p_y)**2 < VIEW_RADIUS * VIEW_RADIUS:
            seen.append(creature)
    seen.sort(key=lambda c: (c.position[0] - p_x)**2 + (c.position[1] - p_y)**2)
    return [game_map.player] + seen

# Where the cursor starts: the nearest visible monster, or the player if none is visible
def first_look_target(game_map):
    seen = visible_creatures(game_map)
    if len(seen) > 1:
        return seen[1]
    return seen[0]

# From the current creature, find the next one in direction (dx, dy).
# Only creatures within 45 degrees of the direction count. Of those, the one with the
# smallest "distance along the direction + 2 x distance sideways" is chosen, so that
# creatures straight in that direction are preferred over nearer ones off to the side.
# Return None if there is no creature in that direction.
def next_in_direction(current, candidates, direction):
    c_x, c_y = current.get_position()
    length = math.hypot(direction[0], direction[1])
    u_x, u_y = direction[0] / length, direction[1] / length
    best, best_score = None, None
    for creature in candidates:
        if creature is current:
            continue
        v_x, v_y = creature.position[0] - c_x, creature.position[1] - c_y
        along = v_x * u_x + v_y * u_y
        sideways = abs(v_x * u_y - v_y * u_x)
        if along <= 0 or sideways > along:
            continue
        score = along + 2 * sideways
        if best is None or score < best_score:
            best, best_score = creature, score
    return best

def steps_text(steps):
    return str(steps) + (" step" if steps == 1 else " steps")

DIRECTION_NAMES = {(1, 0): "right", (1, 1): "down-right", (0, 1): "down", (-1, 1): "down-left",
                   (-1, 0): "left", (-1, -1): "up-left", (0, -1): "up", (1, -1): "up-right"}

# The direction from one tile to another, as the nearest of the 8 directions, e.g. "up-left"
def direction_name(start, end):
    v_x, v_y = end[0] - start[0], end[1] - start[1]
    nearest = max(DIRECTION_NAMES, key=lambda d: (v_x * d[0] + v_y * d[1]) / math.hypot(d[0], d[1]))
    return DIRECTION_NAMES[nearest]

# How a creature's target is called: "you", or e.g. "the orc 3 steps up-left of it"
def target_text(creature):
    target = creature.target
    if target.is_player:
        return "you"
    steps = steps_between(creature.get_position(), target.get_position())
    return target.called() + " " + steps_text(steps) + " " + direction_name(creature.position, target.position) + " of it"

# What a creature is doing, for the look description
def doing(creature, game_map):
    if creature.mood == "friend" and creature.target is not None:
        if game_map.threats_to(creature.target):
            return "It is defending " + target_text(creature) + "."
        if creature.target.is_player:
            return "It is your friend."
        return "It is a friend of " + target_text(creature) + "."
    if creature.mood == "toward" and creature.target is not None:
        return "It is chasing " + target_text(creature) + "."
    if creature.mood == "flee" and creature.target is not None:
        return "It is fleeing from " + target_text(creature) + "."
    if creature.mood == "run right":
        return "It is running to the right."
    return "It is wandering around."

# Two log lines describing the creature
def describe(creature, game_map):
    health = "Health " + str(max(creature.health, 0)) + "/" + str(creature.health_max) + "."   # a dead player: 0
    if creature.is_player:
        return ["Looking at: you (@).", health]
    steps = steps_between(creature.get_position(), game_map.player.get_position())
    article = "an" if creature.name[0] in "aeiou" else "a"
    where = steps_text(steps) + " away"
    return ["Looking at: " + article + " " + creature.name + " (" + creature.sign + "), " + where + ".",
            health + " " + doing(creature, game_map)]
