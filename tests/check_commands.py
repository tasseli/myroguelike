# tests/check_commands.py
# Command checks: what the keys do (m, w, ?, h, l, c, and attacking a friend).

from helpers import *     # pygame, the game's modules (m = map), and the shared helpers

def check_more_key():
    random.seed(0)
    game_map = m.Map()
    messages = ["message " + str(i) for i in range(1, 10)]     # 9 messages: pages 1-4, 5-8, 9
    game_map.messages = list(messages)
    positions = [list(c.position) for c in game_map.creatures]
    offsets = []
    for i in range(4):
        press(game_map, pygame.K_m)
        offsets.append(game_map.log_offset)
    assert offsets == [4, 8, 0, 4], f"More went through offsets {offsets}"
    assert game_map.messages == messages, "More changed the messages"
    assert [list(c.position) for c in game_map.creatures] == positions, "More used up a turn"

    # every page draws without errors
    import draw
    font = pygame.font.SysFont(None, 22)
    for offset in (0, 4, 8):
        draw.render_message_log(messages, offset, pygame, pygame.display.get_surface(), font)

    # a new turn starts the log from its first row
    press(game_map, pygame.K_KP5)
    assert game_map.log_offset == 0, "a new turn didn't reset the log to the first row"

    # with no more messages than rows, More does nothing
    game_map.messages = ["a", "b", "c", "d"]
    press(game_map, pygame.K_m)
    assert game_map.log_offset == 0, "More moved a log that fits on the screen"
    print("OK rule checks: the More key pages through the log without using a turn")

def check_wait():
    from creatures import Kobold
    gap = modes.wait_frames_before_turn
    start = modes.WAIT_START_FRAMES

    # the pace: starts at WAIT_START_FRAMES between turns, never slows down, gets clearly faster
    gaps = [gap(turn) for turn in range(2, 101)]
    assert gaps[0] == start, gaps[:3]
    assert all(later <= earlier for earlier, later in zip(gaps, gaps[1:])), "waiting slowed down"
    assert gaps[-1] == modes.WAIT_MIN_FRAMES, "long waits never reach full speed"

    # nobody around: wait the full 20 turns and heal 1
    game_map = empty_room_map()
    state = modes.new_game_state()
    game_map.player.health = 5
    press(game_map, pygame.K_w, pygame.K_2, pygame.K_KP0, pygame.K_RETURN, game_state=state)
    assert state["wait_input"] is None, "the prompt stayed open"
    # the first turn is played on the same frame as Enter, and shown
    assert game_map.messages[0] == "Waiting: 1/20 turns", game_map.messages
    frames = run_frames_while_waiting(game_map, state)
    expected = sum(gap(turn) for turn in range(2, 21))
    assert frames == expected, f"the other 19 turns took {frames} frames, not {expected}"
    assert frames < 19 * start, "waiting didn't speed up"
    assert game_map.messages[0] == "You wait 20 turns.", game_map.messages

    # the next wait starts at the original pace again: turn 2 comes after WAIT_START_FRAMES frames
    press(game_map, pygame.K_w, pygame.K_5, pygame.K_RETURN, game_state=state)
    for frame in range(start - 1):
        modes.handle_events(pygame, game_map, state)
    assert game_map.messages[0] == "Waiting: 1/5 turns", game_map.messages
    modes.handle_events(pygame, game_map, state)
    assert game_map.messages[0] == "Waiting: 2/5 turns", game_map.messages
    run_frames_while_waiting(game_map, state)
    assert game_map.player.health == 6, "didn't heal while waiting 20 turns"

    # started below full health: stop when full health is reached (1 health short heals in 20 turns)
    full_map = empty_room_map()
    full_state = modes.new_game_state()
    full_map.player.health = full_map.player.health_max - 1
    press(full_map, pygame.K_w, pygame.K_5, pygame.K_0, pygame.K_RETURN, game_state=full_state)
    run_frames_while_waiting(full_map, full_state)
    assert full_map.messages[0] == "You stop waiting after 20 turns: you are at full health.", full_map.messages
    # started at full health: wait as long as asked
    press(full_map, pygame.K_w, pygame.K_2, pygame.K_5, pygame.K_RETURN, game_state=full_state)
    run_frames_while_waiting(full_map, full_state)
    assert full_map.messages[0] == "You wait 25 turns.", full_map.messages

    # typing: backspace removes a digit, Esc cancels without using a turn
    press(game_map, pygame.K_w, pygame.K_1, pygame.K_2, pygame.K_BACKSPACE, game_state=state)
    assert state["wait_input"] == "1", state
    turns_until_heal = game_map.player.turns_until_heal
    press(game_map, pygame.K_ESCAPE, game_state=state)
    assert state["wait_input"] is None and game_map.messages == ["You decide not to wait."]
    assert game_map.player.turns_until_heal == turns_until_heal, "cancelling used up a turn"

    # a kobold comes: stop right when it's next to the player, before it can hit
    p_x, p_y = game_map.player.position
    kobold = Kobold([0, 0], CHASE, game_map.player)
    place(game_map, kobold, p_x - 5, p_y)
    health = game_map.player.health
    press(game_map, pygame.K_w, pygame.K_5, pygame.K_0, pygame.K_RETURN, game_state=state)
    run_frames_while_waiting(game_map, state)
    assert game_map.messages[0] == "You stop waiting after 4 turns: the kobold is next to you.", game_map.messages
    assert monsters.creature_next_to_player(game_map) is kobold
    assert game_map.player.health == health, "the kobold got to hit while the player waited"

    # someone already next to the player: don't wait at all
    kobold_position = list(kobold.position)
    press(game_map, pygame.K_w, pygame.K_9, pygame.K_RETURN, game_state=state)
    assert game_map.messages == ["You can't wait with the kobold next to you."], game_map.messages
    assert kobold.position == kobold_position, "a turn passed although waiting was refused"
    assert state.get("waiting") is None, "waiting started although it was refused"

    # any key stops waiting, and that key does nothing else
    game_map = empty_room_map()
    state = modes.new_game_state()
    press(game_map, pygame.K_w, pygame.K_9, pygame.K_9, pygame.K_RETURN, game_state=state)    # turn 1
    for frame in range(gap(2) + gap(3)):                                                      # turns 2 and 3
        modes.handle_events(pygame, game_map, state)
    assert game_map.messages[0] == "Waiting: 3/99 turns", game_map.messages
    position = list(game_map.player.position)
    press(game_map, pygame.K_LEFT, game_state=state)
    assert state["waiting"] is None and game_map.messages[0] == "You stop waiting after 3 turns.", game_map.messages
    assert game_map.player.position == position, "the key that stopped waiting also moved the player"
    assert game_map.player.turns_until_heal == game_map.player.heal_interval - 3, "more turns passed than shown"
    print("OK rule checks: w starts at about 3 turns a second and speeds up, heals, stops when someone comes next or a key is pressed")

def check_help():
    from help_texts import COMMAND_LINES, HELP_LINES, KEY_HINTS, WAIT_KEY_HINTS, LOOK_KEY_HINTS, DEATH_KEY_HINTS
    from help_texts import CHAT_KEY_HINTS, DIALOGUE_KEY_HINTS, CONFIRM_KEY_HINTS
    game_map = empty_room_map()
    turns_until_heal = game_map.player.turns_until_heal

    # '?' is recognised by the character typed (here Shift + slash, as on a US keyboard)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SLASH, unicode="?"))
    modes.handle_events(pygame, game_map, modes.new_game_state())
    assert game_map.messages == COMMAND_LINES, "? didn't show the commands"
    press(game_map, pygame.K_m)
    assert game_map.log_offset == 4, "m didn't page the commands"

    press(game_map, pygame.K_h)
    assert game_map.messages == HELP_LINES and game_map.log_offset == 0, "h didn't show the help from the start"
    press(game_map, pygame.K_m)
    assert game_map.log_offset == 4, "m didn't page the help"
    assert game_map.player.turns_until_heal == turns_until_heal, "showing the help used up a turn"

    # ? lists only the commands for any turn; how things work (healing, attacking, r after dying) is in h
    for topic in ("heal", "attack", "r plays again"):
        assert not any(topic in line.lower() for line in COMMAND_LINES), f"'{topic}' belongs in h, not ?"
        assert any(topic in line.lower() for line in HELP_LINES), f"h doesn't mention '{topic}'"

    # the texts fit: a line plus its row number must end before the More indicator
    for line in COMMAND_LINES + HELP_LINES:
        assert len(line) <= 52, f"help line too long ({len(line)} characters): {line}"
    for hints in (KEY_HINTS, WAIT_KEY_HINTS, LOOK_KEY_HINTS, CHAT_KEY_HINTS, DIALOGUE_KEY_HINTS, CONFIRM_KEY_HINTS, DEATH_KEY_HINTS):
        assert len(hints) <= m.MAP_WIDTH - 2, f"key hints don't fit on one row ({len(hints)} characters)"
    print("OK rule checks: ? shows the commands, h the help, m pages them, no turn used")

def check_look():
    from creatures import Kobold, Gnoll, Golem
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    kobold = Kobold([0, 0], CHASE, game_map.player)
    gnoll = Gnoll([0, 0])
    golem = Golem([0, 0])
    place(game_map, kobold, p_x + 3, p_y)       # nearest
    place(game_map, gnoll, p_x, p_y - 4)
    place(game_map, golem, min(p_x + 16, m.MAP_WIDTH - 2), p_y)    # too far away to see
    game_map.messages = ["before looking"]
    state = modes.new_game_state()
    turns_until_heal = game_map.player.turns_until_heal

    press(game_map, pygame.K_l, game_state=state)
    assert state["look_target"] is kobold, "look didn't start on the nearest monster"
    assert game_map.messages == ["Looking at: a kobold (k), 3 steps away.",
                                 "Health " + str(kobold.health) + "/" + str(kobold.health_max) + ". It is chasing you."], game_map.messages
    press(game_map, pygame.K_RIGHT, game_state=state)
    assert state["look_target"] is kobold, "jumped to a creature the player can't see"
    press(game_map, pygame.K_LEFT, game_state=state)
    assert state["look_target"] is game_map.player and game_map.messages[0] == "Looking at: you (@)."
    press(game_map, pygame.K_KP8, game_state=state)
    assert state["look_target"] is gnoll and "wandering" in game_map.messages[1], game_map.messages
    press(game_map, pygame.K_KP3, game_state=state)     # down-right from the gnoll: the kobold
    assert state["look_target"] is kobold

    press(game_map, pygame.K_ESCAPE, game_state=state)
    assert state["look_target"] is None and game_map.messages == ["before looking"], "log not put back"
    assert game_map.player.turns_until_heal == turns_until_heal, "looking used up a turn"
    assert kobold.position == [p_x + 3, p_y], "creatures moved while looking"

    # a target other than the player is told with its distance and direction
    from look import describe
    leader = Orc([0, 0], CHASE, game_map.player)
    follower = Orc([0, 0], CHASE, leader)
    place(game_map, follower, p_x + 2, p_y + 2)
    place(game_map, leader, p_x - 1, p_y - 1)     # 3 steps up-left of the follower
    line = describe(follower, game_map)[1]
    assert line.endswith("It is chasing the orc 3 steps up-left of it."), line
    assert describe(leader, game_map)[1].endswith("It is chasing you."), describe(leader, game_map)

    # t follows the chain: follower -> leader -> player; the player has no target
    press(game_map, pygame.K_l, game_state=state)
    state["look_target"] = follower     # put the look cursor on the follower
    press(game_map, pygame.K_t, game_state=state)
    assert state["look_target"] is leader, "t didn't jump to the orc it chases"
    press(game_map, pygame.K_t, game_state=state)
    assert state["look_target"] is game_map.player, "t didn't jump to the player"
    press(game_map, pygame.K_t, game_state=state)
    assert state["look_target"] is game_map.player and game_map.messages[-1] == "It isn't chasing or fleeing anyone."
    # a wanderer has no target either; a target out of sight can't be jumped to
    state["look_target"] = gnoll
    press(game_map, pygame.K_t, game_state=state)
    assert state["look_target"] is gnoll and game_map.messages[-1] == "It isn't chasing or fleeing anyone."
    leader.position = [golem.position[0], golem.position[1] - 1]   # out of sight (the map tile isn't updated)
    state["look_target"] = follower
    press(game_map, pygame.K_t, game_state=state)
    assert state["look_target"] is follower and game_map.messages[-1] == "What it's after is out of sight.", game_map.messages
    press(game_map, pygame.K_ESCAPE, game_state=state)

    # with no monster in sight, looking starts on the player; l also stops looking
    lonely = empty_room_map()
    press(lonely, pygame.K_l, game_state=state)
    assert state["look_target"] is lonely.player
    press(lonely, pygame.K_l, game_state=state)
    assert state["look_target"] is None
    print("OK rule checks: l looks at visible creatures, direction keys jump between them")

def check_look_while_dead():
    from creatures import Uruk
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    uruk = Uruk([0, 0], CHASE, game_map.player)
    place(game_map, uruk, p_x + 1, p_y)
    game_map.player.health = -2                 # dead
    game_map.killed_by = "uruk"
    state = modes.new_game_state()
    modes.die(game_map, state)
    assert state["mode"] == modes.DEAD and game_map.messages[1] == "Killed by an uruk.", game_map.messages

    def death_screen_keys(*keys):
        result = None
        for key in keys:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
            result = modes.handle_events(pygame, game_map, state)
        return result

    assert death_screen_keys(pygame.K_l) is None and state["look_target"] is uruk, "l didn't look at the killer"
    death_screen_keys(pygame.K_LEFT)
    assert state["look_target"] is game_map.player
    assert game_map.messages == ["Looking at: you (@).", "Health 0/12."], game_map.messages
    death_screen_keys(pygame.K_ESCAPE)
    assert state["look_target"] is None and state["mode"] == modes.DEAD, "Esc didn't go back to the death screen"
    assert game_map.messages[1] == "Killed by an uruk.", "the death screen text didn't come back"
    assert death_screen_keys(pygame.K_r) == "restart", "r didn't restart after looking"
    print("OK rule checks: l looks around on the death screen")

def check_attack_friend():
    from creatures import Golem
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    friend = Golem([0, 0], FRIEND, game_map.player)
    place(game_map, friend, p_x + 1, p_y)
    state = modes.new_game_state()
    player = game_map.player
    health, turns = friend.health, player.turns_until_heal

    # walking into the friend asks first, and takes no turn
    press(game_map, pygame.K_RIGHT, game_state=state)
    assert state["mode"] == modes.CONFIRM_ATTACK, state["mode"]
    assert game_map.messages == ["Really attack your friend, the golem? (y/n)"], game_map.messages
    # n: nothing happens
    press(game_map, pygame.K_n, game_state=state)
    assert state["mode"] == modes.PLAY and game_map.messages == ["You leave your friend be."]
    assert friend.health == health and player.turns_until_heal == turns, "saying no hurt the friend or took a turn"
    # y: the player attacks, a turn passes, and the friend turns on the player
    press(game_map, pygame.K_RIGHT, pygame.K_y, game_state=state)
    assert friend.health == health - player.damage, "saying yes didn't attack the friend"
    assert friend.mood == CHASE and friend.target is player and player.turns_until_heal == turns - 1
    print("OK rule checks: walking into your friend asks y/n before attacking")

def check_chat():
    import chat
    from creatures import Golem, Kobold
    game_map = empty_room_map()
    p_x, p_y = game_map.player.position
    golem = Golem([0, 0])
    kobold = Kobold([0, 0])
    place(game_map, golem, p_x + 2, p_y)
    place(game_map, kobold, p_x - 3, p_y)
    state = modes.new_game_state()
    player = game_map.player
    def turns_passed(before):
        return before - player.turns_until_heal

    # c asks whom to talk to, starting from the nearest; choosing takes no turn
    before = player.turns_until_heal
    press(game_map, pygame.K_c, game_state=state)
    assert state["chat_target"] is golem and game_map.messages[0] == "Who do you want to talk to?"
    press(game_map, pygame.K_LEFT, game_state=state)
    assert state["chat_target"] is kobold
    assert turns_passed(before) == 0, "choosing whom to talk to took a turn"

    # talking takes one turn; a kobold just answers
    press(game_map, pygame.K_RETURN, game_state=state)
    assert game_map.messages[0] == "The kobold: Beep beep, I'm a kobold.", game_map.messages
    assert state["chat_target"] is None and state.get("dialogue") is None
    assert turns_passed(before) == 1, "talking didn't take exactly one turn"

    # a golem answers, then asks for a topic; topics take no turns
    before = player.turns_until_heal
    press(game_map, pygame.K_c, game_state=state)
    state["chat_target"] = golem        # both have wandered a turn, so choose the golem directly
    press(game_map, pygame.K_c, game_state=state)                   # c again also talks
    assert state.get("dialogue") is golem, "golem didn't start a dialogue"
    assert game_map.messages[:4] == ["The golem: Beep beep, I'm a golem."] + chat.topic_lines(golem), game_map.messages
    press(game_map, pygame.K_1, pygame.K_KP4, game_state=state)     # weather, then changing body parts
    assert game_map.messages[0] == "The golem: " + chat.GOLEM_TOPICS[3][1] and state["dialogue"] is golem
    assert turns_passed(before) == 1, "choosing topics took turns"
    press(game_map, pygame.K_5, game_state=state)                   # loyalty
    assert golem.mood == FRIEND and golem.target is player and state["dialogue"] is None
    assert game_map.messages[-1] == "The golem is now your friend!", game_map.messages

    # Esc cancels choosing without a turn; with nobody in sight there's nobody to talk to
    before = player.turns_until_heal
    press(game_map, pygame.K_c, pygame.K_ESCAPE, game_state=state)
    assert state["chat_target"] is None and game_map.messages == ["You decide not to talk."]
    assert turns_passed(before) == 0
    lonely = empty_room_map()
    press(lonely, pygame.K_c, game_state=state)
    assert state["chat_target"] is None and lonely.messages == ["There's nobody to talk to."]

    # 'an' before a vowel, 'a' before a consonant
    from creatures import Uruk
    assert chat.greeting(Uruk([0, 0])) == "The uruk: Beep beep, I'm an uruk."
    assert chat.greeting(Orc([0, 0])) == "The orc: Beep beep, I'm an orc."

    # every chat line fits beside the More indicator
    lines = [chat.greeting(c) for c in (golem, kobold)] + chat.topic_lines(golem) \
        + [chat.says(golem, answer) for name, answer in chat.GOLEM_TOPICS]
    for line in lines:
        assert len(line) <= 52, f"chat line too long ({len(line)}): {line}"
    print("OK rule checks: c chats; talking takes a turn, golem topics don't, loyalty makes a friend")
