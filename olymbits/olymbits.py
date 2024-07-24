import random
import math
from functools import cache


class Race:
    def __init__(self, track):
        self.pid = 0
        self.track = track
        self.pos = [0, 0, 0]
        self.stun_cooldown = [0, 0, 0]
        self.stun = [0, 0, 0]
        self.time = [0, 0, 0]


class Archery:
    def __init__(self, wind):
        self.pid = 0
        self.wind = wind
        self.x = [0, 0, 0]
        self.y = [0, 0, 0]
        self.distance = [0, 0, 0]


class Dive:
    def __init__(self, dive):
        self.pid = 0
        self.dive = dive
        self.scores = [0, 0, 0]
        self.combo = [0, 0, 0]


class Olymbits:
    def __init__(self):
        self.track = self._generate_track()
        self.wind = self._generate_wind()
        self.dive = self._generate_dive()
        self.round = 0
        self.result = {
            "race": [],
            "archery": [],
            "dive": [],
        }

        self.race = Race(self.track)
        self.archery = Archery(self.wind)
        self.dive = Dive(self.dive)

    def reward(self):
        return self.result

    def is_terminal(self):
        return self.round == 100

    def take_action(self, action):
        if self.round < 100:
            self._handle_race_action(action)
            self._handle_archery_action(action)
            self._handle_dive_action(action)
            self.round += 1
        else:
            raise Warning("Game has ended")

    def possible_moves(self):
        return ["LEFT", "RIGHT", "UP", "DOWN"]

    def get_state(self):
        return [self.race, self.archery, self.dive]

    def get_race_state(self):
        return self.race

    def get_archery_state(self):
        return self.archery

    def get_dive_state(self):
        return self.dive

    def _handle_race_action(self, action):
        if self.race.track == "GAME_OVER":
            self.race = Race(self._generate_track())
            return
        if self.race.stun_cooldown[self.race.pid] > 0:
            self.race.time[self.race.pid] += 1
            self.race.stun_cooldown[self.race.pid] -= 1
            return
        action_move_map = {
            "DOWN": 2,
            "LEFT": 1,
            "RIGHT": 3,
        }
        pid = self.race.pid
        pos = self.race.pos[pid]
        self.race.time[pid] += 1
        if action == "UP":
            if self.race.track[pos + 2 : pos + 3] == "#":
                self.race.stun_cooldown[pid] += self.race.stun[pid]
            self.race.pos[pid] = min(pos + 2, len(self.track) + 1)
        else:
            for j in range(
                pos + 1,
                min(len(self.race.track) + 1, pos + action_move_map[action] + 1),
            ):
                self.race.pos[pid] = j
                if j == "#":
                    self.race.stun_cooldown[pid] += self.race.stun[pid]
                    break
        if len(self.race.track) <= self.race.pos[self.race.pid]:
            self.race.track = "GAME_OVER"
            optimal = self._optimal_hurdle_race(self.race.track, 0)
            self.result["race"].append(optimal / self.race.time[pid])

    def _handle_archery_action(self, action):
        if self.archery.wind == "GAME_OVER":
            self.archery = Archery(self._generate_wind())
            return
        pid = self.archery.pid
        if action == "UP":
            self.archery.y[pid] -= int(self.archery.wind[0])
        elif action == "DOWN":
            self.archery.y[pid] += int(self.archery.wind[0])
        elif action == "LEFT":
            self.archery.x[pid] -= int(self.archery.wind[0])
        else:
            self.archery.x[pid] += int(self.archery.wind[0])
        self.archery.wind = self.archery.wind[1:]
        self.archery.distance[pid] = math.sqrt(
            self.archery.x[pid] ** 2 + self.archery.y[pid] ** 2
        )
        if len(self.archery.wind) == 0:
            max_dist = 30
            self.result["archery"].append(self.archery.distance[pid] / max_dist)
            self.archery.wind = "GAME_OVER"

    def _handle_dive_action(self, action):
        if self.dive.dive == "GAME_OVER":
            self.dive = Dive(self._generate_dive())
            return
        pid = self.dive.pid
        if action[0] == self.dive.dive[0]:
            self.dive.combo[pid] += 1
            self.dive.scores[pid] += self.dive.combo[pid]
        else:
            self.dive.combo[pid]
        self.dive.dive = self.dive.dive[1:]

        if len(self.dive.dive) == 0:
            self.result["dive"].append(self.dive.scores[pid] / 1080)
            self.dive.dive = "GAME_OVER"

    def _generate_track(self):
        res = ""
        for i in range(30):
            if random.randint(0, 4) == 0 and i >= 3 and res[i - 1] != "#":
                res += "#"
            else:
                res += "."
        return res

    def _generate_wind(self):
        l = random.randint(12, 15)
        res = ""
        for _ in range(l):
            res += str(random.randint(1, 9))
        return res

    def _generate_dive(self):
        l = 14
        res = ""
        for _ in range(l):
            res += random.choice(["R", "L", "U", "D"])
        return res

    def _optimal_hurdle_race(self, track, pos):
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

    def _optimal_archery(self, wind, x, y):

        @cache
        def solve(lx, ly, i):
            if i >= len(wind):
                return math.sqrt(lx**2, ly**2)
            res = 1000_0000_00000
            res = min(res, solve(lx - wind[i], ly, i + 1))
            res = min(res, solve(lx + wind[i], ly, i + 1))
            res = min(res, solve(lx, ly + wind[i], i + 1))
            res = min(res, solve(lx, ly - wind[i], i + 1))
            return res

        return solve(x, y, 0)
