# draw.py

from map import (WHITE, GRAY, DARK_GRAY, BLACK)
from map import (MAP_WIDTH, MAP_HEIGHT, TILE_SIZE)
from map import (OPEN_SPACE, WALL)

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

def render_map(game_map, pygame, screen, font):    
    y = 0
    for x in range(0, MAP_WIDTH):
        for y in range(0, MAP_HEIGHT):
            if game_map.get_sign(x,y) == OPEN_SPACE:
                draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y, GRAY)
            else:
                draw_and_blit_char(pygame, screen, font, game_map.get_sign(x,y), x, y, DARK_GRAY)

def draw_and_blit_char(pygame, screen, font, my_char, x, y, color):
    pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    # Render the my_char (e.g. '#' / '@') character on top of the background color
    text_surface = font.render(my_char, True, BLACK)
    text_rect = text_surface.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
    screen.blit(text_surface, text_rect)
