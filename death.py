# death.py

from map import (OPEN_SPACE,
WALL,
PLAYER,
ORC,
KOBOLD)

def check_deaths(game_map, moves_bool):
    dying = []
    death_notes = []
    if moves_bool:
        for i in range(1, len(game_map.creatures)):                     # don't move the player in a loop
            death_note = game_map.move_moodily(i, game_map.creatures)
            if death_note != "":
                death_notes.append(death_note)
    for i in range(0, len(game_map.creatures)):
        death_note = game_map.creatures[i].check_death()
        if death_note != "":
            if i == 0:
                quit_app("You died!")
            dying.append(i)
            death_notes.append(death_note)
    deaths = len(dying)
    for i in range(0, deaths):
        death_location = game_map.creatures[dying[deaths-i-1]].get_position()
        game_map.my_map[death_location[0]][death_location[1]] = OPEN_SPACE
        game_map.creatures.pop(dying[deaths-i-1])
    return death_notes