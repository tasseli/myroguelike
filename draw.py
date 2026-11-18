# draw.py

from map import (GRAY, DARK_GRAY, BLACK)
from map import (MAP_WIDTH, MAP_HEIGHT, TILE_SIZE)
from map import OPEN_SPACE

# how far around the player the map is visible
VIEW_RADIUS = 12

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

# Show the player's health at the right end of the first message row. Call after render_message_log.
def render_player_status(player, pygame, screen, font):
    status = "HP " + str(max(player.health, 0)) + "/" + str(player.health_max)
    start_x = MAP_WIDTH - 1 - len(status)
    for i in range(len(status)):
        draw_and_blit_char(pygame, screen, font, status[i], start_x + i, MAP_HEIGHT, DARK_GRAY)

def coords_on_border_of_map(x, y):
    if x == 0 or x == MAP_WIDTH-1 or y == 0 or y == MAP_HEIGHT-1:
        return True
    return False

# Compare squared distances: same result as z > sqrt(...), without the slow square root.
def coords_within_distance_z(x, y, z, creature):
    position = creature.get_position()
    c_x, c_y = position[0], position[1]
    return (c_x-x)**2 + (c_y-y)**2 < z*z # True or False

def render_floors_different_color(game_map, pygame, screen, font, x, y):
    if game_map.get_sign(x,y) == OPEN_SPACE:
        draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y, GRAY)
    else:
        draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y, DARK_GRAY)

def render_map(game_map, pygame, screen, font, creature):
    # the map's outer border is always visible
    for x in range(0, MAP_WIDTH):
        render_floors_different_color(game_map, pygame, screen, font, x, 0)
        render_floors_different_color(game_map, pygame, screen, font, x, MAP_HEIGHT-1)
    for y in range(1, MAP_HEIGHT-1):
        render_floors_different_color(game_map, pygame, screen, font, 0, y)
        render_floors_different_color(game_map, pygame, screen, font, MAP_WIDTH-1, y)
    # only tiles in a box around the creature can be close enough to see;
    # the box stays inside the border, which was already drawn above
    c_x, c_y = creature.get_position()
    for x in range(max(c_x - VIEW_RADIUS, 1), min(c_x + VIEW_RADIUS + 1, MAP_WIDTH-1)):
        for y in range(max(c_y - VIEW_RADIUS, 1), min(c_y + VIEW_RADIUS + 1, MAP_HEIGHT-1)):
            if coords_within_distance_z(x, y, VIEW_RADIUS, creature):
                render_floors_different_color(game_map, pygame, screen, font, x, y)

# Rendered characters, built once per font and character and then reused
glyph_cache = {}

def get_glyph(font, my_char):
    key = (font, my_char)
    if key not in glyph_cache:
        glyph_cache[key] = font.render(my_char, True, BLACK)
    return glyph_cache[key]

def draw_and_blit_char(pygame, screen, font, my_char, x, y, color):
    pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Draw the my_char (e.g. '#' / '@') character on top of the background color
    text_surface = get_glyph(font, my_char)
    text_rect = text_surface.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
    screen.blit(text_surface, text_rect)