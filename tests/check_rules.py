# tests/check_rules.py
# Rule checks: single game rules, checked exactly.

from helpers import *     # pygame, the game's modules (m = map), and the shared helpers

def check_healing():
    player = Player([1, 1])
    player.health = 5
    health_each_turn = []
    for turn in range(60):
        player.heal_slowly()
        health_each_turn.append(player.health)
    # turn 20 is index 19
    assert health_each_turn[18] == 5 and health_each_turn[19] == 6, health_each_turn
    assert health_each_turn[39] == 7 and health_each_turn[59] == 8, health_each_turn

    player.health = player.health_max
    for turn in range(40):
        player.heal_slowly()
    assert player.health == player.health_max, "healed above max"

    orc = Orc([1, 1])
    orc.health = 0
    for turn in range(40):
        orc.heal_slowly()
    assert orc.health == 0, "a dead creature healed"
    print("OK rule checks: healing")

def check_hit_message_texts():
    from creatures import Uruk
    player, orc, orc2, uruk = Player([1, 1]), Orc([1, 1]), Orc([1, 1]), Uruk([1, 1])
    orc.health = orc2.health = 5
    assert player.hit(orc) == ["You hit the orc for 4. It has 1 health left."], player.hit
    assert uruk.hit(player) == ["The uruk hits you for 4. You have 8 health left."]
    assert orc2.hit(orc) == ["The orc hits another orc for 3."], "killing hit should leave out health"
    assert orc.check_death() == "The orc dies!"
    print("OK rule checks: hit and death messages")

def check_run_right_stops_at_wall():
    # a runner in the empty test room, with nothing between it and the room's right wall
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    runner = Orc([0, 0], RUN_RIGHT)
    place(game_map, runner, p_x - 5, p_y + 3)
    for turn in range(m.MAP_WIDTH):
        monsters.move_moodily(game_map, game_map.creatures.index(runner))
        if runner.mood != RUN_RIGHT:
            break
    assert runner.mood == WANDER, "the runner never stopped running right"
    x, y = runner.position
    assert game_map.my_map[x + 1][y] == m.WALL, f"runner stopped at {runner.position}, not by a wall"
    print("OK rule checks: the 'run right' orc starts wandering at a wall")

def check_step_around():
    from creatures import Kobold, Gnoll
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    # kobold three tiles left of the player, gnoll right in its way
    kobold = Kobold([0, 0], CHASE, game_map.player)
    gnoll = Gnoll([0, 0])
    place(game_map, kobold, p_x - 3, p_y)
    place(game_map, gnoll, p_x - 2, p_y)
    gnoll_health = gnoll.health
    monsters.move_moodily(game_map, game_map.creatures.index(kobold))
    k_x, k_y = kobold.position
    assert k_x == p_x - 2 and abs(k_y - p_y) == 1, f"kobold went to {kobold.position}, not around the gnoll"
    assert gnoll.health == gnoll_health, "kobold hit the gnoll"
    print("OK rule checks: a chaser steps around a creature in its way")
