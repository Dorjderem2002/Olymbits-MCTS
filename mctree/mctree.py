import random
from copy import deepcopy
import math
import sys
import time

sys.setrecursionlimit(100000)

INF = 1_000_000


class State:
    def __init__(self):
        pass

    def is_terminal(self):
        pass

    def result(self):
        pass

    def take_action(self, action):
        pass

    def possible_moves(self):
        pass


class MCTS_Node:
    def __init__(self, state: State, parent, parent_action):
        self.n = 0  # number of visited
        self.state = state
        self.children = []
        self.parent = parent
        self.parent_action = parent_action
        self.result = {}
        self.result[1] = 0
        self.result[0] = 0
        self.result[-1] = 0
        self.score = 0
        self._unexplored_actions = list(self.state.possible_moves())

    def selection(self, c_param=0.01):
        weights = []
        max_score = -INF
        for child in self.children:
            w = child.result[1] - child.result[-1]
            score = w / child.n + c_param * math.sqrt((2 * math.log(self.n / child.n)))
            child.score = score
            max_score = max(max_score, score)
            weights.append(score)
        return self.children[weights.index(max_score)]

    def expansion(self):
        action = self._unexplored_actions.pop()
        next_state = deepcopy(self.state)
        next_state.take_action(action)
        child = MCTS_Node(next_state, self, action)
        self.children.append(child)
        return child

    def simulation(self):
        copyGame = deepcopy(self.state)
        while copyGame.is_terminal() == False:
            moves = copyGame.possible_moves()
            choice = random.choice(moves)
            copyGame.take_action(choice)
        return copyGame.result()

    def backprop(self, result):
        self.result[result] += 1
        self.n += 1
        if self.parent:
            self.parent.backprop(result)

    def is_fully_expanded(self):
        return len(self._unexplored_actions) == 0

    def search(self):
        current = self
        while not current.state.is_terminal():
            if current.is_fully_expanded():
                current = current.selection()
            else:
                return current.expansion()
        return current


class MCTS:
    def search(self, state: State, iteration=100, logging=False):
        root = MCTS_Node(state, None, None)
        start = time.time()
        for _ in range(iteration):
            v = root.search()
            reward = v.simulation()
            v.backprop(reward)
        choice = root.selection()
        end = time.time()
        if logging:
            print(f"Average iteration: {(end-start)/iteration:.2f}")
            print(f"best move score: {choice.result[1] - choice.result[-1]}")
        return choice.parent_action
