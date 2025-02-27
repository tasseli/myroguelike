# creatures.py
import random

class Creature:
    sign = "c"
    mood = "ambulate"
    name = "generic creature"
    alive = True
    target = None
    health = 2
    health_max = health
    damage = 1

    def __init__(self, coords):
        self.position = coords

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
    health = 12
    health_max = health
    damage = 4

class Orc(Creature):
    sign = "o"
    name = "orc"
    damage = 3

    def __init__(self, coords, mood, target):
        self.position = [coords[0], coords[1]]
        self.health = random.randint(3, 7)
        self.health_max = self.health
        if mood != None:
            self.mood = mood
        if target != None:
            self.target = target

class Kobold(Creature):
    sign = "k"
    name = "kobold"
    damage = 2

    def __init__(self, coords, mood, target):
        self.position = [coords[0], coords[1]]
        self.health = random.randint(2, 6)
        self.health_max = self.health
        if mood != None:
            self.mood = mood
        if target != None:
            self.target = target

class Uruk(Creature):
    sign = "o"
    name = "uruk"
    damage = 4

    def __init__(self, coords, mood, target):
        self.position = [coords[0], coords[1]]
        self.health = random.randint(6, 9)
        self.health_max = self.health
        if mood != None:
            self.mood = mood
        if target != None:
            self.target = target

class Gnoll(Creature):
    sign = "g"
    name = "gnoll"
    damage = 3

    def __init__(self, coords, mood, target):
        self.position = [coords[0], coords[1]]
        self.health = random.randint(3, 6)
        self.health_max = self.health
        if mood != None:
            self.mood = mood
        if target != None:
            self.target = target

class Goblin(Creature):
    sign = "g"
    name = "goblin"
    damage = 2

    def __init__(self, coords, mood, target):
        self.position = [coords[0], coords[1]]
        self.health = random.randint(3, 5)
        self.health_max = self.health
        if mood != None:
            self.mood = mood
        if target != None:
            self.target = target

class Golem(Creature):
    sign = "G"
    name = "golem"
    damage = 4

    def __init__(self, coords, mood, target):
        self.position = [coords[0], coords[1]]
        self.health = random.randint(13, 18)
        self.health_max = self.health
        if mood != None:
            self.mood = mood
        if target != None:
            self.target = target

