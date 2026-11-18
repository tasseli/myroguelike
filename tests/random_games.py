# tests/random_games.py
# 200 seeded games of random key presses through the real handle_events, checking after
# every turn that the game still makes sense.

from helpers import *     # pygame, the game's modules (m = map), and the shared helpers
from check_dungeon import check_generation, check_starting_creatures, check_spawns

# Things that must always be true between turns
def check_consistency(game_map):
    assert game_map.creatures[0] is game_map.player, "the player is not first in the list"
    positions = [tuple(c.position) for c in game_map.creatures]
    assert len(set(positions)) == len(positions), "two creatures share a tile"
    for c in game_map.creatures:
        x, y = c.position
        assert game_map.my_map[x][y] == c.sign, f"{c.name} at {x},{y} but map has {game_map.my_map[x][y]!r}"
        assert c.alive, f"a dead {c.name} is still in the list"
        assert c.health <= c.health_max, f"{c.name} has more than max health"
    creature_tiles = sum(1 for column in game_map.my_map for tile in column
                         if tile not in (m.OPEN_SPACE, m.WALL))
    assert creature_tiles == len(game_map.creatures), \
        f"{creature_tiles} creature tiles on the map, but {len(game_map.creatures)} creatures"

def is_hit_message(message):
    return message.startswith("You hit ") or " hits " in message

def check_hit_messages(messages):
    for message in messages:
        if is_hit_message(message):
            # the player is in every hit, except orcs hitting their target orc
            assert message.startswith("You hit ") or " hits you " in message \
                or message.startswith("The orc hits another orc "), "attack against the rules: " + message

def play_random_games(games=200, max_turns=300):
    totals = {"turns": 0, "hits": 0, "deaths": 0, "heals": 0, "player deaths": 0}
    # remember the log of the turn the player dies on, before die() replaces it with the death screen
    last_turn_before_death = [[]]
    original_die = modes.die
    def remembering_die(game_map, game_state):
        last_turn_before_death[0] = list(game_map.messages)
        original_die(game_map, game_state)
    modes.die = remembering_die
    for game in range(games):
        random.seed(game)       # same games every run, so results can be compared and repeated
        game_map = m.Map()
        check_generation(game_map)
        check_starting_creatures(game_map)
        check_spawns(game_map)
        check_consistency(game_map)
        game_state = modes.new_game_state()
        for turn in range(max_turns):
            health_before = {id(c): c.health for c in game_map.creatures}
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=random.choice(KEYS)))
            modes.handle_events(pygame, game_map, game_state)
            # on the turn the player dies, the log shows the death screen; count that turn's messages instead
            turn_messages = last_turn_before_death[0] if game_state["mode"] == modes.DEAD else game_map.messages
            totals["turns"] += 1
            totals["hits"] += sum(is_hit_message(s) for s in turn_messages)
            totals["deaths"] += sum("dies!" in s for s in turn_messages)
            check_hit_messages(turn_messages)
            if game_state["mode"] == modes.DEAD:
                assert game_map.player.health < 1, "game ended but the player is alive"
                killers = {"orc", "uruk", "kobold", "gnoll", "goblin", "golem"}
                assert game_map.killed_by in killers, f"killed_by is {game_map.killed_by!r}"
                totals["player deaths"] += 1
                break
            assert game_map.player.health >= 1, "player at 0 health but the game goes on"
            for c in game_map.creatures:
                if c.health > health_before.get(id(c), c.health):
                    assert c.health == health_before[id(c)] + 1, f"{c.name} healed more than 1"
                    totals["heals"] += 1
            check_consistency(game_map)
    modes.die = original_die
    print(f"OK random games: {games} games, " + ", ".join(f"{v} {k}" for k, v in totals.items()))
