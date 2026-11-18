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
WHITE       = (255, 255, 255)  #
GRAY        = (128, 128, 128)   # Open space
DARK_GRAY   = (64, 64, 64) # Wall
BLACK       = (0, 0, 0)        # Text color

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

        def init_player(coords):
            player = Player(coords)
            self.set_sign_with_creature(player)
            return player

        def init_orc(coords, mood, target, creatures):
            orc = Orc(coords, mood, target)
            self.set_sign_with_creature(orc)
            creatures.append(orc)
            return orc

        def init_uruk(coords, mood, target, creatures):
            uruk = Uruk(coords, mood, target)
            self.set_sign_with_creature(uruk)
            creatures.append(uruk)
            return uruk

        def init_kobold(coords, mood, target, creatures):
            kobold = Kobold(coords, mood, target)
            self.set_sign_with_creature(kobold)
            creatures.append(kobold)
            return kobold

        def init_gnoll(coords, mood, target, creatures):
            gnoll = Gnoll(coords, mood, target)
            self.set_sign_with_creature(gnoll)
            creatures.append(gnoll)
            return gnoll

        def init_goblin(coords, mood, target, creatures):
            goblin = Goblin(coords, mood, target)
            self.set_sign_with_creature(goblin)
            creatures.append(goblin)
            return goblin

        def init_golem(coords, mood, target, creatures):
            golem = Golem(coords, mood, target)
            self.set_sign_with_creature(golem)
            creatures.append(golem)
            return golem

        free = self.random_free_floor
        self.player = init_player(free())
        self.creatures = [self.player]
        orc = init_orc(free(), "run right", None, self.creatures)
        orc2 = init_orc(free(), None, None, self.creatures)
        orc3 = init_orc(free(), "toward", self.player, self.creatures)
        orc4 = init_orc(free(), "toward", orc3, self.creatures)
        orc5 = init_orc(free(), "toward", orc4, self.creatures)
        kobold = init_kobold(free(), "toward", self.player, self.creatures)
        uruk = init_uruk(free(), "toward", self.player, self.creatures)
        gnoll1 = init_gnoll(free(), "toward", self.player, self.creatures)
        gnoll2 = init_gnoll(free(), "toward", self.player, self.creatures)
        goblin1 = init_goblin(free(), "toward", self.player, self.creatures)
        golem1 = init_golem(free(), None, None, self.creatures)

    def position_filled_by_creature(self, x, y):
        # if position is either open or wall, false
        # if position is not open and not wall, it's a creature (true)
        return self.my_map[x][y] != OPEN_SPACE and self.my_map[x][y] != WALL

    # return True if something happened and time passed, False if no clause managed to do something worthwhile
    # move_to may hurt the target creature. Dying needs to be checked outside of it.
    # Hitting adds its messages to self.messages.
    def move_to(self, i, new_position, creatures):
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
