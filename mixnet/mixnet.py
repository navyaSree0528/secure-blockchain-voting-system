import random


def shuffle_votes(votes):

    shuffled = votes.copy()

    random.shuffle(shuffled)

    return shuffled