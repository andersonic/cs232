import interface as f
import state as s
import time
from selenium import common


def start():
    f.start()


def fight_random_enemy():
    f.find_randbat()
    fight()


def act():
    # Cause the exception to happen before making a new state
    can_move = True
    can_switch = True

    try:
        f.driver.find_element_by_class_name("movemenu")
    except common.exceptions.NoSuchElementException:
        can_move = False
    except common.exceptions.ElementNotVisibleException:
        can_move = False
    try:
        f.driver.find_element_by_class_name("switchmenu")
    except common.exceptions.NoSuchElementException:
        can_switch = False
    except common.exceptions.ElementNotVisibleException:
        can_switch = False

    if not can_switch and not can_move:
        raise CantMoveError("Can't move")

    f.update(can_switch and not can_move)
    current_state = s.State(f.own_team, f.opponent_team, f.own_mon_out, f.opponent_mon_out,
                            can_move, can_switch)
    action = current_state.get_best_action()
    f.act(action.name, action.switch)


def make_state():
    return s.State(f.own_team, f.opponent_team, f.own_mon_out, f.opponent_mon_out,
                            True, True)


class CantMoveError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def fight():
    f.get_own_team()

    battle_over = False

    while not battle_over:
        try:
            act()

            logs = f.driver.find_elements_by_class_name("battle-history")
            for log in logs:
                log_text = log.text
                if "won the battle!" in log_text:
                    battle_over = True
        except CantMoveError:
            time.sleep(2)

    f.opponent_team = []
    f.own_team = []
    f.own_mon_out = None
    f.opponent_mon_out = None
