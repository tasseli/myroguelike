# map.py

from creatures import Orc

# Define the dimensions of the map
MAP_WIDTH = 80
MAP_HEIGHT = 40
TILE_SIZE = 16

# Define constants for tile types
OPEN_SPACE = '.'
WALL = '#'
PLAYER = '@'
ORC = 'o'

# Define colors for tiles
WHITE = (255, 255, 255)  # 
GRAY = (128, 128, 128)   # Open space
DARK_GRAY = (64, 64, 64) # Wall
BLACK = (0, 0, 0)        # Text color

def draw_and_blit_char(pygame, screen, font, my_char, x, y, color):
    pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Render the my_char (e.g. '#' / '@') character on top of the background color
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

    def move_if_available(self, creature, new_position):
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
            print("Player wants to hit an orc at ", new_position[0], new_position[1]) 
        return False

#   An idea for solving moving a whole array of creatures: implement calling each creature's type of movement by their mood.
    def move_moodily(self, creature):
        new_position = creature.get_position()
        if creature.mood == "ambulate":
            new_position = creature.move_random()
        elif creature.mood == "run right":
            new_position = creature.move_right()
        elif creature.mood == "toward":
            new_position = creature.move_toward(creature.target)
        self.move_if_available(creature, new_position)

    def get_sign(self, x, y):
        return self.my_map[x][y]
        
    def set_sign_with_creature(self, creature):
        coords = creature.get_position()
        self.my_map[coords[0]][coords[1]] = creature.sign

