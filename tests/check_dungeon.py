# tests/check_dungeon.py
# Dungeon checks: generation, where creatures start, finding the way, and line of sight.

from helpers import *     # pygame, the game's modules (m = map), and the shared helpers

# Two rooms within the size limits, left one in the left half and right one in the right half,
# joined by a straight corridor; every floor tile can be walked to from every other one
def check_generation(game_map):
    assert len(game_map.rooms) == 2
    (l1, t1, r1, b1), (l2, t2, r2, b2) = game_map.rooms
    for left, top, right, bottom in game_map.rooms:
        assert m.ROOM_MIN_WIDTH <= right - left <= m.ROOM_MAX_WIDTH, f"room width {right - left}"
        assert m.ROOM_MIN_HEIGHT <= bottom - top <= m.ROOM_MAX_HEIGHT, f"room height {bottom - top}"
        assert left >= 1 and top >= 1 and right <= m.MAP_WIDTH - 1 and bottom <= m.MAP_HEIGHT - 1, "room touches the edge"
    assert r1 <= m.MAP_WIDTH // 2 < l2, "the rooms aren't in the left and right halves"
    corridor = game_map.corridor
    rows = {y for x, y in corridor}
    assert len(rows) == 1, "the corridor isn't straight"
    y = rows.pop()
    assert t1 <= y < b1 and t2 <= y < b2, "the corridor isn't on a row both rooms share"
    assert [x for x, _ in corridor] == list(range(r1, l2)), "the corridor doesn't run from room to room"
    # flood fill from one floor tile: it must reach every floor tile (creatures stand on floor too)
    floor = {(x, y) for x in range(m.MAP_WIDTH) for y in range(m.MAP_HEIGHT) if game_map.my_map[x][y] != m.WALL}
    start = next(iter(floor))
    reached, todo = {start}, [start]
    while todo:
        x, y = todo.pop()
        for dx, dy in monsters.DIRECTIONS:
            tile = (x + dx, y + dy)
            if tile in floor and tile not in reached:
                reached.add(tile)
                todo.append(tile)
    assert reached == floor, f"{len(floor - reached)} floor tiles can't be reached"

def check_spawns(game_map):
    room_tiles = [(x, y) for left, top, right, bottom in game_map.rooms
                  for x in range(left, right) for y in range(top, bottom)]
    for c in game_map.creatures:
        assert tuple(c.position) in room_tiles, f"{c.name} spawned outside the rooms, at {c.position}"
    px, py = game_map.player.position
    def moves_from_player(x, y):
        return max(abs(x - px), abs(y - py))
    # the near golem (added right after the player) starts NEAR_GOLEM_SPAWN_DISTANCE moves away,
    # if the rooms have a tile that far
    near_golem = game_map.creatures[1]
    assert near_golem.name == "golem"
    if any(moves_from_player(x, y) == m.NEAR_GOLEM_SPAWN_DISTANCE for x, y in room_tiles):
        assert moves_from_player(*near_golem.position) == m.NEAR_GOLEM_SPAWN_DISTANCE, \
            f"near golem spawned {moves_from_player(*near_golem.position)} moves from the player"
    # monsters start at least MIN_SPAWN_DISTANCE moves away, if the rooms have enough such tiles
    monsters = [c for c in game_map.creatures[1:] if c is not near_golem]
    far_tiles = sum(1 for x, y in room_tiles if moves_from_player(x, y) >= m.MIN_SPAWN_DISTANCE)
    if far_tiles >= len(monsters):
        for c in monsters:
            distance = moves_from_player(*c.position)
            assert distance >= m.MIN_SPAWN_DISTANCE, f"{c.name} spawned {distance} moves from the player"

def check_starting_creatures(game_map):
    kobolds = [c for c in game_map.creatures if c.name == "kobold"]
    hostile = [k for k in kobolds if k.mood == CHASE and k.target is game_map.player]
    wandering = [k for k in kobolds if k.mood == WANDER]
    assert len(kobolds) == 4 and len(hostile) == 2 and len(wandering) == 2, \
        f"{len(kobolds)} kobolds: {len(hostile)} hostile, {len(wandering)} wandering"
    assert not [c for c in game_map.creatures if c.mood == FRIEND], "nobody should start as a friend"
    golems = [c for c in game_map.creatures if c.name == "golem"]
    assert len(golems) == 2 and all(g.mood == WANDER for g in golems), "there should be two wandering golems"

# Press keys one after another; game_state is kept between them (e.g. an open wait prompt)
def check_path_through_corridor():
    from creatures import Kobold
    for seed in range(20):
        random.seed(seed)
        game_map = m.Map()
        for c in game_map.creatures:
            game_map.my_map[c.position[0]][c.position[1]] = m.OPEN_SPACE
        game_map.creatures = []
        # the player in the middle of the left room, a chaser in the middle of the right room
        (l1, t1, r1, b1), (l2, t2, r2, b2) = game_map.rooms
        player = game_map.player
        place(game_map, player, (l1 + r1) // 2, (t1 + b1) // 2)
        kobold = Kobold([0, 0], CHASE, player)
        place(game_map, kobold, (l2 + r2) // 2, (t2 + b2) // 2)
        walk = game_map.distances_to(player)[tuple(kobold.position)]
        # with nobody in the way, it takes the shortest way: next to the player after walk - 1 turns
        for turn in range(walk - 1):
            monsters.move_moodily(game_map, 1)
        assert monsters.steps_apart(kobold, player) == 1, \
            f"seed {seed}: after {walk - 1} turns the kobold is at {kobold.position}, player at {player.position}"
    # in the corridor there's no room to step aside: a chaser swaps places with a wanderer in its way
    from creatures import Gnoll
    seed = 0
    while True:
        random.seed(seed)
        game_map = m.Map()
        if len(game_map.corridor) >= 3:
            break
        seed += 1
    for c in game_map.creatures:
        game_map.my_map[c.position[0]][c.position[1]] = m.OPEN_SPACE
    game_map.creatures = []
    (l2, t2, r2, b2) = game_map.rooms[1]
    place(game_map, game_map.player, (l2 + r2) // 2, (t2 + b2) // 2)
    behind, ahead = game_map.corridor[-3], game_map.corridor[-2]
    kobold = Kobold([0, 0], CHASE, game_map.player)
    gnoll = Gnoll([0, 0])
    place(game_map, kobold, *behind)
    place(game_map, gnoll, *ahead)
    monsters.move_moodily(game_map, game_map.creatures.index(kobold))
    assert kobold.position == list(ahead) and gnoll.position == list(behind), \
        f"no swap: kobold at {kobold.position}, gnoll at {gnoll.position}"
    assert game_map.my_map[ahead[0]][ahead[1]] == "k" and game_map.my_map[behind[0]][behind[1]] == "n"

    # two chasers after the same target in single file, the rear one moving first: they mustn't swap
    # back and forth (which kept both in place). The rear one waits one turn for the front one to move
    # on, then follows: after two turns both are closer to the player
    for c in (kobold, gnoll):
        game_map.my_map[c.position[0]][c.position[1]] = m.OPEN_SPACE
        game_map.creatures.remove(c)
    rear = Gnoll([0, 0], CHASE, game_map.player)
    front = Gnoll([0, 0], CHASE, game_map.player)
    place(game_map, rear, *behind)      # added first, so it moves first
    place(game_map, front, *ahead)
    distances = game_map.distances_to(game_map.player)
    before = [distances[tuple(rear.position)], distances[tuple(front.position)]]
    for turn in range(2):
        for i in (1, 2):
            monsters.move_moodily(game_map, i)
    after = [distances[tuple(rear.position)], distances[tuple(front.position)]]
    assert after[0] < before[0] and after[1] < before[1], f"walking distances {before} -> {after}"
    print("OK rule checks: chasers find the shortest way through the corridor, swapping past others there")

def check_line_of_sight():
    import draw
    from look import visible_creatures
    from creatures import Kobold
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position                      # (40, 20)
    # a wall 3 tiles to the right of the player, 9 tiles high, and a kobold behind it
    for y in range(p_y - 4, p_y + 5):
        game_map.my_map[p_x + 3][y] = m.WALL
    game_map.view_cache = {}
    kobold = Kobold([0, 0], CHASE, game_map.player)
    place(game_map, kobold, p_x + 6, p_y)
    visible = game_map.visible_tiles(game_map.player)
    assert (p_x + 3, p_y) in visible, "the wall itself should be visible"
    assert (p_x + 6, p_y) not in visible, "a tile behind the wall is visible"
    assert (p_x - 6, p_y) in visible and (p_x, p_y - 6) in visible, "open tiles nearby aren't visible"
    assert kobold not in visible_creatures(game_map), "look can pick a creature behind a wall"

    # drawn: the kobold behind the wall isn't; after moving away, the seen wall is remembered, dim
    screen = pygame.display.set_mode((m.MAP_WIDTH * m.TILE_SIZE, m.MAP_HEIGHT * m.TILE_SIZE))
    font = pygame.font.SysFont(None, 22)
    def background(x, y):
        return tuple(screen.get_at((x * m.TILE_SIZE, y * m.TILE_SIZE)))[:3]
    screen.fill(m.GRAY)
    draw.render_map(game_map, pygame, screen, font, game_map.player)
    assert background(p_x + 3, p_y) == m.DARK_GRAY and background(p_x + 6, p_y) == m.GRAY, "wall or kobold drawn wrong"
    assert (p_x + 3, p_y) in game_map.seen
    game_map.my_map[p_x][p_y] = m.OPEN_SPACE
    game_map.player.position = [27, 10]                       # far away, the wall is out of view
    game_map.my_map[27][10] = "@"
    screen.fill(m.GRAY)
    draw.render_map(game_map, pygame, screen, font, game_map.player)
    assert (p_x + 3, p_y) not in game_map.visible_tiles(game_map.player)
    assert background(p_x + 3, p_y) == m.REMEMBERED_WALL, f"remembered wall drawn {background(p_x + 3, p_y)}"
    print("OK rule checks: walls block the view; seen tiles are remembered and drawn dim")
