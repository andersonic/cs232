import interface as f
import math
import copy

BEST_MATCHUP = 4
GOOD_MATCHUP = 3
TIE = 2
BAD_MATCHUP = 1
WORST_MATCHUP = 0


def make_health_difference_matrix():
    health_matrix = [[None for j in range(0,6)] for i in range(0,6)]
    for i in range(0, len(health_matrix)):
        for j in range(0, len(health_matrix[i])):
            try:
                health_matrix[i][j] = f.own_team[i].get_health_percent() - f.opponent_team[j].get_health_percent()
            except IndexError:
                # Unrevealed opponent. It must be at full health.
                health_matrix[i][j] = f.own_team[i].get_health_percent() - 1

    return health_matrix


def make_matchup_matrix():
    matchup_matrix = [[None for j in range(0,6)] for i in range(0,6)]

    for i in range(0, len(matchup_matrix)):
        for j in range(0, len(matchup_matrix[i])):
            try:
                my_mon = f.own_team[i]
                your_mon = f.opponent_team[j]
                if my_mon.present_health == 0 and your_mon.present_health == 0:
                    matchup_matrix[i][j] = 2
                elif my_mon.present_health == 0:
                    matchup_matrix[i][j] = 0
                elif your_mon.present_health == 0:
                    matchup_matrix[i][j] == 4
                else:
                    matchup_matrix[i][j] = get_matchup(my_mon, your_mon)
            except IndexError:
                # Unrevealed opponent
                matchup_matrix[i][j] = TIE

    return matchup_matrix


def get_heuristic():
    health_matrix = make_health_difference_matrix()
    matchup_matrix = make_matchup_matrix()

    heuristic_matrix = [[None for j in range(0,6)] for i in range(0,6)]

    for i in range (0, len(heuristic_matrix)):
        for j in range(0, len(heuristic_matrix[i])):
            heuristic_matrix[i][j] = (math.e ** health_matrix[i][j]) * matchup_matrix[i][j]

    heuristic = 0
    for i in range(0, len(heuristic_matrix)):
        for j in range(0, len(heuristic_matrix[i])):
            heuristic += heuristic_matrix[i][j]

    return heuristic


def get_matchup(my_mon, your_mon):
    my_best_damage = 0
    your_best_damage = 0

    for move in my_mon.moves:
        damage = your_mon.damage_calc(move, my_mon)
        if damage > my_best_damage:
            my_best_damage = damage
    my_best_damage = my_best_damage * 100 / your_mon.total_health

    for move in your_mon.moves:
        damage = my_mon.damage_calc(move, your_mon)
        if damage > your_best_damage:
            your_best_damage = damage
    your_best_damage = your_best_damage * 100 / my_mon.total_health

    faster = None

    if my_mon.calc_effective_stats()[4] > your_mon.calc_effective_stats()[4]:
        faster = my_mon
    elif your_mon.calc_effective_stats()[4] > my_mon.calc_effective_stats()[4]:
        faster = your_mon

    if my_mon is faster and my_best_damage >= 100:
        return BEST_MATCHUP
    elif your_mon is faster and your_best_damage >= 100:
        return WORST_MATCHUP
    elif my_mon is faster and your_best_damage >= 100 and my_best_damage >= 50:
        return BAD_MATCHUP
    elif your_mon is faster and my_best_damage >= 100 and your_best_damage >= 50:
        return GOOD_MATCHUP
    elif my_mon is faster and my_best_damage >= 50:
        return GOOD_MATCHUP
    elif your_mon is faster and your_best_damage >= 50:
        return BAD_MATCHUP
    return TIE


class State:
    def __init__(self, my_team, your_team, my_mon_out, your_mon_out):
        self.my_team = my_team
        self.your_team = your_team
        self.my_mon_out = my_mon_out
        self.your_mon_out = your_mon_out

    def make_health_difference_matrix(self):
        health_matrix = [[None for j in range(0, 6)] for i in range(0, 6)]
        for i in range(0, len(health_matrix)):
            for j in range(0, len(health_matrix[i])):
                try:
                    health_matrix[i][j] = self.my_team[i].get_health_percent() - self.your_team[j].get_health_percent()
                except AttributeError:
                    # Unrevealed opponent. It must be at full health.
                    health_matrix[i][j] = self.my_team[i].get_health_percent() - 1

        return health_matrix

    def make_matchup_matrix(self):
        matchup_matrix = [[None for j in range(0, 6)] for i in range(0, 6)]

        for i in range(0, len(matchup_matrix)):
            for j in range(0, len(matchup_matrix[i])):
                try:
                    my_mon = self.my_team[i]
                    your_mon = self.your_team[j]
                    if my_mon.present_health == 0 and your_mon.present_health == 0:
                        matchup_matrix[i][j] = 2
                    elif my_mon.present_health == 0:
                        matchup_matrix[i][j] = 0
                    elif your_mon.present_health == 0:
                        matchup_matrix[i][j] == 4
                    else:
                        matchup_matrix[i][j] = self.get_matchup(my_mon, your_mon)

        return matchup_matrix

    @staticmethod
    def get_matchup(self, my_mon, your_mon):
        my_best_damage = 0
        your_best_damage = 0

        if your_mon is None:
            return TIE

        for move in my_mon.moves:
            damage = your_mon.damage_calc(move, my_mon)
            if damage > my_best_damage:
                my_best_damage = damage
        my_best_damage = my_best_damage * 100 / your_mon.total_health

        for move in your_mon.moves:
            damage = my_mon.damage_calc(move, your_mon)
            if damage > your_best_damage:
                your_best_damage = damage
        your_best_damage = your_best_damage * 100 / my_mon.total_health

        faster = None

        if my_mon.calc_effective_stats()[4] > your_mon.calc_effective_stats()[4]:
            faster = my_mon
        elif your_mon.calc_effective_stats()[4] > my_mon.calc_effective_stats()[4]:
            faster = your_mon

        if my_mon is faster and my_best_damage >= 100:
            return BEST_MATCHUP
        elif your_mon is faster and your_best_damage >= 100:
            return WORST_MATCHUP
        elif my_mon is faster and your_best_damage >= 100 and my_best_damage >= 50:
            return BAD_MATCHUP
        elif your_mon is faster and my_best_damage >= 100 and your_best_damage >= 50:
            return GOOD_MATCHUP
        elif my_mon is faster and my_best_damage >= 50:
            return GOOD_MATCHUP
        elif your_mon is faster and your_best_damage >= 50:
            return BAD_MATCHUP
        return TIE

    def get_heuristic(self):
        health_matrix = make_health_difference_matrix()
        matchup_matrix = make_matchup_matrix()

        heuristic_matrix = [[None for j in range(0, 6)] for i in range(0, 6)]

        for i in range(0, len(heuristic_matrix)):
            for j in range(0, len(heuristic_matrix[i])):
                heuristic_matrix[i][j] = (math.e ** health_matrix[i][j]) * matchup_matrix[i][j]

        heuristic = 0
        for i in range(0, len(heuristic_matrix)):
            for j in range(0, len(heuristic_matrix[i])):
                heuristic += heuristic_matrix[i][j]

        return heuristic

    """
    def value(self):
        return 1

    def max_value(self):
        val = -1  # Heuristic is non-negative
        successors = []

        for successor in successors:
            v = max(val, successor.value())
        return val

    def exp_value(self):
        val = 0
        successors = []

        for successor in successors:
            prob = successor.probability()
            val += prob * successor.value()

        return val

    def probability(self):
        return 1

"""

    def get_successor(self, myaction, youraction):
        successor = copy.deepcopy(self)

        # Handle one or both players switching, damaging moves only
        if myaction.switch:
            for mon in self.my_team:
                if mon == myaction:
                    successor.my_mon_out = mon
            assert successor.my_mon_out != self.my_mon_out
            if not youraction.switch:
                successor.my_mon_out.present_health -= \
                    successor.my_mon_out.damage_calc(youraction, successor.your_mon_out)
        if youraction.switch:
            for mon in self.your_team:
                if mon.name == youraction.name:
                    successor.your_mon_out = mon
            assert successor.your_mon_out != self.your_mon_out
            if not myaction.switch:
                successor.your_mon_out.present_health -= \
                successor.your_mon_out.damage_calc(myaction, successor.my_mon_out)


class Action:
    def __init__(self, action, switch=False):
        self.name = action
        self.switch = switch