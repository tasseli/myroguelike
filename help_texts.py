# help_texts.py
# Texts for ? (commands), h (help) and the key hint row under the message log.
# Keep each line at most 52 characters, so that a row number in front of it
# still leaves room for the "[m] More" indicator on the same row.

# ? : the commands that can be used on any turn
COMMAND_LINES = [
    "Move: arrow keys or numpad 1-9 (diagonals too).",
    "5: stay in place for one turn.",
    "w: wait many turns (type a number, then Enter).",
    "l: look at creatures you can see.",
    "c: chat with a creature you can see.",
    "m: show more rows of the log.",
    "p: the game's earlier messages.",
    "?: this list of commands.   h: help.",
    "q or x: quit the game.",
]

# h : how things work, in more detail
HELP_LINES = [
    "Attacking: walk into a creature to attack it.",
    "Red monsters attack you. A grey one bumping into",
    "   you turns red instead of hitting. Monsters",
    "   attack only you or the creature they chase;",
    "   others in their way just block them.",
    "Health: HP at the right. At 0 health you die.",
    "Healing: everyone heals 1 health every 20 turns.",
    "Waiting (w): type how many turns, then Enter.",
    "   Backspace deletes a digit, Esc cancels.",
    "   Turns are shown, speeding up; any key stops.",
    "   Waiting stops when someone comes next to you,",
    "   and doesn't start if someone already is.",
    "   It also stops when you reach full health,",
    "   unless you started waiting at full health.",
    "Colors: monsters on red are chasing you; those on",
    "   grey wander or go their own way.",
    "   Hit a grey one and it starts chasing you.",
    "   Yellow: fleeing. Kobolds flee at 2 health or less",
    "   until they have healed back to full.",
    "   Golems flee at 2 health or less too, until at",
    "   half health; then they go back to what they did.",
    "   Green: friendly. A friend stays near you and",
    "   attacks monsters that come after you.",
    "   Monsters it hits turn on it and fight back.",
    "   Walking into your friend asks before attacking.",
    "Looking (l): a blinking cursor shows a creature",
    "   you can see; arrows/numpad jump to the next",
    "   one that way; t jumps to the one it chases or",
    "   flees from. l or Esc stops looking.",
    "Chatting (c): choose whom with arrows/numpad,",
    "   then Enter or c. Talking takes a turn; with",
    "   golems, choosing topics (1-5) doesn't.",
    "Log: when a turn has more than 4 messages, the",
    "   rows are numbered and m shows the next ones.",
    "History (p): the game's earlier messages, newest",
    "   first; m, p or up: older, down: newer, Esc: back.",
    "After dying: r plays again, l looks around,",
    "   p shows earlier messages, q quits.",
]

# Shown on the row under the message log
# (m is left out to make room; the "[m] More" indicator shows it when it's needed)
KEY_HINTS = "arrows/numpad: move  5: stay  w: wait  l: look  c: chat  ?: commands  h: help"
WAIT_KEY_HINTS = "any key: stop waiting"
CHAT_KEY_HINTS = "arrows/numpad: choose whom  Enter or c: talk  Esc: cancel"
CONFIRM_KEY_HINTS = "y: attack your friend   n or any other key: don't"
DIALOGUE_KEY_HINTS ="1-5: choose a topic  m: more  Esc: end the talk"
LOOK_KEY_HINTS ="arrows/numpad: next creature that way  t: its target  l or Esc: stop looking"
HISTORY_KEY_HINTS = "m, p or up: older messages  down: newer  Esc: back"
DEATH_KEY_HINTS = "r: play again   l: look around   p: messages   q: quit"
