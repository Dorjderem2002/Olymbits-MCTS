import random
from solver import Solver
from tqdm import tqdm


class Olymbits:
    def __init__(self):
        self.race = ""
        self.wind = []
        self.dive = []

    def run(self):
        time_mcts, time_rand, time_optimal, time_right = 0, 0, 0, 0
        dist_optimal, dist_greedy, dist_sim, dist_rand = 0, 0, 0, 0
        score_optimal, score_sim, score_rand = 0, 0, 0
        time_combined, dist_combined, score_combined = 0, 0, 0
        for _ in tqdm(range(10)):
            self.race = self.generate_track()
            self.wind = self.generate_wind()
            self.dive = self.generate_dive()
            solver = Solver()

            # hurdle
            hurdle_optimal = solver.optimal_hurdle_race(self.race, 0)
            hurdle_sim = solver.sim_hurdle_race(self.race, 0, 3)
            hurdle_rnd = solver.random_hurdle_race(self.race, 0, 3)
            hurdle_right = solver.right_hurdle_race(self.race, 0, 3)
            time_mcts += hurdle_sim
            time_rand += hurdle_rnd
            time_optimal += hurdle_optimal
            time_right += hurdle_right

            # archery
            x, y = random.randint(-20, 20), random.randint(-20, 20)
            copy_wind = self.wind[:]
            archery_optimal = solver.optimal_archery(copy_wind, x, y)
            copy_wind = self.wind[:]
            archery_greedy = solver.greedy_archery(copy_wind, x, y)
            copy_wind = self.wind[:]
            archery_sim = solver.sim_archery(copy_wind, [x, x, x], [y, y, y])
            copy_wind = self.wind[:]
            archery_rand = solver.random_archery(copy_wind, x, y)
            dist_greedy += archery_greedy
            dist_optimal += archery_optimal
            dist_rand += archery_rand
            dist_sim += archery_sim
            # dive

            score_optimal += solver.optimal_dive(len(self.dive))
            score_rand += solver.random_dive(self.dive)
            score_sim += solver.sim_dive(self.dive, 0, [0,0,0])

            # combined

            hurdle_combined_time, archery_combined_time, dive_combined_time = solver.sim_combined(
                self.race, 0, 3, self.wind, [x, x, x], [y, y, y], self.dive
            )

            time_combined += hurdle_combined_time
            dist_combined += archery_combined_time
            score_combined += dive_combined_time

        print("-" * 10 + "HURDLE" + "-" * 10)
        print("OPTIMAL", time_optimal)
        print("MCTS:", time_mcts)
        print("RANDOM:", time_rand)
        print("RIGHT:", time_right)
        print("EPSILON MCTS:", time_optimal / time_mcts)
        print("EPSILON RANDOM:", time_optimal / time_rand)
        print("EPSILON RIGHT:", time_optimal / time_right)
        print("-" * 10 + "ARCHERY" + "-" * 10)
        print("OPTIMAL:", dist_optimal)
        print("GREEDY:", dist_greedy)
        print("MCTS:", dist_sim)
        print("RANDOM:", dist_rand)
        print("-" * 10 + "DIVE" + "-" * 10)
        print("OPTIMAL:", score_optimal)
        print("MCTS:", score_sim)
        print("RANDOM:", score_rand)
        print("-" * 10 + "COMBINED" + "-" * 10)
        print("MCTS COMBINED HURDLE:", time_optimal / time_combined)
        print("MCTS COMBINED ARCHERY:", dist_combined)
        print("MCTS COMBINED DIVE:", score_combined)

    def generate_track(self):
        res = ""
        for i in range(30):
            if random.randint(0, 4) == 0 and i >= 3 and res[i - 1] != "#":
                res += "#"
            else:
                res += "."
        return res

    def generate_wind(self):
        l = random.randint(12, 15)
        res = []
        for _ in range(l):
            res.append(random.randint(1, 9))
        return res

    def generate_dive(self):
        l = 14
        res = []
        for _ in range(l):
            res.append(random.choice(["R", "L", "U", "D"]))
        return res


game = Olymbits()
game.run()
