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

# Define colors for tiles
WHITE = (255, 255, 255)  # 
GRAY = (128, 128, 128)   # Open space
DARK_GRAY = (64, 64, 64) # Wall
BLACK = (0, 0, 0)        # Text color

# rough idea for the map's creature move checking function
# add ID for both creatures
#def move_if_available(my_map, new_position, creature):
#    if my_map[new_position[0]][new_position[1]] == OPEN_SPACE:
#        # Clear the old position
#        current_pos = creature.get_position()
#        my_map[current_pos[0]][current_pos[1]] = OPEN_SPACE
#        # Update the player position
#        creature.position = new_position
#        # Mark the new position with its ID
#        my_map[player.position[0]][player.position[1]] = PLAYER

def draw_and_blit_char(pygame, screen, font, my_char, x, y):
    pygame.draw.rect(screen, DARK_GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Render the my_char ('#'/'@') character on top of the background color
    text_surface = font.render(my_char, True, BLACK)
    text_rect = text_surface.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
    screen.blit(text_surface, text_rect)

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

