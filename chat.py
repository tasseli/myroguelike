# chat.py
# What creatures say when the player chats with them (c).
# Keep each line at most 52 characters, so that it fits beside the "[m] More" indicator
# when the log has more rows than fit.

from creatures import with_article

def says(creature, text):
    return "The " + creature.name + ": " + text

# Every creature answers this when talked to: "I'm a kobold", "I'm an uruk"
def greeting(creature):
    return says(creature, "Beep beep, I'm " + with_article(creature.name) + ".")

# Golems can talk about these topics, chosen with the keys 1-5.
# Each topic is (name, answer); the loyalty answer also makes the golem the player's friend.
GOLEM_TOPICS = [
    ("weather", "Beep. Damp in here. Good for moss."),
    ("moods", "Beep. Some chase, some flee. I stand."),
    ("meaning of life", "Beep boop. To hold up the ceiling."),
    ("changing body parts", "Beep. My left arm was a doorstep."),
    ("loyalty", "Beep... Loyalty. I will guard you."),
]
LOYALTY = 4     # index of the topic that makes the golem a friend

def has_topics(creature):
    return creature.name == "golem"

# The question and the topics to choose from, as log lines
def topic_lines(creature):
    names = [str(i + 1) + ": " + GOLEM_TOPICS[i][0] for i in range(len(GOLEM_TOPICS))]
    return [says(creature, "What do you want to talk about?"),
            "  ".join(names[:3]),
            "  ".join(names[3:])]
