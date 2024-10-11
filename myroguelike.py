# Ideas
# map generation
# agent knowledge
# agent communication (language, )
# agent faction
# faction knowledge
# faction communication
# cultures for groups?
# languages based on INT
# bartering based on language / abilities
# "Look at ..." "It doesn't make sense to you" / "you see another Dwarven healer with a spellbook of second circle on their backpack, probably"
# It would be very cool if there'd be stat potions lying around, and raising a stat did show, but everything else changed based on the stats.

# Easy steps for refactoring
#- do functions 
#- make classes 
#- create input handle logic 
#- refactor game loop 
#- plan map logic 
#- load map from file 
#- consider game manager class 
#- modularize rendering logic 
#- create collision and movement system 
#- consider game states

# pygame.display.set_mode() 	can be used to create the grid
# pygame.Surface				represents an off-screen image I can draw before blitting it to display. Frames, as it were.
# pygame.event.get()			capture inputs. Most commands use up a turn, some don't.
# pygame.KEYDOWN				detects arrows or WASD etc.
# pygame.font.Font()			creating font object to render text
# font.render()					converting ASCII to images
# pygame.time.Clock()			control speed of the game. Handling frame rate, checking for input.
# screen.blit()					Draw surface
# pygame.display.update()		Updates the contents of the display after drawing everything. Update the screen after action or turn.
# Game loop idea:				1 capture input 2 update game state 3 render new state 4 wait for next input

# Example file showing a basic pygame "game loop"
import pygame
import sys

# Define the dimensions of the map
MAP_WIDTH = 80
MAP_HEIGHT = 40
TILE_SIZE = 16

# Define constants for tile types
OPEN_SPACE = 0
WALL = 1
PLAYER = 2

class Player:
    def __init__(self):
        self.position = [3, 6]

    def get_position(self):
        return self.position

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

# Define colors for tiles
WHITE = (255, 255, 255)  # Open space
GRAY = (128, 128, 128)   # Wall
DARK_GRAY = (64, 64, 64)
BLACK = (0, 0, 0)        # Text color

# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE))
pygame.display.set_caption("Simple Roguelike Map")

# Initialize an empty map
game_map = Map()

# Initialize a font
font = pygame.font.SysFont(None, 22)
    
player = Player()
current_pos = player.get_position()
game_map.set_location(current_pos, 2)

def draw_and_blit_char(my_char, x, y):
    pygame.draw.rect(screen, DARK_GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Render the my_char ('#'/'@') character on top of the background color
    text_surface = font.render(my_char, True, BLACK)
    text_rect = text_surface.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
    screen.blit(text_surface, text_rect)

 # Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            new_position = player.get_position().copy()
            if event.key == pygame.K_LEFT:
                new_position[0] -= 1
            if event.key == pygame.K_RIGHT:
                new_position[0] += 1
            if event.key == pygame.K_UP:
                new_position[1] -= 1
            if event.key == pygame.K_DOWN:
                new_position[1] += 1
            if event.key == pygame.K_1:
                new_position[0] -= 1
                new_position[1] += 1

            # Check if the new position is not a wall
            if game_map.my_map[new_position[0]][new_position[1]] != WALL:
                # Clear the old position
                current_pos = player.get_position()
                game_map.my_map[current_pos[0]][current_pos[1]] = OPEN_SPACE
                # Update the player position
                player.position = new_position
                # Mark the new position with PLAYER
                game_map.my_map[player.position[0]][player.position[1]] = PLAYER
                
    # Clear the screen
    screen.fill(GRAY)

    # Render the map
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if game_map.get_location(x,y) == WALL:
                draw_and_blit_char("#", x, y)
            elif game_map.get_location(x,y) == PLAYER:
                draw_and_blit_char("@", x, y)
    # Update the display
    pygame.display.flip()
