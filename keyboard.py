#keyboard.py

# Return the outcome of a key press, and which way to move as (dx, dy):
#   regular move:                           return "m", (dx, dy)
#   stay still, middle direction:           return "s", (0, 0)
#   quit command, to be handled in caller:  return "q", None
#   show more of the message log:           return "more", None
#   wait a number of turns:                 return "wait", None
#   show the list of commands:              return "commands", None
#   show the help:                          return "help", None
#   look at creatures:                      return "look", None
#   other, currently unhandled:             return "o", None
# typed_char is the character the key produced; '?' is checked by it, because
# which key gives '?' depends on the keyboard layout.
def read_moves(eventkey, pygame, typed_char=""):
    if eventkey == pygame.K_q or eventkey == pygame.K_x:
        return "q", None
    elif typed_char == "?":
        return "commands", None
    elif eventkey == pygame.K_h:
        return "help", None
    elif eventkey == pygame.K_l:
        return "look", None
    elif eventkey == pygame.K_m:
        return "more", None
    elif eventkey == pygame.K_w:
        return "wait", None
    elif eventkey == pygame.K_LEFT or eventkey == pygame.K_KP4:
        return "m", (-1, 0)
    elif eventkey == pygame.K_RIGHT or eventkey == pygame.K_KP6:
        return "m", (1, 0)
    elif eventkey == pygame.K_UP or eventkey == pygame.K_KP8:
        return "m", (0, -1)
    elif eventkey == pygame.K_DOWN or eventkey == pygame.K_KP2:
        return "m", (0, 1)
    elif eventkey == pygame.K_1 or eventkey == pygame.K_KP1:
        return "m", (-1, 1)
    elif eventkey == pygame.K_3 or eventkey == pygame.K_KP3:
        return "m", (1, 1)
    elif eventkey == pygame.K_7 or eventkey == pygame.K_KP7:
        return "m", (-1, -1)
    elif eventkey == pygame.K_9 or eventkey == pygame.K_KP9:
        return "m", (1, -1)
    elif eventkey == pygame.K_5 or eventkey == pygame.K_KP5:
        return "s", (0, 0)
    else:
        return "o", None

# Return the digit typed as a string ("0"-"9"), from the number row or the numpad, or None for other keys
def read_digit(eventkey, pygame):
    number_row = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                  pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
    numpad = [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4,
              pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9]
    if eventkey in number_row:
        return str(number_row.index(eventkey))
    if eventkey in numpad:
        return str(numpad.index(eventkey))
    return None

# Keys on the death screen: "q" to quit, "r" to play again, "l" to look, None for any other key
def read_death_screen_key(eventkey, pygame):
    if eventkey == pygame.K_q or eventkey == pygame.K_x:
        return "q"
    elif eventkey == pygame.K_r:
        return "r"
    elif eventkey == pygame.K_l:
        return "l"
    return None
