# map.py

# Define the dimensions of the map
MAP_WIDTH = 80
MAP_HEIGHT = 40
TILE_SIZE = 16

# Define constants for tile types
OPEN_SPACE = 0
WALL = 1
PLAYER = 2
ORC = 3

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
    def get_location(self, x, y):
        return self.my_map[x][y]
    def set_location(self, coords, value):
        self.my_map[coords[0]][coords[1]] = value

