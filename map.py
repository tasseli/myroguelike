# map.py

from creatures import Player, Orc, Kobold, Uruk, Gnoll, Goblin, Golem

# Define the dimensions of the map
MAP_WIDTH = 80
MAP_HEIGHT = 40
TILE_SIZE = 16

# Define constants for tile types
OPEN_SPACE = '.'
WALL = '#'

# Define colors for tiles
WHITE = (255, 255, 255)  # 
GRAY = (128, 128, 128)   # Open space
DARK_GRAY = (64, 64, 64) # Wall
BLACK = (0, 0, 0)        # Text color

def find_creature_at(creatures, x, y):
    i = 0
    for creature in creatures:
        if creature.position[0] == x and creature.position[1] == y:
            return i
        i += 1
    return -1

class Map:

    def __init__(self):
        self.my_map = [[OPEN_SPACE for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]
        # Set a wall at position (3, 5)
        self.my_map[3][5] = WALL
        for i in range(6, 14):
            self.my_map[55][i] = WALL
        for i in range(13, 30):
            self.my_map[75][i] = WALL
        for i in range(15, 25):
            self.my_map[i][33] = WALL
        # wall for left side
        self.my_map[0] = [WALL for x in range(MAP_HEIGHT)]
        # wall for right side
        self.my_map[MAP_WIDTH-1] = [WALL for x in range(MAP_HEIGHT)]
        # wall for top and bottom
        for x in range(MAP_WIDTH):
            self.my_map[x][0] = WALL
            self.my_map[x][MAP_HEIGHT-1] = WALL

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

        self.player = init_player([3,6])

        self.creatures = [self.player]
        orc = init_orc([5,12], "run right", None, self.creatures)
        orc2 = init_orc([1,3], None, None, self.creatures)
        orc3 = init_orc([72,33], "toward", self.player, self.creatures)
        orc4 = init_orc([37,23], "toward", orc3, self.creatures)
        orc5 = init_orc([6,38], "toward", orc4, self.creatures)
        kobold = init_kobold([49,29], "toward", self.player, self.creatures)
        uruk = init_uruk([40,10], "toward", self.player, self.creatures) 
        gnoll1 = init_gnoll([45,2], "toward", self.player, self.creatures)
        gnoll2 = init_gnoll([48,5], "toward", self.player, self.creatures)
        goblin1 = init_goblin([65,38], "toward", self.player, self.creatures)
        golem1 = init_golem([6,7], None, None, self.creatures)

    def position_filled_by_creature(self, x, y):
        # if position is either open or wall, false
        # if position is not open and not wall, it's a creature (true)
        return self.my_map[x][y] != OPEN_SPACE and self.my_map[x][y] != WALL

    # return True if something happened and time passed, False if no clause managed to do something worthwhile
    # move_to may hurt the target creature. Dying needs to be checked outside of it. Target is at new_position, self.creatures[target]
    # target = find_creature_at(creatures, new_position[0], new_position[1])
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
        elif self.position_filled_by_creature(new_position[0], new_position[1]) or self.my_map[new_position[0]][new_position[1]] == "@":
            target = find_creature_at(creatures, new_position[0], new_position[1])
            if target != -1:
                creature.hit(self.creatures[target])
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
        # a function call to print a message would make sense, but there's no function like that yet.
