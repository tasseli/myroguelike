#keyboard.py

# give a return value based on the outcome:
#   regular move successful:                return "m"
#   quit command, to be handled in called:  return "q"
#   other, currently unhandled:             return "o"
#   stay still, middle direction:           return "s"
def read_moves(new_position, eventkey, pygame):
    if eventkey == pygame.K_q or eventkey == pygame.K_x:
        return "q"
    elif eventkey == pygame.K_LEFT or eventkey == pygame.K_KP4:
        new_position[0] -= 1
        return "m"
    elif eventkey == pygame.K_RIGHT or eventkey == pygame.K_KP6:
        new_position[0] += 1
        return "m"
    elif eventkey == pygame.K_UP or eventkey == pygame.K_KP8:
        new_position[1] -= 1
        return "m"
    elif eventkey == pygame.K_DOWN or eventkey == pygame.K_KP2:
        new_position[1] += 1
        return "m"
    elif eventkey == pygame.K_1 or eventkey == pygame.K_KP1:
        new_position[0] -= 1
        new_position[1] += 1
        return "m"
    elif eventkey == pygame.K_3 or eventkey == pygame.K_KP3:
        new_position[0] += 1
        new_position[1] += 1
        return "m"
    elif eventkey == pygame.K_7 or eventkey == pygame.K_KP7:
        new_position[0] -= 1
        new_position[1] -= 1
        return "m"
    elif eventkey == pygame.K_9 or eventkey == pygame.K_KP9:
        new_position[0] += 1
        new_position[1] -= 1
        return "m"
    elif eventkey == pygame.K_5 or eventkey == pygame.K_KP5:
        return "s"
    else:
        return "o"