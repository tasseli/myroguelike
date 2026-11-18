# map.py

from creatures import Player, Orc, Kobold, Uruk, Gnoll, Goblin, Golem
from creatures import CHASE, FLEE, FRIEND, RUN_RIGHT
import random
from collections import deque

# The 8 steps from a tile to its neighbours
NEIGHBOURS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

# Define the dimensions of the map
MAP_WIDTH   = 80
MAP_HEIGHT  = 40
TILE_SIZE   = 16
LOG_ROWS    = 4     # message rows shown under the map

# How far the player can see (if no wall is in the way)
VIEW_RADIUS = 12

# The sizes of the two rooms, picked at random between these, inclusive
ROOM_MIN_WIDTH, ROOM_MAX_WIDTH = 8, 24
ROOM_MIN_HEIGHT, ROOM_MAX_HEIGHT = 6, 16

# How many moves away from the player other creatures start, when the rooms are big enough
MIN_SPAWN_DISTANCE = 8
# How many moves away from the player the near golem starts, when possible
NEAR_GOLEM_SPAWN_DISTANCE = 6
# "Close" for a friendly creature: next to its friend, or next to one of those tiles
CLOSE_STEPS = 2

# Define constants for tile types
OPEN_SPACE  = '.'
WALL        = '#'

# Define colors for tiles
WHITE       = (255, 255, 255)   # 
GRAY        = (128, 128, 128)   # Open space
DARK_GRAY   = (64, 64, 64)      # Wall
BLACK       = (0, 0, 0)         # Text color
RED         = (190, 50, 50)     # Monster chasing the player
YELLOW      = (210, 180, 50)    # Monster fleeing
GREEN       = (70, 170, 70)     # Friendly creature
REMEMBERED_WALL = (96, 96, 96)  # Wall seen before but not in view now
DIM_TEXT    = (70, 70, 70)      # Text color for tiles seen before but not in view now

def find_creature_at(creatures, x, y):
    i = 0
    for creature in creatures:
        if creature.position[0] == x and creature.position[1] == y:
            return i
        i += 1
    return -1

class Map:

    # Fill the map with walls, carve two random sized rooms, one in the left half and one in the right
    # half, and join them with a straight corridor along a row that both rooms share.
    # Return the rooms as (left, top, right, bottom), right and bottom exclusive, and the corridor tiles.
    def generate(self):
        self.my_map = [[WALL for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
        middle = MAP_WIDTH // 2
        # the left room ends before the middle column; neither room touches the map's outer wall
        width1 = random.randint(ROOM_MIN_WIDTH, ROOM_MAX_WIDTH)
        height1 = random.randint(ROOM_MIN_HEIGHT, ROOM_MAX_HEIGHT)
        left1 = random.randint(1, middle - 1 - width1)
        top1 = random.randint(1, MAP_HEIGHT - 1 - height1)
        room1 = (left1, top1, left1 + width1, top1 + height1)
        # the right room starts after the middle column, and shares at least one row with the left room
        width2 = random.randint(ROOM_MIN_WIDTH, ROOM_MAX_WIDTH)
        height2 = random.randint(ROOM_MIN_HEIGHT, ROOM_MAX_HEIGHT)
        left2 = random.randint(middle + 1, MAP_WIDTH - 1 - width2)
        top2 = random.randint(max(1, top1 - height2 + 1), min(MAP_HEIGHT - 1 - height2, room1[3] - 1))
        room2 = (left2, top2, left2 + width2, top2 + height2)
        for left, top, right, bottom in (room1, room2):
            for y in range(top, bottom):
                for x in range(left, right):
                    self.my_map[x][y] = OPEN_SPACE
        # the corridor: on one of the shared rows, from the left room's right wall to the right room's left wall
        corridor_y = random.randint(max(room1[1], room2[1]), min(room1[3], room2[3]) - 1)
        corridor = [[x, corridor_y] for x in range(room1[2], room2[0])]
        for x, y in corridor:
            self.my_map[x][y] = OPEN_SPACE
        return [room1, room2], corridor

    # How many steps each floor tile is from the given creature, walking around walls (creatures don't
    # block here: they move). A dict {(x, y): steps}; tiles that can't be reached aren't in it.
    # The walls never change, so the result for a tile is kept and reused (a few hundred at most).
    def distances_to(self, creature):
        start = tuple(creature.get_position())
        if start not in self.distance_cache:
            if len(self.distance_cache) > 200:
                self.distance_cache = {}
            self.distance_cache[start] = self.walking_distances(start)
        return self.distance_cache[start]

    # Breadth-first search: first the tiles next to start (1 step), then the tiles next to those (2), ...
    def walking_distances(self, start):
        distances = {start: 0}
        todo = deque([start])
        while todo:
            x, y = todo.popleft()
            for dx, dy in NEIGHBOURS:
                tile = (x + dx, y + dy)
                if tile not in distances and self.my_map[tile[0]][tile[1]] != WALL:
                    distances[tile] = distances[(x, y)] + 1
                    todo.append(tile)
        return distances

    # The tiles the player can see from where it stands: within VIEW_RADIUS, with no wall on the straight
    # line from the player to the tile (a wall itself can be seen, but not what's behind it). Creatures
    # don't block the view. A set of (x, y); kept and reused per tile, as the walls never change.
    def visible_tiles(self, viewer):
        start = tuple(viewer.get_position())
        if start not in self.view_cache:
            if len(self.view_cache) > 200:
                self.view_cache = {}
            self.view_cache[start] = self.tiles_in_view(start)
        return self.view_cache[start]

    def tiles_in_view(self, start):
        s_x, s_y = start
        visible = set()
        for x in range(max(s_x - VIEW_RADIUS, 0), min(s_x + VIEW_RADIUS + 1, MAP_WIDTH)):
            for y in range(max(s_y - VIEW_RADIUS, 0), min(s_y + VIEW_RADIUS + 1, MAP_HEIGHT)):
                if (x - s_x)**2 + (y - s_y)**2 < VIEW_RADIUS * VIEW_RADIUS and self.line_is_clear(s_x, s_y, x, y):
                    visible.add((x, y))
        return visible

    # True if no wall stands on the straight line between the two tiles (the ends themselves don't count).
    # The line goes tile by tile, like a line drawn on squared paper (Bresenham's line algorithm).
    def line_is_clear(self, x0, y0, x1, y1):
        d_x, d_y = abs(x1 - x0), -abs(y1 - y0)
        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1
        error = d_x + d_y
        x, y = x0, y0
        while (x, y) != (x1, y1):
            if (x, y) != (x0, y0) and self.my_map[x][y] == WALL:
                return False
            double_error = 2 * error
            if double_error >= d_y:
                error += d_y
                x += step_x
            if double_error <= d_x:
                error += d_x
                y += step_y
        return True

    # The floor tiles in the rooms (not the corridor) that have no creature on them
    def free_room_tiles(self):
        return [[x, y] for left, top, right, bottom in self.rooms
                for x in range(left, right) for y in range(top, bottom)
                if self.my_map[x][y] == OPEN_SPACE]

    # Return the coords of a random free floor tile in a room.
    # With away_from, only tiles at least min_distance moves from that creature are used.
    # If the rooms have no tile that far, the farthest free tiles are used instead.
    def random_free_floor(self, away_from=None, min_distance=0):
        free = self.free_room_tiles()
        if away_from is not None:
            ax, ay = away_from.get_position()
            def moves(tile):
                # diagonal steps are allowed, so the number of moves is the larger of the two distances
                return max(abs(tile[0] - ax), abs(tile[1] - ay))
            far = [tile for tile in free if moves(tile) >= min_distance]
            if not far:
                farthest = max(moves(tile) for tile in free)
                far = [tile for tile in free if moves(tile) == farthest]
            free = far
        return random.choice(free)

    # Return a random free floor tile in a room exactly the given number of moves from a creature,
    # or, if the rooms have none, one of the free tiles closest to that number of moves.
    def free_floor_at_distance(self, creature, moves_wanted):
        c_x, c_y = creature.get_position()
        free = self.free_room_tiles()
        def off_by(tile):
            return abs(max(abs(tile[0] - c_x), abs(tile[1] - c_y)) - moves_wanted)
        best = min(off_by(tile) for tile in free)
        return random.choice([tile for tile in free if off_by(tile) == best])

    def __init__(self):
        # messages produced during a turn, shown in the bottom UI
        self.messages = []
        # index of the first message shown in the log; the More key moves it
        self.log_offset = 0
        # name of the creature that killed the player, set when that happens
        self.killed_by = None
        self.rooms, self.corridor = self.generate()
        self.distance_cache = {}    # for distances_to
        self.view_cache = {}        # for visible_tiles
        self.seen = set()           # every tile the player has seen: remembered and drawn dim
        self.creatures = []

        # the player must be added first: index 0 in self.creatures is always the player
        self.player = self.add_creature(Player)
        # a neutral golem starting NEAR_GOLEM_SPAWN_DISTANCE moves away if possible, close enough to go and talk to
        near_golem = Golem(self.free_floor_at_distance(self.player, NEAR_GOLEM_SPAWN_DISTANCE))
        self.set_sign_with_creature(near_golem)
        self.creatures.append(near_golem)
        self.add_creature(Orc, RUN_RIGHT)
        self.add_creature(Orc)
        orc3 = self.add_creature(Orc, CHASE, self.player)
        orc4 = self.add_creature(Orc, CHASE, orc3)
        self.add_creature(Orc, CHASE, orc4)
        self.add_creature(Kobold, CHASE, self.player)
        self.add_creature(Kobold, CHASE, self.player)
        self.add_creature(Kobold)
        self.add_creature(Kobold)
        self.add_creature(Uruk, CHASE, self.player)
        self.add_creature(Gnoll, CHASE, self.player)
        self.add_creature(Gnoll, CHASE, self.player)
        self.add_creature(Goblin, CHASE, self.player)
        self.add_creature(Golem)

    # Create a creature of the given class on a random free floor tile and add it to the map.
    # Creatures other than the player start at least MIN_SPAWN_DISTANCE moves from the player.
    def add_creature(self, creature_class, mood=None, target=None):
        if self.creatures:
            coords = self.random_free_floor(self.player, MIN_SPAWN_DISTANCE)
        else:
            coords = self.random_free_floor()
        creature = creature_class(coords, mood, target)
        self.set_sign_with_creature(creature)
        self.creatures.append(creature)
        return creature

    def position_filled_by_creature(self, x, y):
        # if position is either open or wall, false
        # if position is not open and not wall, it's a creature (true)
        return self.my_map[x][y] != OPEN_SPACE and self.my_map[x][y] != WALL

    # return True if something happened and time passed, False if no clause managed to do something worthwhile
    # move_to may hurt the target creature. Dying needs to be checked outside of it.
    # Hitting adds its messages to self.messages.
    # Creatures only hit those they can_attack; anyone else just blocks their way.
    def move_to(self, i, new_position):
        creatures = self.creatures
        creature = creatures[i]

        if new_position == creature.get_position():
            return True
        if self.my_map[new_position[0]][new_position[1]] == OPEN_SPACE:
            # Clear the old position
            current_pos = creature.get_position()
            self.my_map[current_pos[0]][current_pos[1]] = OPEN_SPACE
            # Update the creature position
            creature.position = new_position
            # Mark the new position with its ID
            self.my_map[creature.position[0]][creature.position[1]] = creature.sign
            return True
        elif self.position_filled_by_creature(new_position[0], new_position[1]):
            target = find_creature_at(creatures, new_position[0], new_position[1])
            if target != -1:
                victim = creatures[target]
                if not self.can_attack(creature, victim):
                    return False
                if victim is self.player and not self.chases_player(creature):
                    # a grey monster bumping into the player doesn't hit, but turns to chase the player
                    self.provoke(creature)
                    return True
                self.messages.extend(creature.hit(victim))
                self.react_to_hit(creature, victim)
            return True
        return False

    # How a creature that survives a hit reacts:
    # - one that flees at low health (kobolds, golems) and is now that low starts fleeing from the attacker
    # - one already fleeing keeps fleeing from whoever it fled from first
    # - otherwise, one the player hits starts chasing the player
    # - and one a friendly creature hits turns on that friendly creature
    def react_to_hit(self, attacker, victim):
        if victim.health <= 0 or victim.mood == FLEE:
            return
        if victim.flee_at_health is not None and victim.health <= victim.flee_at_health:
            victim.start_fleeing(attacker)
            self.messages.append("The " + victim.name + " flees from " + attacker.called() + "!")
        elif attacker is self.player:
            self.provoke(victim)
        elif attacker.mood == FRIEND and not (victim.mood == CHASE and victim.target is attacker):
            victim.mood = CHASE
            victim.target = attacker
            self.messages.append("The " + victim.name + " turns on " + attacker.called() + "!")

    def chases_player(self, creature):
        return creature.mood == CHASE and creature.target is self.player

    # A monster the player hits, or one that bumps into the player, starts chasing the player
    # if it wasn't already
    def provoke(self, victim):
        if self.chases_player(victim):
            return
        victim.mood = CHASE
        victim.target = self.player
        if victim.health > 0:       # a killed one gets a death message instead
            self.messages.append("The " + victim.name + " turns to chase you!")

    # The player attacks anyone. A friendly creature never attacks its friend, but attacks anyone
    # chasing its friend or itself. Other creatures attack only the player or their own target.
    # (move_to turns a grey monster's attack on the player into turning to chase instead.)
    def can_attack(self, creature, victim):
        if creature is self.player:
            return True
        if creature.mood == FRIEND:
            return victim is not creature.target and victim.mood == CHASE \
                and (victim.target is creature.target or victim.target is creature)
        return victim is self.player or victim is creature.target

    # The creatures chasing the given one that are close to it (within CLOSE_STEPS)
    def threats_to(self, friend):
        f_x, f_y = friend.get_position()
        return [c for c in self.creatures if c.mood == CHASE and c.target is friend
                and max(abs(c.position[0] - f_x), abs(c.position[1] - f_y)) <= CLOSE_STEPS]

    # Two creatures change places (a chaser getting past one it won't attack, e.g. in the corridor)
    def swap_places(self, a, b):
        a.position, b.position = b.position, a.position
        self.set_sign_with_creature(a)
        self.set_sign_with_creature(b)

    def get_sign(self, x, y):
        return self.my_map[x][y]

    def set_sign_with_creature(self, creature):
        coords = creature.get_position()
        self.my_map[coords[0]][coords[1]] = creature.sign

    # return a death_note for passing a message to UI, and the index of creature that dies, to be handled in the calling function. -1 means none.
    def check_death_for_coords(self, x, y):
        creature_index = find_creature_at(self.creatures, x, y)
        if creature_index != -1:
            message = self.creatures[creature_index].check_death()
            if message != "":
                return (message, creature_index)
        return ("", -1)
