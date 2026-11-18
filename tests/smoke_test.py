# tests/smoke_test.py
#
# A quick check that the game still basically works. Run it from anywhere with:
#     python tests/smoke_test.py
# It prints OK lines and totals, or stops with an AssertionError that says what broke.
#
# The checks are in these files, next to this one:
#   check_rules.py     single game rules        check_dungeon.py   generation, paths, sight
#   check_commands.py  what the keys do         check_moods.py     colors, fleeing, friends
#   random_games.py    200 random games         real_game.py       myroguelike.py itself
#   helpers.py         shared setup and helpers

import helpers      # first: sets up pygame without a window
from check_rules import check_healing, check_hit_message_texts, check_run_right_stops_at_wall, check_step_around
from check_dungeon import check_path_through_corridor, check_line_of_sight
from check_commands import check_more_key, check_wait, check_help, check_look, check_look_while_dead, check_attack_friend, check_chat, check_history
from check_moods import check_mood_colors, check_provoke, check_flee, check_friend, check_golem_flee
from random_games import play_random_games
from real_game import run_real_game

check_healing()
check_hit_message_texts()
check_run_right_stops_at_wall()
check_more_key()
check_step_around()
check_path_through_corridor()
check_wait()
check_help()
check_look()
check_look_while_dead()
check_line_of_sight()
check_mood_colors()
check_provoke()
check_flee()
check_friend()
check_golem_flee()
check_attack_friend()
check_chat()
check_history()
play_random_games()
run_real_game()     # last, because quitting the game shuts pygame down
print("All checks passed.")
