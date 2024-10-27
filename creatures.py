# creatures.py

class Player:
    sign = "@"
    id = 2

    def __init__(self):
        self.position = [3, 6]

    def get_position(self):
        return self.position

class Orc:
    sign = "o"
    id = 3

    def __init__(self):
        self.position = [62, 30]

    def get_position(self):
        return self.position

    def move(self):
        return [self.position[0] + 1, self.position[1]]

