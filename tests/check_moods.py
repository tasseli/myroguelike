# tests/check_moods.py
# Mood checks: colors, provoking, fleeing, and friends.

from helpers import *     # pygame, the game's modules (m = map), and the shared helpers

def check_mood_colors():
    import draw
    from creatures import Kobold, Gnoll
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    chaser = Kobold([0, 0], CHASE, game_map.player)
    wanderer = Gnoll([0, 0])
    orc_chasing_orc = Orc([0, 0], CHASE, wanderer)
    place(game_map, chaser, p_x + 2, p_y)
    place(game_map, wanderer, p_x - 2, p_y)
    place(game_map, orc_chasing_orc, p_x, p_y + 2)
    assert draw.creature_color(chaser, game_map.player) == m.RED
    assert draw.creature_color(wanderer, game_map.player) == m.DARK_GRAY
    assert draw.creature_color(orc_chasing_orc, game_map.player) == m.DARK_GRAY
    assert draw.creature_color(game_map.player, game_map.player) == m.DARK_GRAY

    # on screen: the corner pixel of each tile has the tile's background color
    screen = pygame.display.set_mode((m.MAP_WIDTH * m.TILE_SIZE, m.MAP_HEIGHT * m.TILE_SIZE))
    draw.render_map(game_map, pygame, screen, pygame.font.SysFont(None, 22), game_map.player)
    def tile_color(c):
        return tuple(screen.get_at((c.position[0] * m.TILE_SIZE, c.position[1] * m.TILE_SIZE)))[:3]
    assert tile_color(chaser) == m.RED, tile_color(chaser)
    assert tile_color(wanderer) == m.DARK_GRAY and tile_color(orc_chasing_orc) == m.DARK_GRAY
    print("OK rule checks: monsters chasing the player are drawn on red, others on grey")

def check_provoke():
    import draw
    from creatures import Kobold, Golem
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    golem = Golem([0, 0])                                   # wandering, tough enough to survive a hit
    chaser = Kobold([0, 0], CHASE, game_map.player)
    place(game_map, golem, p_x + 1, p_y)
    place(game_map, chaser, p_x - 1, p_y)

    game_map.messages = []
    game_map.move_to(0, [p_x + 1, p_y])                     # the player hits the golem
    assert golem.mood == CHASE and golem.target is game_map.player, "hit golem didn't start chasing"
    assert draw.creature_color(golem, game_map.player) == m.RED
    assert game_map.messages[-1] == "The golem turns to chase you!", game_map.messages

    game_map.messages = []
    game_map.move_to(0, [p_x - 1, p_y])                     # hitting a chaser changes nothing
    assert chaser.target is game_map.player
    assert not any("turns to chase" in s for s in game_map.messages), game_map.messages
    # a grey monster bumping into the player doesn't hit, but turns to chase the player
    from creatures import Gnoll
    wanderer = Gnoll([0, 0])
    place(game_map, wanderer, p_x, p_y + 1)
    health = game_map.player.health
    game_map.messages = []
    game_map.move_to(game_map.creatures.index(wanderer), [p_x, p_y])
    assert game_map.player.health == health, "a grey monster hit the player"
    assert wanderer.mood == CHASE and wanderer.target is game_map.player
    assert game_map.messages == ["The gnoll turns to chase you!"], game_map.messages
    # now it chases the player, so the next bump is a hit
    game_map.move_to(game_map.creatures.index(wanderer), [p_x, p_y])
    assert game_map.player.health == health - wanderer.damage, "the now red gnoll didn't hit"
    print("OK rule checks: a grey monster hit by or bumping into the player starts chasing instead of hitting")

def check_flee():
    import draw
    from look import describe
    from creatures import Kobold
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    kobold = Kobold([0, 0], CHASE, game_map.player)
    place(game_map, kobold, p_x + 1, p_y)
    kobold.health = kobold.health_max = 5

    game_map.messages = []
    game_map.move_to(0, [p_x + 1, p_y])         # the player hits it for 4: 1 health left
    assert kobold.health == 1 and kobold.mood == FLEE and kobold.target is game_map.player, \
        f"kobold at {kobold.health} health has mood {kobold.mood}"
    assert game_map.messages[-1] == "The kobold flees from you!", game_map.messages
    assert draw.creature_color(kobold, game_map.player) == m.YELLOW
    assert describe(kobold, game_map)[1].endswith("It is fleeing from you."), describe(kobold, game_map)

    # it moves away from the player every turn
    i = game_map.creatures.index(kobold)
    def squared_distance():
        return (kobold.position[0] - p_x)**2 + (kobold.position[1] - p_y)**2
    for turn in range(3):
        before = squared_distance()
        monsters.move_moodily(game_map, i)
        assert squared_distance() > before, f"fleeing kobold didn't get farther: {before} -> {squared_distance()}"
    assert kobold.mood == FLEE, "stopped fleeing before full health"

    # back at full health it starts wandering
    kobold.health = kobold.health_max
    monsters.move_moodily(game_map, i)
    assert kobold.mood == WANDER and kobold.target is None, kobold.mood

    # a kobold left at 2 health flees too
    kobold2 = Kobold([0, 0], CHASE, game_map.player)
    place(game_map, kobold2, p_x, p_y + 1)
    kobold2.health = kobold2.health_max = 6
    game_map.move_to(0, [p_x, p_y + 1])
    assert kobold2.health == 2 and kobold2.mood == FLEE, f"kobold at 2 health has mood {kobold2.mood}"

    # other monsters don't flee: an orc left at 1 health turns to chase the player instead
    orc = Orc([0, 0])
    place(game_map, orc, p_x - 1, p_y)
    orc.health = 5
    game_map.move_to(0, [p_x - 1, p_y])
    assert orc.health == 1 and orc.mood == CHASE and orc.target is game_map.player, orc.mood
    print("OK rule checks: kobolds at 2 health or less flee (yellow) until healed, then wander")

def check_friend():
    import draw
    from look import describe
    from creatures import Golem, Gnoll
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    friend = Golem([0, 0], FRIEND, game_map.player)
    place(game_map, friend, p_x + 4, p_y)
    i = game_map.creatures.index(friend)
    assert draw.creature_color(friend, game_map.player) == m.GREEN
    assert describe(friend, game_map)[1].endswith("It is your friend."), describe(friend, game_map)

    # it comes close, then stays close without ever bumping into or hurting the player
    health = game_map.player.health
    for turn in range(30):
        monsters.move_moodily(game_map, i)
        if turn >= 2:
            assert monsters.steps_apart(friend, game_map.player) <= m.CLOSE_STEPS, \
                f"turn {turn}: friend {monsters.steps_apart(friend, game_map.player)} steps away"
    assert game_map.player.health == health and friend.mood == FRIEND, "the friend hurt or turned on the player"

    # next to the player, the friend doesn't stop waiting
    place_next = [p_x + 1, p_y + 1]
    game_map.my_map[friend.position[0]][friend.position[1]] = m.OPEN_SPACE
    friend.position = place_next
    game_map.my_map[place_next[0]][place_next[1]] = friend.sign
    assert monsters.creature_next_to_player(game_map) is None, "the friend counts as someone next to the player"

    # a monster chasing the player comes close: the friend goes for it and attacks it
    orc = Orc([0, 0], CHASE, game_map.player)
    place(game_map, orc, p_x - 2, p_y)
    orc.health = orc.health_max = 20
    assert describe(friend, game_map)[1].endswith("It is defending you."), describe(friend, game_map)
    for turn in range(4):
        monsters.move_moodily(game_map, i)
    assert orc.health < 20, "the friend didn't attack the orc chasing the player"

    # the orc it hit fights back: it turns on the friend, and the friend keeps fighting it
    assert orc.mood == CHASE and orc.target is friend, f"the hit orc has mood {orc.mood}"
    assert "The orc turns on the golem!" in game_map.messages, game_map.messages
    assert game_map.can_attack(orc, friend) and game_map.can_attack(friend, orc)
    orc_health, friend_health = orc.health, friend.health
    for turn in range(4):
        monsters.move_moodily(game_map, game_map.creatures.index(orc))
        monsters.move_moodily(game_map, i)
    assert friend.health < friend_health and orc.health < orc_health, "the orc and the friend didn't fight"
    assert friend.mood == FRIEND, "the friend stopped being a friend"

    # it doesn't attack a monster that isn't chasing the player or itself
    wanderer = Gnoll([0, 0])
    assert not game_map.can_attack(friend, wanderer) and not game_map.can_attack(friend, game_map.player)
    print("OK rule checks: the friendly golem (green) stays close, defends the player, never hurts the player")

def check_golem_flee():
    from creatures import Golem
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    player = game_map.player
    golem = Golem([0, 0], FRIEND, player)
    orc = Orc([0, 0], CHASE, golem)
    place(game_map, golem, p_x + 1, p_y)
    place(game_map, orc, p_x + 2, p_y)
    golem.health_max = 16
    golem.health = 5

    # the orc hits it down to 2 health: it flees from the orc, even though it's the player's friend
    game_map.messages = []
    game_map.move_to(game_map.creatures.index(orc), [p_x + 1, p_y])
    assert golem.health == 2 and golem.mood == FLEE and golem.target is orc, golem.mood
    assert game_map.messages[-1] == "The golem flees from the orc!", game_map.messages
    # while fleeing it's still the player's friend: walking into it asks first, and it doesn't stop waiting
    assert modes.friend_in_direction(game_map, (1, 0)) is golem
    assert monsters.creature_next_to_player(game_map) is None

    # below half health it keeps fleeing; at half health it's the player's friend again
    i = game_map.creatures.index(golem)
    golem.health = 7
    monsters.move_moodily(game_map, i)
    assert golem.mood == FLEE, "stopped fleeing below half health"
    golem.health = 8
    monsters.move_moodily(game_map, i)
    assert golem.mood == FRIEND and golem.target is player, f"after fleeing: {golem.mood}"

    # if what it did before was about a creature that has died since, it wanders instead
    hunter = Golem([0, 0], CHASE, orc)
    hunter.start_fleeing(player)
    orc.alive = False
    hunter.stop_fleeing()
    assert hunter.mood == WANDER and hunter.target is None, hunter.mood
    print("OK rule checks: golems at 2 health or less flee until half health, then go back to their mood")
