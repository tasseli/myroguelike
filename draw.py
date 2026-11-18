# draw.py

from map import (WHITE, GRAY, DARK_GRAY, BLACK, RED)
from map import (MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, LOG_ROWS)
from map import OPEN_SPACE

# how far around the player the map is visible
VIEW_RADIUS = 12

# Draw text on a dark background, one character per tile, starting at tile x, y.
def draw_text(text, x, y, pygame, screen, font):
    for i in range(len(text)):
        draw_and_blit_char(pygame, screen, font, text[i], x + i, y, DARK_GRAY)

# Draw text so that it ends one tile before the right edge of the window.
def draw_text_right(text, y, pygame, screen, font):
    draw_text(text, MAP_WIDTH - 1 - len(text), y, pygame, screen, font)

# Show LOG_ROWS messages under the map, starting from messages[offset].
# If there are more messages than fit, the rows are numbered and the last row
# tells which rows are shown and that the m key shows more.
def render_message_log(messages, offset, pygame, screen, font):
    numbered = len(messages) > LOG_ROWS
    number_width = len(str(len(messages)))
    shown = messages[offset:offset + LOG_ROWS]
    for row in range(len(shown)):
        text = shown[row]
        if numbered:
            text = str(offset + row + 1).rjust(number_width) + " " + text
        draw_text(text, 1, MAP_HEIGHT + row, pygame, screen, font)
    if numbered:
        if len(shown) == 1:
            rows = str(offset + 1)                                      # "9 of 9"
        else:
            rows = str(offset + 1) + "-" + str(offset + len(shown))    # "1-4 of 9"
        more = "[m] More: " + rows + " of " + str(len(messages))
        draw_text_right(more, MAP_HEIGHT + LOG_ROWS - 1, pygame, screen, font)

# In look mode, make the selected creature's tile blink: a white background every other 0.4 seconds
def render_look_cursor(creature, pygame, screen, font):
    if (pygame.time.get_ticks() // 400) % 2 == 0:
        x, y = creature.get_position()
        draw_and_blit_char(pygame, screen, font, creature.sign, x, y, WHITE)

# Show the most needed keys on the row under the message log
def render_key_hints(hints, pygame, screen, font):
    draw_text(hints, 1, MAP_HEIGHT + LOG_ROWS, pygame, screen, font)

# Show the player's health at the right end of the first message row. Call after render_message_log.
def render_player_status(player, pygame, screen, font):
    status = "HP " + str(max(player.health, 0)) + "/" + str(player.health_max)
    draw_text_right(status, MAP_HEIGHT, pygame, screen, font)

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
    # visible creatures whose mood has its own color are drawn again in that color
    for other in game_map.creatures:
        color = creature_color(other, game_map.player)
        o_x, o_y = other.get_position()
        if color != DARK_GRAY and coords_within_distance_z(o_x, o_y, VIEW_RADIUS, creature):
            draw_and_blit_char(pygame, screen, font, other.sign, o_x, o_y, color)

# The background color of a creature's tile, by its mood:
#   red:  a monster chasing the player
#   grey: everyone else (wandering, running, chasing another creature, and the player)
# A new mood shown in green is planned: add it here, e.g. if creature.mood == "...": return GREEN
def creature_color(creature, player):
    if creature.mood == "toward" and creature.target is player:
        return RED
    return DARK_GRAY

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