# loop_utils.py

import sys
import random
from keyboard import read_moves, read_death_screen_key, read_digit
from map import OPEN_SPACE, WALL, LOG_ROWS, CLOSE_STEPS, find_creature_at
from creatures import CHASE, WANDER, FLEE, FRIEND, RUN_RIGHT, with_article
from help_texts import COMMAND_LINES, HELP_LINES
from look import visible_creatures, first_look_target, next_in_direction, describe
from chat import says, greeting, has_topics, topic_lines, GOLEM_TOPICS, LOYALTY

# The 8 directions in order around a circle, so neighbours in the list are 45 degrees apart
DIRECTIONS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

def quit_app(reason, pygame):
    print(reason)
    pygame.quit()
    sys.exit()

# A chaser's straight step toward its goal (its target, unless another goal is given) may be blocked by
# a wall, or by a creature it won't attack. Then try the two directions next to the straight one, the one
# closer to the goal first, and return the first open one. If both are blocked too, return the straight
# step (which then does nothing).
def step_around_blocker(map, creature, new_position, goal=None):
    if goal is None:
        goal = creature.target
    x, y = new_position
    sign = map.get_sign(x, y)
    if sign == OPEN_SPACE:
        return new_position
    if sign != WALL:
        blocker = map.creatures[find_creature_at(map.creatures, x, y)]
        if map.can_attack(creature, blocker):
            return new_position
    c_x, c_y = creature.get_position()
    t_x, t_y = goal.get_position()
    straight = DIRECTIONS.index((x - c_x, y - c_y))
    options = []
    for turn in (-1, 1):
        dx, dy = DIRECTIONS[(straight + turn) % len(DIRECTIONS)]
        options.append([c_x + dx, c_y + dy])
    random.shuffle(options)     # if both are equally close, pick either
    options.sort(key=lambda p: max(abs(p[0] - t_x), abs(p[1] - t_y)))
    for option in options:
        if map.get_sign(option[0], option[1]) == OPEN_SPACE:
            return option
    return new_position

# A fleeing creature steps to the free neighbouring tile farthest from the one it flees from.
# If no free tile is farther away than where it stands, it stays put.
def flee_step(map, creature):
    c_x, c_y = creature.get_position()
    t_x, t_y = creature.target.get_position()
    def distance(tile):
        return (tile[0] - t_x)**2 + (tile[1] - t_y)**2
    best = [c_x, c_y]
    options = [[c_x + dx, c_y + dy] for dx, dy in DIRECTIONS]
    random.shuffle(options)     # equally far tiles: pick any
    for option in options:
        if map.get_sign(option[0], option[1]) == OPEN_SPACE and distance(option) > distance(best):
            best = option
    return best

def steps_apart(a, b):
    return max(abs(a.position[0] - b.position[0]), abs(a.position[1] - b.position[1]))

# A friendly creature's move:
# 1. if creatures chasing its friend are close to the friend, or creatures chasing itself are close to
#    itself, go for the nearest of them (and attack it when next to it)
# 2. otherwise, if it's farther than CLOSE_STEPS from its friend, walk back toward the friend
# 3. otherwise move around randomly, or stay, without leaving the friend's close area
def friend_step(map, creature):
    friend = creature.target
    threats = map.threats_to(friend) + map.threats_to(creature)
    if threats:
        threat = min(threats, key=lambda t: steps_apart(creature, t))
        return step_around_blocker(map, creature, creature.move_toward(threat), threat)
    if steps_apart(creature, friend) > CLOSE_STEPS:
        return step_around_blocker(map, creature, creature.move_toward(friend), friend)
    c_x, c_y = creature.get_position()
    f_x, f_y = friend.get_position()
    options = [[c_x, c_y]]
    for dx, dy in DIRECTIONS:
        x, y = c_x + dx, c_y + dy
        if map.get_sign(x, y) == OPEN_SPACE and max(abs(x - f_x), abs(y - f_y)) <= CLOSE_STEPS:
            options.append([x, y])
    return random.choice(options)

#   An idea for solving moving a whole array of creatures: implement calling each creature's type of movement by their mood.
def move_moodily(map, creature_i):
    creatures = map.creatures
    creature = creatures[creature_i]
    new_position = creature.get_position()
    death_note = creature.check_death()
    # handle possible creature index of a neighboring death. -1 stands for "no creature killed", otherwise pass the index of the creature to later kill in calling function.
    creature_index = -1
    neighbor_death_note = ""
    if death_note == "":
        if creature.mood == FLEE and (creature.health >= creature.health_max or not creature.target.alive):
            # back at full health, or the one it fled from is dead: stop fleeing and wander
            creature.mood = WANDER
            creature.target = None
        if creature.mood == FRIEND and not creature.target.alive:
            # its friend is dead: wander
            creature.mood = WANDER
            creature.target = None
        if creature.mood == CHASE:
            if creature.target.alive == False:
                creature.mood = WANDER
            else:
                new_position = creature.move_toward(creature.target)
                new_position = step_around_blocker(map, creature, new_position)
        if creature.mood == WANDER:
            new_position = creature.move_random()
        elif creature.mood == RUN_RIGHT:
            new_position = creature.move_right()
            # a wall ahead: running right can't go on, so start wandering from the next turn
            if map.get_sign(new_position[0], new_position[1]) == WALL:
                creature.mood = WANDER
        elif creature.mood == FLEE:
            new_position = flee_step(map, creature)
        elif creature.mood == FRIEND:
            new_position = friend_step(map, creature)
        map.move_to(creature_i, new_position)
        #I need to check here if the hit creature died, and return the data if they did
        neighbor_death_note, creature_index = map.check_death_for_coords(new_position[0], new_position[1])
    return death_note, neighbor_death_note, creature_index

# Check every creature for death and remove the dead from the map.
# If other_creatures_move is True, the non-player creatures take their turn first.
# Death notes are added to game_map.messages. Return True if the player died.
def check_deaths(game_map, other_creatures_move):
    dying = []
    player_died = False

    def mark_dead(i, death_note):
        nonlocal player_died
        if i == 0:
            player_died = True
        elif i not in dying:
            dying.append(i)
            game_map.creatures[i].alive = False
            game_map.messages.append(death_note)

    if other_creatures_move:
        for i in range(1, len(game_map.creatures)):                     # don't move the player in a loop
            death_note, neighbor_death_note, neighbor_creature_index = move_moodily(game_map, i)
            if neighbor_death_note != "":
                if neighbor_creature_index == 0:
                    game_map.killed_by = game_map.creatures[i].name
                mark_dead(neighbor_creature_index, neighbor_death_note)
            if death_note != "":
                mark_dead(i, death_note)
            if player_died:
                break
    else:
        for i in range(0, len(game_map.creatures)):
            death_note = game_map.creatures[i].check_death()
            if death_note != "":
                mark_dead(i, death_note)

    # remove from the highest index down, so removing one doesn't shift the indexes of the rest
    for i in sorted(dying, reverse=True):
        death_location = game_map.creatures[i].get_position()
        game_map.my_map[death_location[0]][death_location[1]] = OPEN_SPACE
        game_map.creatures.pop(i)
    return player_died

# One game turn: the player moves (or stays, with direction (0, 0)), then the other creatures move,
# then everyone still alive heals a little. Messages are added to game_map.messages.
# Return True if the player died.
def play_turn(game_map, direction):
    x, y = game_map.player.get_position()
    new_position = [x + direction[0], y + direction[1]]
    # move creature_0, the player
    if game_map.move_to(0, new_position):
        check_deaths(game_map, False)       # check if player killed anyone
    if check_deaths(game_map, True):        # have all creatures move and check if they killed anyone
        return True
    for creature in game_map.creatures:
        creature.heal_slowly()
    return False

# Return a creature standing next to the player (in any of the 8 directions), or None.
# The player's friends don't count.
def creature_next_to_player(game_map):
    p_x, p_y = game_map.player.get_position()
    for creature in game_map.creatures[1:]:
        if creature.mood == FRIEND and creature.target is game_map.player:
            continue
        x, y = creature.get_position()
        if max(abs(x - p_x), abs(y - p_y)) == 1:
            return creature
    return None

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
DEAD = "dead"                   # the death screen

# The state of one game, apart from the map. Besides the mode, it holds what the modes need:
#   wait_input: digits typed at the wait prompt          waiting: how waiting is going
#   look_target, look_saved_log, mode_before_look: look  chat_target, dialogue: chatting
# Each of these is None when its mode isn't active.
def new_game_state():
    return {"mode": PLAY, "wait_input": None, "waiting": None,
            "look_target": None, "look_saved_log": None, "mode_before_look": None,
            "chat_target": None, "dialogue": None}

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

def handle_play_key(event_key, typed_char, pygame, game_map, game_state):
    outcome, direction = read_moves(event_key, pygame, typed_char)
    if outcome == "q":
        quit_app("", pygame)
    elif outcome == "more":
        page_log(game_map)
    elif outcome == "m" or outcome == "s":
        # a move key, or 5 to stay: one turn passes
        game_map.messages = []
        game_map.log_offset = 0
        if play_turn(game_map, direction):
            die(game_map, game_state)
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
