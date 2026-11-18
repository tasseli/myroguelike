# map.py

from creatures import Player, Orc, Kobold, Uruk, Gnoll, Goblin, Golem
import random

# Define the dimensions of the map
MAP_WIDTH   = 80
MAP_HEIGHT  = 40
TILE_SIZE   = 16

# Define constants for tile types
OPEN_SPACE  = '.'
WALL        = '#'

# Define colors for tiles
WHITE       = (255, 255, 255)   # 
GRAY        = (128, 128, 128)   # Open space
DARK_GRAY   = (64, 64, 64)      # Wall
BLACK       = (0, 0, 0)         # Text color

def find_creature_at(creatures, x, y):
    i = 0
    for creature in creatures:
        if creature.position[0] == x and creature.position[1] == y:
            return i
        i += 1
    return -1

class Map:

    # Fill the map with walls and carve out one room.
    # Return the room as (left, top, right, bottom); right and bottom are exclusive.
    def generate(self):
        self.my_map = [[WALL for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
        # the room is at least 8 by 8, and never touches the map's outer wall
        top = random.randint(1, MAP_HEIGHT // 2 - 4)
        bottom = random.randint(MAP_HEIGHT // 2 + 4, MAP_HEIGHT - 1)
        left = random.randint(1, MAP_WIDTH // 2 - 4)
        right = random.randint(MAP_WIDTH // 2 + 4, MAP_WIDTH - 1)
        for y in range(top, bottom):
            for x in range(left, right):
                self.my_map[x][y] = OPEN_SPACE
        return (left, top, right, bottom)

    # Return the coords of a random floor tile in the room that has no creature on it.
    def random_free_floor(self):
        left, top, right, bottom = self.room
        while True:
            x = random.randint(left, right - 1)
            y = random.randint(top, bottom - 1)
            if self.my_map[x][y] == OPEN_SPACE:
                return [x, y]

    def __init__(self):
        # messages produced during a turn, shown in the bottom UI
        self.messages = []
        self.room = self.generate()
        self.creatures = []

        # the player must be added first: index 0 in self.creatures is always the player
        self.player = self.add_creature(Player)
        self.add_creature(Orc, "run right")
        self.add_creature(Orc)
        orc3 = self.add_creature(Orc, "toward", self.player)
        orc4 = self.add_creature(Orc, "toward", orc3)
        self.add_creature(Orc, "toward", orc4)
        self.add_creature(Kobold, "toward", self.player)
        self.add_creature(Uruk, "toward", self.player)
        self.add_creature(Gnoll, "toward", self.player)
        self.add_creature(Gnoll, "toward", self.player)
        self.add_creature(Goblin, "toward", self.player)
        self.add_creature(Golem)

    # Create a creature of the given class on a random free floor tile and add it to the map.
    def add_creature(self, creature_class, mood=None, target=None):
        creature = creature_class(self.random_free_floor(), mood, target)
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
                self.messages.extend(creature.hit(creatures[target]))
            return True
        return False

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
