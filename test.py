import random
from olymbits import Olymbits


env = Olymbits()

while not env.is_terminal():
    possible_moves = env.possible_moves()
    env.take_action(random.choice(possible_moves))

print(env.reward())