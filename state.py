import math
import copy

BEST_MATCHUP = 0
GOOD_MATCHUP = 1
TIE = 2
BAD_MATCHUP = 3
WORST_MATCHUP = 4


class State:

    def __init__(self, my_team, your_team, my_mon_out, your_mon_out,
                 can_move, can_switch):
        self.my_team = my_team
        self.your_team = your_team
        self.my_mon_out = my_mon_out
        self.your_mon_out = your_mon_out
        self.can_move = can_move
        self.can_switch = can_switch

    def get_best_action(self):
        """Returns an Action that is the best action the user can take given
        the State."""
        action = self.value()
        return self.get_my_actions()[action[1].index(action[0])]

    def value(self, depth=0):
        """Returns the value of a state. Also returns the array of values
        so that the action leading to the best expected value may be
        determined."""
        MAX_DEPTH = 1
        if depth >= MAX_DEPTH:
            return self.get_heuristic(), None
        else:
            successor_matrix = self.make_successor_matrix()
            probs = self.get_prob(successor_matrix)

            # Multiply each row by its probability. Then sum the columns, and pick the best one
            col_sums = [0 for i in range(len(successor_matrix[0]))]

            for i in range(0, len(successor_matrix)):
                for j in range(0, len(successor_matrix[0])):
                    col_sums[j] += probs[i] * successor_matrix[i][j].value(depth + 1)[0]

            return min(col_sums), col_sums

    def get_heuristic(self):
        """Sum the matchup values of each possible user-opponent
        1v1 Pokémon matchup"""
        heuristic_matrix = self.make_matchup_matrix()
        return sum([sum(row) for row in heuristic_matrix])

    def make_matchup_matrix(self):
        matchup_matrix = [[None for j in range(0, 6)] for i in range(0, 6)]

        for i in range(0, len(matchup_matrix)):
            for j in range(0, len(matchup_matrix[i])):
                try:
                    my_mon = self.my_team[j]
                    your_mon = self.your_team[i]
                    if my_mon.present_health <= 0 and your_mon.present_health <= 0:
                        matchup_matrix[i][j] = TIE
                    elif my_mon.present_health <= 0:
                        matchup_matrix[i][j] = WORST_MATCHUP
                    elif your_mon.present_health <= 0:
                        matchup_matrix[i][j] = BEST_MATCHUP
                    else:
                        matchup_matrix[i][j] = self.get_matchup(my_mon, your_mon)
                except IndexError:
                    my_mon = self.my_team[j]
                    if my_mon.present_health <= 0:
                        matchup_matrix[i][j] = WORST_MATCHUP
                    else:
                        matchup_matrix[i][j] = TIE
                except AttributeError:
                    matchup_matrix[i][j] = TIE

        return matchup_matrix

    @staticmethod
    def get_matchup(my_mon, your_mon):
        if your_mon is None:
            return TIE

        my_best_damage = State.get_max_damage_percent(my_mon, your_mon)
        your_best_damage = State.get_max_damage_percent(your_mon, my_mon)

        faster = State.get_faster(my_mon, your_mon)

        if my_mon is faster and my_best_damage >= 100:
            # Outspeed and OHKO
            return BEST_MATCHUP
        elif your_mon is faster and your_best_damage >= 100:
            # Get outsped and OHKO'd
            return WORST_MATCHUP
        elif my_mon is faster and your_best_damage >= 100 and my_best_damage >= 50:
            # Deal damage before being KO'd
            return BAD_MATCHUP
        elif your_mon is faster and my_best_damage >= 100 and your_best_damage >= 50:
            # Receive damage before being KO'd
            return GOOD_MATCHUP
        elif my_mon is faster and my_best_damage >= your_best_damage:
            return GOOD_MATCHUP
        elif your_mon is faster and your_best_damage >= my_best_damage:
            return BAD_MATCHUP
        elif my_best_damage >= 2 * your_best_damage:
            return GOOD_MATCHUP
        elif your_best_damage >= 2 * my_best_damage:
            return BAD_MATCHUP
        return TIE

    @staticmethod
    def get_faster(my_mon, your_mon):
        """Return the faster of the two Pokémon. In the case of a speed tie,
        return None."""
        if my_mon.calc_real_stats()[4] > your_mon.calc_real_stats()[4]:
            return my_mon
        elif my_mon.calc_real_stats()[4] < your_mon.calc_real_stats()[4]:
            return your_mon
        else:
            return None

    @staticmethod
    def get_max_damage_percent(user, target):
        """Calculate the maximum damage Pokémon user can deal to Pokémon
        target. Return as a percent of target's current health."""
        max_damage = 0
        for move in user.moves:
            damage = move.damage_calc(user, target)
            if damage > max_damage:
                max_damage = damage

        return max_damage * 100 / target.present_health

    def make_successor_matrix(self):
        return self.aux_make_successor_matrix(self.get_my_actions(),
                                              self.get_your_actions())

    def aux_make_successor_matrix(self, myactions, youractions):
        """Given all possible actions by both players, return a 2D
        array of all possible successor states, index as
        [opponent action][player action]."""
        successor_matrix = []
        for youraction in youractions:
            row = []
            for myaction in myactions:
                row.append(self.get_successor(myaction, youraction))
            successor_matrix.append(row)
        return successor_matrix

    def get_successor(self, myaction, youraction):
        """Determine successor state given both players' actions."""
        successor = copy.deepcopy(self)

        if myaction.switch or youraction.switch:
            return self.successor_with_switch(successor, myaction, youraction)
        else:
            return self.successor_both_move(successor, myaction, youraction)

    def successor_with_switch(self, successor, myaction, youraction):
        """Handle one or both players switching, damaging moves only"""
        if myaction.switch:
            successor.my_mon_out.boosts = [0 for i in range(0,5)]
            for mon in successor.my_team:
                if mon == myaction.action:
                    successor.my_mon_out = mon
            assert successor.my_mon_out != self.my_mon_out
            if not youraction.switch:
                youraction.action.apply_move(successor.your_mon_out, successor.my_mon_out)
        if youraction.switch:
            successor.your_mon_out.boosts = [0 for i in range(0,5)]
            for mon in successor.your_team:
                if mon.name == youraction.name:
                    successor.your_mon_out = mon
            assert successor.your_mon_out != self.your_mon_out
            if not myaction.switch:
                myaction.action.apply_move(successor.my_mon_out, successor.your_mon_out)
        return successor

    def successor_both_move(self, successor, my_action, your_action):
        """Handle both players moving"""
        faster = self.get_faster(successor.my_mon_out, successor.your_mon_out)

        myaction = my_action.action
        youraction = your_action.action

        if faster is None:
            # Assume you lose the speed tie for now
            faster = successor.your_mon_out

        if successor.your_mon_out is faster:
            youraction.apply_move(successor.your_mon_out, successor.my_mon_out)

            if successor.my_mon_out.present_health > 0:
                myaction.apply_move(successor.my_mon_out, successor.your_mon_out)
        else:
            myaction.apply_move(successor.my_mon_out, successor.your_mon_out)

            if successor.your_mon_out.present_health > 0:
                youraction.apply_move(successor.your_mon_out, successor.my_mon_out)
        return successor

    def get_my_actions(self):
        """Get all possible actions."""
        moves = []
        switches = []
        if self.can_move:
            moves = [Action(move) for move in self.my_mon_out.available_moves]
        if self.can_switch:
            switches = [Action(switch, True) for switch in self.my_team if
                        (switch is not self.my_mon_out and switch.present_health > 0)]

        actions = moves + switches
        print([action.name for action in actions])
        return actions

    def get_your_actions(self):
        moves = [Action(move) for move in self.your_mon_out.moves]
        switches = [Action(switch, True) for switch in self.your_team if
                    (switch is not self.your_mon_out and switch.present_health > 0)]
        return moves + switches

    @staticmethod
    def get_prob(matrix):
        """Given a 2-D matrix of floats, return a 1-D array proportional to the sums of the columns,
        adjusted to sum to 1."""

        row_sums = []
        for i in range(0, len(matrix)):
            row_sum = 0
            for j in range(0, len(matrix[i])):
                row_sum += matrix[i][j].get_heuristic()
            row_sums.append(row_sum)

        total = sum(row_sums)
        for number in row_sums:
            try:
                number /= total
            except ZeroDivisionError:
                pass

        return row_sums


class Action:
    def __init__(self, action, switch=False):
        self.name = action.name
        self.switch = switch
        self.action = action
