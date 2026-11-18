# modes.py
# The modes of the game (playing, waiting, looking, chatting, the death screen...) and what the keys do
# in each. A game turn itself is played by monsters.play_turn.

import sys
from keyboard import read_moves, read_death_screen_key, read_digit
from map import LOG_ROWS, find_creature_at
from creatures import CHASE, FLEE, FRIEND, with_article
from help_texts import COMMAND_LINES, HELP_LINES
from look import visible_creatures, first_look_target, next_in_direction, describe
from chat import says, greeting, has_topics, topic_lines, GOLEM_TOPICS, LOYALTY
from monsters import play_turn, creature_next_to_player

def quit_app(reason, pygame):
    print(reason)
    pygame.quit()
    sys.exit()

def turns_text(turns):
    return str(turns) + (" turn" if turns == 1 else " turns")

# Waiting plays the turns a few frames apart, so each turn can be seen, and speeds up as it goes on.
# The game draws 30 frames a second. Every wait starts with WAIT_START_FRAMES between turns
# (about 3 turns a second); each later gap is WAIT_SPEEDUP times shorter, down to WAIT_MIN_FRAMES.
WAIT_START_FRAMES = 10
WAIT_SPEEDUP = 1.1
WAIT_MIN_FRAMES = 1

# How many frames to wait before playing the given turn of a wait (turn 1 is the first)
def wait_frames_before_turn(turn_number):
    if turn_number <= 2:
        return WAIT_START_FRAMES
    return max(WAIT_MIN_FRAMES, round(WAIT_START_FRAMES / WAIT_SPEEDUP ** (turn_number - 2)))

# Modes: what the keys do right now. Exactly one mode is active, in game_state["mode"];
# handle_events passes each key press to that mode's key handler (KEY_HANDLERS at the end).
PLAY = "play"                   # moving, attacking, and starting the other commands
WAIT_PROMPT = "wait prompt"     # typing how many turns to wait
WAITING = "waiting"             # turns pass by themselves; any key stops
LOOK = "look"                   # a cursor shows creatures
CHOOSE_CHAT = "choose chat"     # a cursor to choose whom to talk to
DIALOGUE = "dialogue"           # choosing a topic to talk about
CONFIRM_ATTACK = "confirm attack"   # y/n: really attack your friend?
DEAD = "dead"                   # the death screen

# The state of one game, apart from the map. Besides the mode, it holds what the modes need:
#   wait_input: digits typed at the wait prompt          waiting: how waiting is going
#   look_target, look_saved_log, mode_before_look: look  chat_target, dialogue: chatting
#   attack_direction: the step that would attack a friend, waiting for y/n
# Each of these is None when its mode isn't active.
def new_game_state():
    return {"mode": PLAY, "wait_input": None, "waiting": None,
            "look_target": None, "look_saved_log": None, "mode_before_look": None,
            "chat_target": None, "dialogue": None, "attack_direction": None}

# The player has died: switch to the death screen
def die(game_map, game_state):
    game_state["mode"] = DEAD
    game_state["waiting"] = None
    game_state["chat_target"] = None
    game_state["dialogue"] = None
    game_map.log_offset = 0
    game_map.messages = ["You died gloriously on the battlefield!",
                         "Killed by " + with_article(game_map.killed_by) + ".",
                         "Thank you for playing. Better luck next time.",
                         "Press 'r' to play again, 'l' to look around or 'q' to quit."]

# Show the next rows of the log, back to the first after the last; no turn passes
def page_log(game_map):
    if len(game_map.messages) > LOG_ROWS:
        game_map.log_offset += LOG_ROWS
        if game_map.log_offset >= len(game_map.messages):
            game_map.log_offset = 0


# --- PLAY mode ---

# The player moves (or stays) one step, and a turn passes
def take_step(game_map, game_state, direction):
    game_map.messages = []
    game_map.log_offset = 0
    if play_turn(game_map, direction):
        die(game_map, game_state)

# The player's friend standing one step away in the given direction, or None
def friend_in_direction(game_map, direction):
    x, y = game_map.player.get_position()
    i = find_creature_at(game_map.creatures, x + direction[0], y + direction[1])
    if i <= 0:                  # -1: nobody there, 0: the player itself (direction (0, 0))
        return None
    creature = game_map.creatures[i]
    if creature.is_friend_of(game_map.player):
        return creature
    return None

def handle_play_key(event_key, typed_char, pygame, game_map, game_state):
    outcome, direction = read_moves(event_key, pygame, typed_char)
    if outcome == "q":
        quit_app("", pygame)
    elif outcome == "more":
        page_log(game_map)
    elif outcome == "m" or outcome == "s":
        # a move key, or 5 to stay: one turn passes. Walking into a friend asks first.
        friend = friend_in_direction(game_map, direction)
        if friend is not None:
            game_state["mode"] = CONFIRM_ATTACK
            game_state["attack_direction"] = direction
            game_map.log_offset = 0
            game_map.messages = ["Really attack your friend, " + friend.called() + "? (y/n)"]
            return
        take_step(game_map, game_state, direction)
    elif outcome == "commands" or outcome == "help":
        # show the commands (?) or the help (h) in the log, m pages through it; no turn passes
        game_map.messages = list(COMMAND_LINES if outcome == "commands" else HELP_LINES)
        game_map.log_offset = 0
    elif outcome == "look":
        start_looking(game_map, game_state)
    elif outcome == "chat":
        start_chat(game_map, game_state)
    elif outcome == "wait":
        # open the prompt for how many turns to wait; no turn passes yet
        game_state["mode"] = WAIT_PROMPT
        game_state["wait_input"] = ""
        game_map.log_offset = 0
        game_map.messages = [WAIT_PROMPT_TEXT + "_" + WAIT_HELP]
    # any other key ("o") does nothing


# --- WAIT_PROMPT and WAITING modes ---

WAIT_PROMPT_TEXT = "Wait how many turns? "
WAIT_HELP = "   (Enter: wait, Esc: cancel)"

# Keys type the number of turns: digits, Backspace, Enter to wait, Esc to cancel
def handle_wait_input(event_key, typed_char, pygame, game_map, game_state):
    typed = game_state["wait_input"]
    digit = read_digit(event_key, pygame)
    if digit is not None and len(typed) < 3:
        typed += digit
    elif event_key == pygame.K_BACKSPACE:
        typed = typed[:-1]
    elif event_key == pygame.K_ESCAPE:
        game_state["wait_input"] = None
        game_state["mode"] = PLAY
        game_map.messages = ["You decide not to wait."]
        return
    elif event_key == pygame.K_RETURN or event_key == pygame.K_KP_ENTER:
        game_state["wait_input"] = None
        game_state["mode"] = PLAY
        if typed == "" or int(typed) == 0:
            game_map.messages = ["You decide not to wait."]
        else:
            start_waiting(game_map, game_state, int(typed))
        return
    game_state["wait_input"] = typed
    game_map.messages = [WAIT_PROMPT_TEXT + typed + "_" + WAIT_HELP]

# Start waiting up to the given number of turns. Waiting doesn't start if a creature is already
# next to the player.
def start_waiting(game_map, game_state, turns):
    game_map.log_offset = 0
    nearby = creature_next_to_player(game_map)
    if nearby is not None:
        game_map.messages = ["You can't wait with " + nearby.called() + " next to you."]
        return
    # frames starts one short, so the first turn is played on the very next frame.
    # stop_at_full_health: waiting started below full health, so stop when full health is reached;
    # waiting started at full health goes on as long as asked.
    player = game_map.player
    game_state["mode"] = WAITING
    game_state["waiting"] = {"turns": turns, "waited": 0, "frames": wait_frames_before_turn(1) - 1, "log": [],
                             "stop_at_full_health": player.health < player.health_max}
    game_map.messages = ["Waiting: 0/" + str(turns) + " turns"]

# End waiting: the log gets the summary first, then the messages of all the waited turns
def finish_waiting(game_map, game_state, summary):
    game_map.messages = [summary] + game_state["waiting"]["log"]
    game_map.log_offset = 0
    game_state["waiting"] = None
    game_state["mode"] = PLAY

# Any key stops waiting, and does nothing else
def handle_waiting_key(event_key, typed_char, pygame, game_map, game_state):
    finish_waiting(game_map, game_state, "You stop waiting after " + turns_text(game_state["waiting"]["waited"]) + ".")

# Called once a frame while waiting. When enough frames have passed, play the next turn; stop when
# all turns are waited, or a creature comes next to the player, or the player reaches full health
# (if waiting started below it), or the player dies.
def continue_waiting(game_map, game_state):
    waiting = game_state["waiting"]
    waiting["frames"] += 1
    if waiting["frames"] < wait_frames_before_turn(waiting["waited"] + 1):
        return
    waiting["frames"] = 0
    waiting["waited"] += 1
    game_map.messages = []
    if play_turn(game_map, (0, 0)):
        die(game_map, game_state)
        return
    turn_messages = game_map.messages
    waiting["log"] += turn_messages
    waited = turns_text(waiting["waited"])
    nearby = creature_next_to_player(game_map)
    player = game_map.player
    if nearby is not None:
        finish_waiting(game_map, game_state, "You stop waiting after " + waited + ": " + nearby.called() + " is next to you.")
    elif waiting["stop_at_full_health"] and player.health >= player.health_max:
        finish_waiting(game_map, game_state, "You stop waiting after " + waited + ": you are at full health.")
    elif waiting["waited"] >= waiting["turns"]:
        finish_waiting(game_map, game_state, "You wait " + waited + ".")
    else:
        # show the progress and this turn's messages
        game_map.messages = ["Waiting: " + str(waiting["waited"]) + "/" + str(waiting["turns"]) + " turns"] + turn_messages
        game_map.log_offset = 0


# --- LOOK mode ---
# The log shows the description while looking, and what it showed before afterwards.
# Looking works from PLAY and from DEAD, and goes back to the mode it came from.

def start_looking(game_map, game_state):
    game_state["mode_before_look"] = game_state["mode"]
    game_state["mode"] = LOOK
    game_state["look_saved_log"] = (game_map.messages, game_map.log_offset)
    target = first_look_target(game_map)
    game_state["look_target"] = target
    game_map.messages = describe(target, game_map)
    game_map.log_offset = 0

def stop_looking(game_map, game_state):
    game_map.messages, game_map.log_offset = game_state["look_saved_log"]
    game_state["mode"] = game_state["mode_before_look"]
    game_state["look_target"] = None
    game_state["look_saved_log"] = None
    game_state["mode_before_look"] = None

# t moves the cursor to the creature the selected one chases, flees from or befriends.
# If it has none, or that one can't be seen, the cursor stays and the log says why.
def jump_to_target(game_map, game_state):
    current = game_state["look_target"]
    target = current.target
    if current.is_player or current.mood not in (CHASE, FLEE, FRIEND) or target is None:
        game_map.messages = describe(current, game_map) + ["It isn't chasing or fleeing anyone."]
    elif not target.alive or target not in visible_creatures(game_map):
        game_map.messages = describe(current, game_map) + ["What it's after is out of sight."]
    else:
        game_state["look_target"] = target
        game_map.messages = describe(target, game_map)

# Direction keys jump to the next visible creature in that direction; no turns pass
def handle_look_input(event_key, typed_char, pygame, game_map, game_state):
    if event_key == pygame.K_l or event_key == pygame.K_ESCAPE:
        stop_looking(game_map, game_state)
        return
    if event_key == pygame.K_t:
        jump_to_target(game_map, game_state)
        return
    outcome, direction = read_moves(event_key, pygame, typed_char)
    if outcome == "q":
        quit_app("", pygame)
    elif outcome == "m":
        next_target = next_in_direction(game_state["look_target"], visible_creatures(game_map), direction)
        if next_target is not None:
            game_state["look_target"] = next_target
            game_map.messages = describe(next_target, game_map)


# --- CHOOSE_CHAT and DIALOGUE modes ---
# Chatting (c) has three steps:
# 1. CHOOSE_CHAT: choose whom to talk to with a cursor like in look mode; no turn passes
# 2. talk: the creature answers, and this takes one turn
# 3. DIALOGUE: golems go on with topics to choose from; choosing takes no turns

def start_chat(game_map, game_state):
    game_map.log_offset = 0
    monsters = visible_creatures(game_map)[1:]
    if not monsters:
        game_map.messages = ["There's nobody to talk to."]
        return
    game_state["mode"] = CHOOSE_CHAT
    game_state["chat_target"] = monsters[0]
    game_map.messages = ["Who do you want to talk to?"] + describe(monsters[0], game_map)

def handle_chat_choice(event_key, typed_char, pygame, game_map, game_state):
    if event_key == pygame.K_ESCAPE:
        game_state["chat_target"] = None
        game_state["mode"] = PLAY
        game_map.messages = ["You decide not to talk."]
        return
    if event_key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_c):
        talk_to(game_map, game_state, game_state["chat_target"])
        return
    outcome, direction = read_moves(event_key, pygame, typed_char)
    if outcome == "q":
        quit_app("", pygame)
    elif outcome == "m":
        monsters = visible_creatures(game_map)[1:]
        next_target = next_in_direction(game_state["chat_target"], monsters, direction)
        if next_target is not None:
            game_state["chat_target"] = next_target
            game_map.messages = ["Who do you want to talk to?"] + describe(next_target, game_map)

def talk_to(game_map, game_state, creature):
    game_state["chat_target"] = None
    game_state["mode"] = PLAY
    game_map.log_offset = 0
    game_map.messages = [greeting(creature)]
    # talking takes a turn: the others move, and their messages follow the talk
    if play_turn(game_map, (0, 0)):
        die(game_map, game_state)
        return
    if has_topics(creature) and creature in game_map.creatures:
        game_state["mode"] = DIALOGUE
        game_state["dialogue"] = creature
        game_map.messages = game_map.messages[:1] + topic_lines(creature) + game_map.messages[1:]

def end_dialogue(game_state):
    game_state["dialogue"] = None
    game_state["mode"] = PLAY

# Keys 1-5 choose a topic, m pages the log, Esc ends the talk
def handle_dialogue(event_key, typed_char, pygame, game_map, game_state):
    creature = game_state["dialogue"]
    digit = read_digit(event_key, pygame)
    if event_key == pygame.K_ESCAPE:
        end_dialogue(game_state)
        game_map.messages = ["You end the talk."]
        game_map.log_offset = 0
    elif event_key == pygame.K_m:
        page_log(game_map)
    elif event_key == pygame.K_q or event_key == pygame.K_x:
        quit_app("", pygame)
    elif digit is not None and 1 <= int(digit) <= len(GOLEM_TOPICS):
        topic = int(digit) - 1
        answer = says(creature, GOLEM_TOPICS[topic][1])
        game_map.log_offset = 0
        if topic == LOYALTY:
            creature.mood = FRIEND
            creature.target = game_map.player
            end_dialogue(game_state)
            game_map.messages = [answer, "The " + creature.name + " is now your friend!"]
        else:
            game_map.messages = [answer] + topic_lines(creature)


# --- CONFIRM_ATTACK mode ---

# y attacks the friend (a turn passes); any other key leaves it be (no turn)
def handle_confirm_attack(event_key, typed_char, pygame, game_map, game_state):
    direction = game_state["attack_direction"]
    game_state["attack_direction"] = None
    game_state["mode"] = PLAY
    if event_key == pygame.K_y:
        take_step(game_map, game_state, direction)
    else:
        game_map.log_offset = 0
        game_map.messages = ["You leave your friend be."]


# --- DEAD mode ---

# r plays again (returns "restart"), l looks around, q quits
def handle_dead_key(event_key, typed_char, pygame, game_map, game_state):
    outcome = read_death_screen_key(event_key, pygame)
    if outcome == "q":
        quit_app("", pygame)
    elif outcome == "r":
        return "restart"
    elif outcome == "l":
        start_looking(game_map, game_state)
    return None


# --- every frame ---

# Which function handles a key press in each mode
KEY_HANDLERS = {
    PLAY: handle_play_key,
    WAIT_PROMPT: handle_wait_input,
    WAITING: handle_waiting_key,
    LOOK: handle_look_input,
    CHOOSE_CHAT: handle_chat_choice,
    DIALOGUE: handle_dialogue,
    CONFIRM_ATTACK: handle_confirm_attack,
    DEAD: handle_dead_key,
}

# Called once a frame: pass each key pressed to the current mode's key handler, and while waiting,
# play the next waited turn when it's time. Return "restart" if the player wants to play again.
def handle_events(pygame, game_map, game_state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app("", pygame)
        if event.type == pygame.KEYDOWN:
            mode_before = game_state["mode"]
            handler = KEY_HANDLERS[mode_before]
            if handler(event.key, getattr(event, "unicode", ""), pygame, game_map, game_state) == "restart":
                return "restart"
            if game_state["mode"] == DEAD and mode_before != DEAD:
                return None         # just died: ignore any further keys pressed in the same frame
    if game_state["mode"] == WAITING:
        continue_waiting(game_map, game_state)
    return None
