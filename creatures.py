# creatures.py
import random

class Player:
    sign = "@"

    def __init__(self):
        self.position = [3, 6]

    def get_position(self):
        return self.position

class Orc:
    sign = "o"

    def __init__(self, coords):
        self.position = [coords[0], coords[1]]

    def get_position(self):
        return self.position

    def move(self):
        return [self.position[0] + 1, self.position[1]]

    def move_random(self):
        x = random.randint(0,2)-1
        y = random.randint(0,2)-1
        return [self.position[0] + x, self.position[1] + y]