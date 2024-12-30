# creatures.py
import random

class Player:
    sign = "@"
    mood = "player"
    name = "player"
    health = 12
    health_max = health
    damage = 4

    def __init__(self, coords):
        self.position = coords

    def get_position(self):
        return self.position

    def hit(self, target_creature):
        target_creature.health -= self.damage
        message1 = target_creature.name + " hit for " + str(self.damage) + " damage by " + self.name
        print(message1)
        message2 = target_creature.name + " has " + str(target_creature.health) + " health"
        print(message2)

    def check_death(self):
        if self.health < 1:
            return self.name + " dies!"
        return ""

class Orc:
    sign = "o"
    name = "orc"
    mood = "ambulate"
    target = None
    damage = 3
    health = 5

    def __init__(self, coords, mood, target):
        self.position = [coords[0], coords[1]]
        health = random.randint(3, 7)
        health_max = health
        if mood != None:
            self.mood = mood
        if target != None:
            self.target = target

    def hit(self, target_creature):
        target_creature.health -= self.damage
        message1 = target_creature.name + " hit for " + str(self.damage) + " damage by " + self.name
        print(message1)
        message2 = target_creature.name + " has " + str(target_creature.health) + " health"
        print(message2)

    def take_hit(self, damage):
        self.health -= damage

    def get_position(self):
        return self.position

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

    def check_death(self):
        if self.health < 1:
            return self.name + " dies!"
        return ""

class Kobold:
    sign = "k"
    name = "kobold"
    mood = "ambulate"
    target = None
    damage = 2
    health = 4

    def __init__(self, coords, mood, target):
        self.position = [coords[0], coords[1]]
        health = random.randint(2, 6)
        health_max = health
        if mood != None:
            self.mood = mood
        if target != None:
            self.target = target

    def hit(self, target_creature):
        target_creature.health -= self.damage
        message1 = target_creature.name + " hit for " + str(self.damage) + " damage by " + self.name
        print(message1)
        message2 = target_creature.name + " has " + str(target_creature.health) + " health"
        print(message2)

    def take_hit(self, damage):
        self.health -= damage

    def get_position(self):
        return self.position

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

    def check_death(self):
        if self.health < 1:
            return self.name + " dies!"
        return ""

