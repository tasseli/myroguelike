# draw.py

from map import (WHITE, GRAY, DARK_GRAY, BLACK)
from map import (MAP_WIDTH, MAP_HEIGHT, TILE_SIZE)
from map import (OPEN_SPACE, WALL)
from creatures import Creature
from math import sqrt

def render_message_log(messages, pygame, screen, font):
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

def coords_on_border_of_map(x, y):
    if x == 0 or x == MAP_WIDTH-1 or y == 0 or y == MAP_HEIGHT-1:
        return True
    return False

def coords_within_distance_z(x, y, z, creature):
    position = creature.get_position()
    c_x = position[0]
    c_y = position[1]
    return z > sqrt((c_x-x)**2 + (c_y-y)**2) # True or False

def render_floors_different_color(game_map, pygame, screen, font, x, y):
    if game_map.get_sign(x,y) == OPEN_SPACE:
        draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y, GRAY)
    else:
        draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y, DARK_GRAY)

def render_map(game_map, pygame, screen, font, creature):    
    y = 0
    for x in range(0, MAP_WIDTH):
        for y in range(0, MAP_HEIGHT):
            if coords_on_border_of_map(x, y):
                render_floors_different_color(game_map, pygame, screen, font, x, y)
            if coords_within_distance_z(x, y, 12, creature):
                render_floors_different_color(game_map, pygame, screen, font, x, y)

def draw_and_blit_char(pygame, screen, font, my_char, x, y, color):
    pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Render the my_char (e.g. '#' / '@') character on top of the background color
    text_surface = font.render(my_char, True, BLACK)
    text_rect = text_surface.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
    screen.blit(text_surface, text_rect)