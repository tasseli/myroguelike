# creatures.py
import random

# Moods: what a creature does on its turn. Most moods are about creature.target.
CHASE = "chase"             # moves toward its target and attacks it
WANDER = "wander"           # moves around randomly
RUN_RIGHT = "run right"     # runs right until it hits a wall, then wanders
FLEE = "flee"               # moves away from its target until healed to full
FRIEND = "friend"           # stays close to its target and defends it
PLAYER_MOOD = "player"      # the player: moved by the keyboard

# "an orc", "a gnoll"
def with_article(name):
    return ("an " if name[0] in "aeiou" else "a ") + name

class Creature:
    sign = "c"
    mood = WANDER
    name = "generic creature"
    health_range = (2, 2)   # starting health is rolled from this range, inclusive
    damage = 1
    heal_interval = 20      # heal 1 health every this many turns
    flee_at_health = None   # a hit that leaves this much health or less makes it flee; None: never flees
    is_player = False

    def __init__(self, coords, mood=None, target=None):
        self.position = [int(coords[0]), int(coords[1])]
        self.health = random.randint(*self.health_range)
        self.health_max = self.health
        self.turns_until_heal = self.heal_interval
        self.alive = True
        self.target = target
        if mood is not None:
            self.mood = mood

    def get_position(self):
        return self.position

    # How the creature is called in messages: "you" for the player, "the orc" for others
    def called(self):
        if self.is_player:
            return "you"
        return "the " + self.name

    # Hit target_creature and return the messages about it, to be displayed
    def hit(self, target_creature):
        target_creature.health -= self.damage
        attacker = self.called()
        victim = target_creature.called()
        if victim == attacker:              # an orc hitting another orc
            victim = "another " + target_creature.name
        verb = "hit" if self.is_player else "hits"
        message = attacker.capitalize() + " " + verb + " " + victim + " for " + str(self.damage) + "."
        if target_creature.health > 0:      # a killing hit is followed by a death message instead
            if target_creature.is_player:
                message += " You have " + str(target_creature.health) + " health left."
            else:
                message += " It has " + str(target_creature.health) + " health left."
        return [message]

    # Call once per turn. Every heal_interval turns, heal 1 health, up to health_max.
    def heal_slowly(self):
        self.turns_until_heal -= 1
        if self.turns_until_heal <= 0:
            self.turns_until_heal = self.heal_interval
            if 0 < self.health < self.health_max:
                self.health += 1

    def check_death(self):
        if self.health < 1:
            return "The " + self.name + " dies!"
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
    mood = PLAYER_MOOD
    name = "player"
    is_player = True
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
    flee_at_health = 2

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
