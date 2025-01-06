# loop_utils.py

import sys
from keyboard import read_moves
from map import (OPEN_SPACE, WALL)
from map import find_creature_at

def quit_app(reason, pygame):
    print(reason)
    pygame.quit()
    sys.exit()    

#   An idea for solving moving a whole array of creatures: implement calling each creature's type of movement by their mood.
def move_moodily(map, creature_i):
    creatures = map.creatures
    creature = creatures[creature_i]
    new_position = creature.get_position()
    death_note = creature.check_death()
    # handle possible creature index of a neighboring death. -1 stands for "no creature killed", otherwise pass the index of the creature to later kill in calling function.
    creature_index = -1
    neighbor_death_note = ""
    if death_note == "":
        if creature.mood == "ambulate":
            new_position = creature.move_random()
        elif creature.mood == "run right":
            new_position = creature.move_right()
        elif creature.mood == "toward":
            new_position = creature.move_toward(creature.target)
        map.move_to(creature_i, new_position, creatures)
        #I need to check here if the hit creature died, and return the data if they did
        neighbor_death_note, creature_index = map.check_death_for_coords(new_position[0], new_position[1])
    return death_note, neighbor_death_note, creature_index

def check_deaths(game_map, other_creatures_move_bool):
    dying = []
    death_notes = []
    deaths = 0
    neighbor_death_note = ""
    if other_creatures_move_bool:
        for i in range(1, len(game_map.creatures)):                     # don't move the player in a loop
            death_note, neighbor_death_note, neighbor_creature_index = move_moodily(game_map, i)
            if neighbor_death_note != "":
                dying.append(neighbor_creature_index)
                death_notes.append(neighbor_death_note)                
                print(str(neighbor_creature_index) + " is dying")
            if death_note != "":
                if i not in dying:
                    dying.append(i)
                    death_notes.append(death_note)
                    print(str(i) + " is dying")
        deaths = len(dying)
    else: 
        for i in range(0, len(game_map.creatures)):
            death_note = game_map.creatures[i].check_death()
            if death_note != "":
                if i == 0:
                    return "You die!"
                if i not in dying:
                    dying.append(i)
                    death_notes.append(death_note)
                    print(str(i) + " is dying")
        deaths = len(dying)
    for i in range(0, deaths):
        death_location = game_map.creatures[dying[deaths-i-1]].get_position()
        game_map.my_map[death_location[0]][death_location[1]] = OPEN_SPACE
        game_map.creatures.pop(dying[deaths-i-1])
    return death_notes

def handle_events(pygame, game_map, messages):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("event.type == quit", pygame)
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
                messages = []
                death_notes1 = []
                # move creature_0, the player
                if game_map.move_to(0, new_position, game_map.creatures): # 0 refers to the player
                    death_notes1 = check_deaths(game_map, False)   # check if player killed anyone
                death_notes2 = check_deaths(game_map, True)    # have all creatures move and check if they killed anyone
                if "You die!" in death_notes2:
                    quit_app("You die!", pygame)
                if len(death_notes1) > 0:
                    messages += death_notes1
                if len(death_notes2) > 0:
                    messages += death_notes2
    return messages