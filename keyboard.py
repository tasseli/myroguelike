#keyboard.py

# Return the outcome of a key press, and which way to move as (dx, dy):
#   regular move:                           return "m", (dx, dy)
#   stay still, middle direction:           return "s", (0, 0)
#   quit command, to be handled in caller:  return "q", None
#   other, currently unhandled:             return "o", None
def read_moves(eventkey, pygame):
    if eventkey == pygame.K_q or eventkey == pygame.K_x:
        return "q", None
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

def read_q_only(eventkey, pygame):
    if eventkey == pygame.K_q or eventkey == pygame.K_x:
        return "q"
