# Example file showing a basic pygame "game loop"
import pygame
import sys

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

class Player:
    position = [1, 1]
    def __init__(self):
        self.position = [3, 6]
    def get_position(self):
        return self.position

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

# Define constants for tile types
OPEN_SPACE = 0
WALL = 1
PLAYER = 2

# Define colors for tiles
WHITE = (255, 255, 255)  # Open space
GRAY = (128, 128, 128)   # Wall
DARK_GRAY = (64, 64, 64)
BLACK = (0, 0, 0)        # Text color

# Define the dimensions of the map
MAP_WIDTH = 80
MAP_HEIGHT = 40
TILE_SIZE = 16

# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE))
pygame.display.set_caption("Simple Roguelike Map")

# Initialize an empty map
game_map = [[OPEN_SPACE for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

# Initialize a font
font = pygame.font.SysFont(None, 22)

# Set a wall at position (3, 5)
game_map[3][5] = WALL
game_map[0] = [WALL for x in range(MAP_HEIGHT)]
game_map[MAP_WIDTH-1] = [WALL for x in range(MAP_HEIGHT)]
for x in range(MAP_WIDTH):
    game_map[x][0] = WALL
    game_map[x][MAP_HEIGHT-1] = WALL
    
player = Player()
current_pos = player.get_position()
game_map[current_pos[0]][current_pos[1]] = 2

def draw_and_blit_char(my_char):
    pygame.draw.rect(screen, DARK_GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Render the '#' character on top of the wall
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
            if event.key == pygame.K_LEFT:
                player.position[0] = player.position[0]-1
            if event.key == pygame.K_RIGHT:
                player.position[0] = player.position[0]+1
            if event.key == pygame.K_UP:
                player.position[1] = player.position[1]-1
            if event.key == pygame.K_DOWN:
                player.position[1] = player.position[1]+1

    game_map[current_pos[0]][current_pos[1]] = 2

    # Clear the screen
    screen.fill(GRAY)

    # Render the map
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if game_map[x][y] == WALL:
                draw_and_blit_char("#")
            elif game_map[x][y] == PLAYER:
                draw_and_blit_char("@")
    # Update the display
    pygame.display.flip()
