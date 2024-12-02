# myroguelike.py

import pygame
import sys
from map import (Map, 
MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
OPEN_SPACE, WALL, PLAYER, ORC)
from map import (draw_and_blit_char,
WHITE, GRAY, DARK_GRAY, BLACK)
from keyboard import read_moves
BOTTOM_UI_HEIGHT = 4

# pygame setup
pygame.init()
# Set up the display
screen = pygame.display.set_mode((MAP_WIDTH * TILE_SIZE, (MAP_HEIGHT + BOTTOM_UI_HEIGHT) * TILE_SIZE))
pygame.display.set_caption("MYRoguelike")

# Initialize a font
font = pygame.font.SysFont(None, 22)

def quit_app(reason):
    print(reason)
    pygame.quit()
    sys.exit()    

# Initialize an empty map
game_map = Map()

def check_deaths(game_map, moves_bool):
    dying = []
    death_notes = []
    if moves_bool:
        for i in range(1, len(game_map.creatures)):                     # don't move the player in a loop
            death_note = game_map.move_moodily(i, game_map.creatures)
            if death_note != "":
                print("Death note works: " + death_note)
                death_notes.append(death_note)
                for note in death_notes:
                    print(note)
    for i in range(0, len(game_map.creatures)):
        death_note = game_map.creatures[i].check_death()
        if death_note != "":
            if i == 0:
                quit_app("You died!")
            dying.append(i)
            print("Death note works: " + death_note)
            death_notes.append(death_note)
            print("death_notes: ")
            for note in death_notes:
                print(note)
    deaths = len(dying)
    for i in range(0, deaths):
        death_location = game_map.creatures[dying[deaths-i-1]].get_position()
        game_map.my_map[death_location[0]][death_location[1]] = OPEN_SPACE
        game_map.creatures.pop(dying[deaths-i-1])
    return death_notes

# Main loop

while True:
    messages = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("event.type == quit")
        if event.type == pygame.KEYDOWN:
            new_position = game_map.player.get_position().copy()
            outcome = read_moves(new_position, event.key, pygame)
            if outcome == "q":
                quit_app("q or x pressed")
            elif outcome == "o":
#               An unhandled key was pressed
                pass
            elif outcome == "m" or outcome == "s":
#               Move key or stand still key
                death_notes1 = []
                if game_map.move_to(0, new_position, game_map.creatures): # 0 refers to the player
                    death_notes1 = check_deaths(game_map, False)   # check if player killed anyone
                death_notes2 = check_deaths(game_map, True)    # have all creatures move and check if they killed anyone
                if len(death_notes1) > 0:
                    messages = death_notes1
                if len(death_notes1) > 0:
                    messages += death_notes2
    if len(messages) > 0:
        print("Messages0 currently: " + messages[0])

    # Clear the screen
    screen.fill(GRAY)

    # Render the map
    y = 0
    for x in range(0, MAP_WIDTH):
        for y in range(0, MAP_HEIGHT):
            if game_map.get_sign(x,y) == OPEN_SPACE:
                draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y, GRAY)
            else:
                draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y, DARK_GRAY)

    if len(messages) > 0:
        if len(messages) < 4:
            for i in range(4 - len(messages)):
                messages.append("")
                #now there are 4 strings in message
        string_index = 0
        for a_string in messages:
            draw_and_blit_char(pygame, screen, font, " ", 0, MAP_HEIGHT + string_index, GRAY)
            for i in range(0, len(a_string)):
                draw_and_blit_char(pygame, screen, font, a_string[i], 1 + i, MAP_HEIGHT + string_index, DARK_GRAY)
            for j in range(len(a_string), MAP_WIDTH):
                draw_and_blit_char(pygame, screen, font, " ", j, MAP_HEIGHT + string_index, GRAY)
            string_index += 1
    # Update the display
    pygame.display.flip()
