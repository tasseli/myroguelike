# loop_utils.py

import sys
from keyboard import read_moves
from death import check_deaths

def quit_app(reason, pygame):
    print(reason)
    pygame.quit()
    sys.exit()    

def handle_events(pygame, game_map, messages):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("event.type == quit")
        if event.type == pygame.KEYDOWN:
            new_position = game_map.player.get_position().copy()
            outcome = read_moves(new_position, event.key, pygame)
            if outcome == "q":
                quit_app("q or x pressed", pygame)
            elif outcome == "o":
#               An unhandled key was pressed
                pass
            elif outcome == "m" or outcome == "s":
#               Move key or stand still key
                messages = [""]
                death_notes1 = []
                if game_map.move_to(0, new_position, game_map.creatures): # 0 refers to the player
                    death_notes1 = check_deaths(game_map, False)   # check if player killed anyone
                death_notes2 = check_deaths(game_map, True)    # have all creatures move and check if they killed anyone
                if len(death_notes1) > 0:
                    messages = death_notes1
                if len(death_notes1) > 0:
                    messages += death_notes2
    return messages