# map.py

from creatures import Player, Orc, Kobold

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
            current_pos = player.get_position()
            self.set_sign_with_creature(player)
            return player

        def init_orc(coords, mood, target, creatures):
            orc = Orc(coords, mood, target)
            self.set_sign_with_creature(orc)
            creatures.append(orc)
            return orc

        def init_kobold(coords, mood, target, creatures):
            kobold = Kobold(coords, mood, target)
            self.set_sign_with_creature(kobold)
            creatures.append(kobold)
            return kobold

        self.player = init_player([3,6])

        self.creatures = [self.player]
        orc = init_orc([5,12], "run right", None, self.creatures)
        orc2 = init_orc([1,3], None, None, self.creatures)
        orc3 = init_orc([72,33], "toward", self.player, self.creatures)
        orc4 = init_orc([37,23], "toward", orc3, self.creatures)
        orc5 = init_orc([6,38], "toward", orc4, self.creatures)
        kobold = init_kobold([49,29], "toward", self.player, self.creatures)

    # return True if something happened and time passed, False if no clause managed to do something worthwhile
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
        elif self.my_map[new_position[0]][new_position[1]] == "o" and creature.sign == "@":
            target = find_creature_at(creatures, new_position[0], new_position[1])
            if target != -1: 
            # -1 stands for "no creature"
                creature.hit(self.creatures[target])
            return True
        elif (self.my_map[new_position[0]][new_position[1]] == "o" or self.my_map[new_position[0]][new_position[1]] == "@"):
            target = find_creature_at(creatures, new_position[0], new_position[1])
            if target != -1:
                creature.hit(self.creatures[target])
            return True
        return False

#this belongs under creatures
#   An idea for solving moving a whole array of creatures: implement calling each creature's type of movement by their mood.
    def move_moodily(self, creature_i, creatures):
        creature = creatures[creature_i]
        new_position = creature.get_position()
        death_note = creature.check_death()
        if death_note == "":
            if creature.mood == "ambulate":
                new_position = creature.move_random()
            elif creature.mood == "run right":
                new_position = creature.move_right()
            elif creature.mood == "toward":
                new_position = creature.move_toward(creature.target)
            self.move_to(creature_i, new_position, creatures)
            return death_note
        return death_note

    def get_sign(self, x, y):
        return self.my_map[x][y]
        
    def set_sign_with_creature(self, creature):
        coords = creature.get_position()
        self.my_map[coords[0]][coords[1]] = creature.sign

