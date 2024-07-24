## EXAMPLE USE AS LIBRARY

```
import random
from olymbits import Olymbits


env = Olymbits()

while not env.is_terminal():
    possible_moves = env.possible_moves()
    env.take_action(random.choice(possible_moves))

print(env.reward())
```

## RUN

```
python run.py
```

## PERFORMANCE (Higher the better)

----------HURDLE----------

MCTS: 0.9485294117647058

RANDOM: 0.5201612903225806

RIGHT: 0.5657894736842105

----------ARCHERY----------

OPTIMAL: 0.999375

GREEDY: 0.98575

MCTS: 0.792625

RANDOM: 0.326625

----------DIVE----------

OPTIMAL: 1

MCTS: 0.35

RANDOM: 0.029
