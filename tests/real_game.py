# tests/real_game.py
# Runs myroguelike.py itself for a few seconds without a window.

from helpers import *     # pygame, the game's modules (m = map), and the shared helpers

def run_real_game(seconds=3):
    # count the games started: myroguelike.py creates a new Map for each game
    games_started = [0]
    original_map = m.Map
    # so that the player dies soon and r can be tested: 1 health, and no friend to defend the player
    def counting_map():
        games_started[0] += 1
        game_map = original_map()
        game_map.player.health = 1
        for friend in [c for c in game_map.creatures if c.mood == FRIEND]:
            game_map.my_map[friend.position[0]][friend.position[1]] = m.OPEN_SPACE
            game_map.creatures.remove(friend)
        return game_map
    m.Map = counting_map

    # after each drawn frame, press 5 (wait); every 10th frame press r (play again) instead;
    # close the window after the given time (the game runs at 30 frames per second)
    frames = [0]
    original_flip = pygame.display.flip
    def flip_and_press_keys():
        original_flip()
        frames[0] += 1
        if frames[0] >= seconds * 30:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif frames[0] % 10 == 0:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
        else:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_KP5))
    pygame.display.flip = flip_and_press_keys

    random.seed(1)
    os.chdir(REPO)
    try:
        runpy.run_path(os.path.join(REPO, "myroguelike.py"), run_name="__main__")
    except SystemExit:
        pass    # quit_app() exits the program, which is what should happen
    m.Map = original_map
    pygame.display.flip = original_flip
    assert games_started[0] >= 2, f"only {games_started[0]} game started; pressing r on the death screen didn't restart"
    print(f"OK real game: played {games_started[0]} games in a row (r restarts) and quit")
