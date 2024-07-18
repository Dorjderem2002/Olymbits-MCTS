import sys
import math
from dataclasses import dataclass, field
from typing import List
import time
import random
from copy import deepcopy, copy
import math
from collections import defaultdict
from functools import cache

INF = 1_000_000
ITERATION = 200


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
        self.result = defaultdict(int)
        self.game_result = {}
        self.game_result["hurdle"] = defaultdict(int)
        self.game_result["archery"] = defaultdict(int)
        self.game_result["dive"] = defaultdict(int)
        self.score = 0
        self._unexplored_actions = self.state.possible_moves()

    def selection(self, c_param=0.1):
        max_score = -INF
        max_index = 0
        for i in range(len(self.children)):
            child = self.children[i]
            w_archery = (
                child.game_result["archery"][1] - child.game_result["archery"][-1]
            ) / max(0.01, child.state.archery.medal)
            w_dive = (
                child.game_result["dive"][1] - child.game_result["dive"][-1]
            ) / max(0.01, child.state.dive.medal)
            w_hurdle = (
                child.game_result["hurdle"][1] - child.game_result["hurdle"][-1]
            ) / max(0.01, child.state.race.medal)
            w = w_archery + w_dive + w_hurdle
            score = w / child.n + c_param * math.sqrt((2 * math.log(self.n / child.n)))
            self.children[i].score = score
            if score > max_score:
                max_score = score
                max_index = i
        return self.children[max_index]

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
        self.game_result["dive"][result["dive"]] += 1
        self.game_result["archery"][result["archery"]] += 1
        self.game_result["hurdle"][result["hurdle"]] += 1
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
    def search(self, state: State, iteration=100):
        root = MCTS_Node(state, None, None)
        for _ in range(iteration):
            v = root.search()
            reward = v.simulation()
            v.backprop(reward)
        choice = root.selection()
        convert = {"L": "LEFT", "R": "RIGHT", "U": "UP", "D": "DOWN"}
        return convert[choice.parent_action]


def debug(*args):
    print(*args, file=sys.stderr, flush=True)


class Race:
    def __init__(self, medal, pid, time, track, pos, stun):
        self.medal = medal
        self.pid = pid
        self.time = time
        self.track = track
        self.pos = pos
        self.stun = stun


class Archery:
    def __init__(self, medal, pid, distance, wind, x, y):
        self.medal = medal
        self.pid = pid
        self.distance = distance
        self.wind = wind
        self.x = x
        self.y = y


class Dive:
    def __init__(self, medal, pid, goal, points, combo):
        self.medal = medal
        self.pid = pid
        self.goal = goal
        self.points = points
        self.combo = combo


class GameState(State):
    def __init__(self, race: Race, archery: Archery, dive: Dive):
        self.race: Race = race
        self.archery: Archery = archery
        self.dive: Dive = dive

    def is_terminal(self):
        return (
            (self.race.track == "G" or max(self.race.pos) >= 30)
            and (self.archery.wind == "G" or len(self.archery.wind) == 0)
            and (self.dive.goal == "G" or len(self.dive.goal) == 0)
        )

    def result(self):
        game_eval = {"archery": 0, "dive": 0, "hurdle": 0}
        if self.dive.goal != "G" and len(self.dive.goal) == 0:
            if self.dive.points[self.dive.pid] == max(self.dive.points):
                game_eval["dive"] = 1
            else:
                game_eval["dive"] = -1
        if self.archery.wind != "G" and len(self.archery.wind) == 0:
            if self.archery.distance[self.archery.pid] == min(self.archery.distance):
                game_eval["archery"] = 1
            else:
                game_eval["archery"] = -1
        if self.race.track != "G" and max(self.race.pos) >= 30:
            if self.race.time[self.race.pid] == max(self.race.time):
                game_eval["hurdle"] = 1
            else:
                game_eval["hurdle"] = -1
        return game_eval

    def handle_hurdle_move(self, action, pid):
        stun = self.race.stun[pid]
        track = self.race.track
        pos = self.race.pos[pid]
        if action == "L":
            self.race.pos[pid] += 1
            if "#" in track[pos + 1 : pos + 2]:
                self.race.time[pid] += stun
        if action == "R":
            self.race.pos[pid] += 3
            if "#" in track[pos + 1 : pos + 4]:
                loc = track[pos + 1 : pos + 4].index("#")
                self.race.pos[pid] = pos + loc + 1
                self.race.time[pid] += stun
        if action == "U":
            self.race.pos[pid] += 2
            if "#" in track[pos + 2 : pos + 3]:
                loc = track[pos + 1 : pos + 4].index("#")
                self.race.pos[pid] = pos + loc + 1
                self.race.time[pid] += stun
        if action == "D":
            self.race.pos[pid] += 2
            if "#" in track[pos + 1 : pos + 3]:
                loc = track[pos + 1 : pos + 4].index("#")
                self.race.pos[pid] = pos + loc + 1
                self.race.time[pid] += stun
        self.race.time[pid] += 1

    def handle_archery_move(self, action, pid, wind_speed):
        if wind_speed == None:
            wind_speed = int(self.archery.wind.pop(0))
        if action == "U":
            self.archery.y[pid] -= wind_speed
        elif action == "D":
            self.archery.y[pid] += wind_speed
        elif action == "L":
            self.archery.x[pid] -= wind_speed
        else:
            self.archery.x[pid] += wind_speed
        self.archery.distance[pid] = self.distance(
            self.archery.x[pid], self.archery.y[pid]
        )

    def handle_dive_move(self, action, pid, current_ans):
        if current_ans == None:
            current_ans = self.dive.goal.pop(0)
        if action[0] == current_ans:
            self.dive.combo[pid] += 1
            self.dive.points[pid] += self.dive.combo[pid]
        else:
            self.dive.combo[pid] = 0

    def take_action(self, action):
        bots = [0, 1, 2]
        bots.remove(self.race.pid)
        if self.race.track != "G" and max(self.race.pos) < 30:
            self.handle_hurdle_move(action, self.race.pid)
            self.handle_hurdle_move(random.choice(self.enemy_moves(bots[0])), bots[0])
            self.handle_hurdle_move(random.choice(self.enemy_moves(bots[1])), bots[1])
        if self.archery.wind != "G" and len(self.archery.wind) > 0:
            self.handle_archery_move(
                random.choice(["U", "D", "L", "R"]),
                bots[0],
                self.archery.wind[0],
            )
            self.handle_archery_move(
                random.choice(["U", "D", "L", "R"]),
                bots[1],
                self.archery.wind[0],
            )
            self.handle_archery_move(action, self.archery.pid, None)
        if self.dive.goal != "G" and len(self.dive.goal) > 0:
            self.handle_dive_move(
                random.choice(["U", "D", "L", "R"]),
                bots[0],
                self.dive.goal[0],
            )
            self.handle_dive_move(
                random.choice(["U", "D", "L", "R"]),
                bots[1],
                self.dive.goal[0],
            )
            self.handle_dive_move(action, self.dive.pid, None)

    def possible_moves(self):
        moves = []
        if self.race.track != "G":
            pos = self.race.pos[self.race.pid]
            if "#" == self.race.track[pos + 1 : pos + 2]:
                moves.append("U")
            if "#" not in self.race.track[pos + 1 : pos + 4]:
                moves.append("R")
            if "#" not in self.race.track[pos + 1 : pos + 3]:
                moves.append("D")
            if "#" not in self.race.track[pos + 1 : pos + 2]:
                moves.append("L")
        if len(moves) == 0:
            return ["U", "R", "D", "L"]
        if (
            self.race.medal >= self.dive.medal
            and len(self.dive.goal) > 0
            and self.dive.goal[0] != "G"
            and self.dive.goal[0] not in moves
        ):
            moves.append(self.dive.goal[0])
        return moves

    def enemy_moves(self, pid):
        moves = []
        pos = self.race.pos[pid]
        if "#" == self.race.track[pos + 1 : pos + 2]:
            moves.append("U")
        if "#" not in self.race.track[pos + 1 : pos + 4]:
            moves.append("R")
        if "#" not in self.race.track[pos + 1 : pos + 3]:
            moves.append("D")
        if "#" not in self.race.track[pos + 1 : pos + 2]:
            moves.append("L")
        return moves

    def distance(self, x, y):
        return x * x + y * y


class Solver:
    def __init__(self):
        self.ai = MCTS()

    def sim_hurdle_race(self, track, pos, stun):
        res = 0
        while pos < 30:
            race = Race(0, 0, [res, res, res], track, [pos, 0, 0], [stun, 0, 0])
            archery = Archery(0, 0, 0, 'G', 0, 0)
            dive = Dive(0, 0, 'G', [], [])
            state = GameState(race, archery, dive)
            action = self.ai.search(state, iteration=ITERATION)
            if action == "LEFT":
                if "#" in track[pos + 1 : pos + 2]:
                    pos += 1
                    res += stun
                else:
                    pos += 1
            if action == "RIGHT":
                if "#" in track[pos + 1 : pos + 4]:
                    loc = track[pos + 1 : pos + 4].index("#")
                    pos += loc + 1
                    res += stun
                else:
                    pos += 3

            if action == "UP":
                if "#" in track[pos + 2 : pos + 3]:
                    loc = track[pos + 1 : pos + 4].index("#")
                    pos += loc + 1
                    res += stun
                else:
                    pos += 2

            if action == "DOWN":
                if "#" in track[pos + 1 : pos + 3]:
                    loc = track[pos + 1 : pos + 4].index("#")
                    pos += loc + 1
                    res += stun
                else:
                    pos += 2
            res += 1
        return res

    def optimal_hurdle_race(self, track, pos):
        res = 0
        while pos < 30:
            res += 1
            if "#" == track[pos + 1 : pos + 2]:
                pos += 2
            elif "#" not in track[pos + 1 : pos + 4]:
                pos += 3
            elif "#" not in track[pos + 1 : pos + 3]:
                pos += 2
            elif "#" not in track[pos + 1 : pos + 2]:
                pos += 1
        return res

    def random_hurdle_race(self, track, pos, stun):
        res = 0
        while pos < 30:
            action = random.choice(["LEFT", "RIGHT", "UP", "DOWN"])
            if action == "LEFT":
                if "#" in track[pos + 1 : pos + 2]:
                    pos += 1
                    res += stun
                else:
                    pos += 1

            if action == "RIGHT":
                if "#" in track[pos + 1 : pos + 4]:
                    loc = track[pos + 1 : pos + 4].index("#")
                    pos += loc + 1
                    res += stun
                else:
                    pos += 3

            if action == "UP":
                if "#" in track[pos + 2 : pos + 3]:
                    loc = track[pos + 1 : pos + 4].index("#")
                    pos += loc + 1
                    res += stun
                else:
                    pos += 2

            if action == "DOWN":
                if "#" in track[pos + 1 : pos + 3]:
                    loc = track[pos + 1 : pos + 4].index("#")
                    pos += loc + 1
                    res += stun
                else:
                    pos += 2
            res += 1
        return res

    def right_hurdle_race(self, track, pos, stun):
        res = 0
        while pos < 30:
            if "#" in track[pos + 1 : pos + 4]:
                loc = track[pos + 1 : pos + 4].index("#")
                pos += loc + 1
                res += stun
            else:
                pos += 3
            res += 1
        return res

    def distance(self, x, y):
        return x * x + y * y

    def greedy_archery(self, wind, x, y):
        while len(wind) > 0:
            a = wind.pop(0)
            dist = INF
            lx, ly = x, y
            if dist > self.distance(x + a, y):
                lx = x + a
                dist = self.distance(x + a, y)
            if dist > self.distance(x - a, y):
                lx = x - a
                dist = self.distance(x - a, y)
            if dist > self.distance(x, y + a):
                ly = y + a
                dist = self.distance(x, y + a)
            if dist > self.distance(x, y - a):
                ly = y - a
                dist = self.distance(x, y - a)
            x, y = lx, ly
        return self.distance(x, y)

    def optimal_archery(self, wind, x, y):

        @cache
        def solve(lx, ly, i):
            if i >= len(wind):
                return self.distance(lx, ly)
            res = INF
            res = min(res, solve(lx - wind[i], ly, i + 1))
            res = min(res, solve(lx + wind[i], ly, i + 1))
            res = min(res, solve(lx, ly + wind[i], i + 1))
            res = min(res, solve(lx, ly - wind[i], i + 1))
            return res

        return solve(x, y, 0)

    def sim_archery(self, wind, x, y):
        while len(wind) > 0:
            race = Race(0, 0, [], 'G', [], [])
            archery = Archery(
                0,
                0,
                [
                    self.distance(x[0], y[0]),
                    self.distance(x[1], y[1]),
                    self.distance(x[2], y[2]),
                ],
                wind,
                x,
                y,
            )
            dive = Dive(0, 0, 'G', 0, [])
            state = GameState(race, archery, dive)
            action = self.ai.search(state, iteration=ITERATION)
            if action == "UP":
                y[0] -= wind.pop(0)
            elif action == "DOWN":
                y[0] += wind.pop(0)
            elif action == "LEFT":
                x[0] -= wind.pop(0)
            else:
                x[0] += wind.pop(0)
        return self.distance(x[0], y[0])

    def random_archery(self, wind, x, y):
        while len(wind) > 0:
            action = random.choice(["U", "D", "L", "R"])
            if action == "U":
                y -= wind.pop(0)
            elif action == "D":
                y += wind.pop(0)
            elif action == "L":
                x -= wind.pop(0)
            else:
                x += wind.pop(0)
        return self.distance(x, y)

    def optimal_dive(self, dive_len):
        res = 0
        bonus = 0
        for i in range(dive_len):
            bonus += 1
            res += bonus
        return res

    def random_dive(self, dive):
        res = 0
        bonus = 0
        for i in range(len(dive)):
            action = random.choice(["RIGHT", "LEFT", "UP", "DOWN"])
            if action[0] == dive[i]:
                bonus += 1
                res += bonus
            else:
                bonus = 0
        return res

    def sim_dive(self, dive, pid, pos):
        res = 0
        bonus = 0
        copy_dive = copy(dive)
        while len(copy_dive) > 0:
            race = Race(0, 0, [0, 0, 0], 'G', [0, 0, 0], [0, 0, 0])
            archery = Archery(0, 0, [], 'G', [], [])
            dive = Dive(0, pid, copy_dive, [res, res, res], [bonus, bonus, bonus])
            state = GameState(race, archery, dive)
            action = self.ai.search(state, iteration=ITERATION)
            if action[0] == copy_dive.pop(0):
                bonus += 1
                res += bonus
            else:
                bonus = 0
        return res

    def sim_combined(self, track, pos, stun, wind, x, y, dive):
        res = 0
        bonus = 0
        res_bonus = 0
        copy_dive = dive[:]
        while pos < 30 or len(wind) > 0 or len(copy_dive):
            race = Race(0, 0, [res, res, res], track, [pos, 0, 0], [stun, 0, 0])
            archery = Archery(
                0,
                0,
                [
                    self.distance(x[0], y[0]),
                    self.distance(x[1], y[1]),
                    self.distance(x[2], y[2]),
                ],
                wind,
                x,
                y,
            )
            cp = copy_dive[:]
            dive = Dive(0, 0, cp, [res, res, res], [bonus, bonus, bonus])
            state = GameState(race, archery, dive)
            action = self.ai.search(state, iteration=ITERATION)
            if action == "LEFT":
                if "#" in track[pos + 1 : pos + 2]:
                    pos += 1
                    res += stun
                else:
                    pos += 1
            if action == "RIGHT":
                if "#" in track[pos + 1 : pos + 4]:
                    loc = track[pos + 1 : pos + 4].index("#")
                    pos += loc + 1
                    res += stun
                else:
                    pos += 3

            if action == "UP":
                if "#" in track[pos + 2 : pos + 3]:
                    loc = track[pos + 1 : pos + 4].index("#")
                    pos += loc + 1
                    res += stun
                else:
                    pos += 2

            if action == "DOWN":
                if "#" in track[pos + 1 : pos + 3]:
                    loc = track[pos + 1 : pos + 4].index("#")
                    pos += loc + 1
                    res += stun
                else:
                    pos += 2
            res += 1
            if len(wind) > 0:
                if action == "UP":
                    y[0] -= wind.pop(0)
                elif action == "DOWN":
                    y[0] += wind.pop(0)
                elif action == "LEFT":
                    x[0] -= wind.pop(0)
                else:
                    x[0] += wind.pop(0)
            if len(copy_dive) > 0:
                if action[0] == copy_dive.pop(0):
                    bonus += 1
                    res_bonus += bonus
                else:
                    bonus = 0
        return res, self.distance(x[0], y[0]), res_bonus
