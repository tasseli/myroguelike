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
    "m: show more rows of the log.",
    "?: this list of commands.   h: help.",
    "q or x: quit the game.",
]

# h : how things work, in more detail
HELP_LINES = [
    "Attacking: walk into a creature to attack it.",
    "Monsters attack you, or the creature they chase;",
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
    "Looking (l): a blinking cursor shows a creature",
    "   you can see; arrows/numpad jump to the next",
    "   one that way. l or Esc stops looking.",
    "Log: when a turn has more than 4 messages, the",
    "   rows are numbered and m shows the next ones.",
    "After dying: r plays again, q quits.",
]

# Shown on the row under the message log
KEY_HINTS = "arrows/numpad: move  5: stay  w: wait  l: look  m: more  ?: commands  h: help"
WAIT_KEY_HINTS = "any key: stop waiting"
LOOK_KEY_HINTS ="arrows/numpad: next creature that way   l or Esc: stop looking"
DEATH_KEY_HINTS = "r: play again   q: quit"
