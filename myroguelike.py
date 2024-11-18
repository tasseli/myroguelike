# myroguelike.py

import pygame
import sys
from map import (Map, 
MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
OPEN_SPACE, WALL, PLAYER, ORC)
from map import (draw_and_blit_char,
WHITE, GRAY, DARK_GRAY, BLACK)
from keyboard import read_moves
BOTTOM_UI_HEIGHT = 2

# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, (MAP_HEIGHT) * TILE_SIZE))
pygame.display.set_caption("MYRoguelike")

# Initialize a font
font = pygame.font.SysFont(None, 22)

def quit_app(reason):
    print(reason)
    pygame.quit()
    sys.exit()    

# Initialize an empty map
game_map = Map()

# Main loop

while True:
#    y = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("event.type == quit")
        if event.type == pygame.KEYDOWN:
            new_position = game_map.player.get_position().copy()
            outcome = read_moves(new_position, event.key, pygame)
            if outcome == "q":
                quit_app("q or x pressed")
            elif outcome == "o":
#               print("An unhandled key was pressed.")
                pass
            elif outcome == "m" or outcome == "s":
#               print("Move key or stand still key")
                if game_map.move_if_available(0, new_position, game_map.creatures): # 0 refers to the player
                    dying = []
                    for i in range(1, len(game_map.creatures)):                     # don't move the player in a loop
                        game_map.move_moodily(i, game_map.creatures)
                        if game_map.creatures[i].check_death():
                            print("Looks like ", game_map.creatures[i].sign, " took so much damage it dies!")
                            dying.append(i)
                            print("dying: ", dying)
                    deaths = len(dying)
                    print("deaths: ", deaths)
                    for i in range(0, deaths):
                        print("popping: ", dying[deaths-i-1])
                        game_map.creatures.pop(dying[deaths-i-1])
                        

    # Clear the screen
    screen.fill(GRAY)

    # Render the map
    for x in range(MAP_WIDTH):
        for y in range(MAP_HEIGHT):
            if game_map.get_sign(x,y) == OPEN_SPACE:
                draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y, GRAY)
            else:
                draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y, DARK_GRAY)

#    for y in range(y, y + BOTTOM_UI_HEIGHT):
#        for x in range(MAP_WIDTH):
#            if y == MAP_HEIGHT:
##                draw_and_blit_char(pygame, screen, font, "-", x, y)

    # Update the display
    pygame.display.flip()
