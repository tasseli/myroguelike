# help_texts.py
# Texts for the help (? and h) and the key hint row under the message log.
# Keep each help line at most 52 characters, so that a row number in front of it
# still leaves room for the "[m] More" indicator on the same row.

HELP_LINES = [
    "Move: arrow keys or numpad 1-9 (diagonals too).",
    "Walk into a creature to attack it.",
    "5: stay in place for one turn.",
    "w: wait many turns. Type a number, then Enter.",
    "   Waiting stops when someone comes next to you.",
    "Everyone heals 1 health every 20 turns.",
    "m: show more rows when the log has more than 4.",
    "? or h: show this help.   q or x: quit the game.",
    "After dying: r plays again, q quits.",
]

# Shown on the row under the message log
KEY_HINTS = "arrows/numpad: move   5: stay   w: wait   m: more   ?/h: help   q: quit"
DEATH_KEY_HINTS = "r: play again   q: quit"
