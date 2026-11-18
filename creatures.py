# creatures.py
import random

class Creature:
    sign = "c"
    mood = "ambulate"
    name = "generic creature"
    health_range = (2, 2)   # starting health is rolled from this range, inclusive
    damage = 1

    def __init__(self, coords, mood=None, target=None):
        self.position = [int(coords[0]), int(coords[1])]
        self.health = random.randint(*self.health_range)
        self.health_max = self.health
        self.alive = True
        self.target = target
        if mood is not None:
            self.mood = mood

    def get_position(self):
        return self.position

    def hit(self, target_creature):
	#pass messages about hitting to be displayed
        target_creature.health -= self.damage
        message1 = target_creature.name + " hit for " + str(self.damage) + " damage by " + self.name
        message2 = target_creature.name + " has " + str(target_creature.health) + " health. "
        return message1, message2

    def check_death(self):
        if self.health < 1:
            return self.name + " dies! "
        return ""

    def move_right(self):
        return [self.position[0] + 1, self.position[1]]

    def move_random(self):
        x = random.randint(0,2)-1
        y = random.randint(0,2)-1
        return [self.position[0] + x, self.position[1] + y]

    def move_toward(self, destination):
        destination = destination.get_position()
        x = 0
        y = 0
        if destination[0] > self.position[0]:
            x = 1
        elif destination[0] < self.position[0]:
            x = -1
        if destination[1] > self.position[1]:
            y = 1
        elif destination[1] < self.position[1]:
            y = -1
        return [self.position[0] + x, self.position[1] + y]

class Player(Creature):
    sign = "@"
    mood = "player"
    name = "player"
    health_range = (12, 12)
    damage = 4

class Orc(Creature):
    sign = "o"
    name = "orc"
    health_range = (3, 7)
    damage = 3

class Kobold(Creature):
    sign = "k"
    name = "kobold"
    health_range = (2, 6)
    damage = 2

class Uruk(Creature):
    sign = "u"
    name = "uruk"
    health_range = (6, 9)
    damage = 4

class Gnoll(Creature):
    sign = "n"
    name = "gnoll"
    health_range = (3, 6)
    damage = 3

class Goblin(Creature):
    sign = "g"
    name = "goblin"
    health_range = (3, 5)
    damage = 2

class Golem(Creature):
    sign = "G"
    name = "golem"
    health_range = (13, 18)
    damage = 4
