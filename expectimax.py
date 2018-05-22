import interface as f
import state as s
import time
from selenium import common


def act():
    print("Act called")
    can_move = True
    can_switch = True

    # Cause the exception to happen before making a new state
    try:
        f.driver.find_element_by_name("chooseMove")
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

    if can_switch and not can_move:
        time.sleep(1)
        try:
            f.driver.find_element_by_name("chooseMove")
            can_move = True
        except common.exceptions.NoSuchElementException:
            can_move = False
        except common.exceptions.ElementNotVisibleException:
            can_move = False

    if can_move and not can_switch:
        time.sleep(1)
        try:
            f.driver.find_element_by_class_name("switchmenu")
            can_switch = True
        except common.exceptions.NoSuchElementException:
            can_switch = False
        except common.exceptions.ElementNotVisibleException:
            can_switch = False

    print("Switch: " + str(can_switch) + " | Move: " + str(can_move))
    if not can_switch and not can_move:
        raise CantMoveError("Can't move")

    f.update(can_switch and not can_move)
    current_state = s.State(f.own_team, f.opponent_team, f.own_mon_out,
                            f.opponent_mon_out, can_move, can_switch)
    action = current_state.get_best_action()
    print(action.name)
    f.act(action.name, action.switch)
    print("Acted")


class CantMoveError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def fight():
    """Find a random battle and play it to the end."""
    f.get_own_team()

    try:
        f.driver.find_element_by_name("openTimer").click()
        time.sleep(0.500)
        f.driver.find_element_by_name("timerOn").click()
    except common.exceptions.NoSuchElementException:
        f.driver.find_element_by_name("openTimer").click()

    battle_over = False

    while not battle_over:
        try:
            # Attempt to take turn. Detect if battle ends
            try:
                replay = f.driver.find_element_by_name("instantReplay")
                time.sleep(1)
                replay = f.driver.find_element_by_name("closeAndMainMenu")
                battle_over = True
                break
            except common.exceptions.NoSuchElementException:
                pass
            act()
        except CantMoveError:
            # Wait for opponent to move
            time.sleep(2)

    # Reset interface
    f.opponent_team = []
    f.own_team = []
    f.own_mon_out = None
    f.opponent_mon_out = None
    f.driver.find_element_by_name("closeAndMainMenu").click()


def fight_random_enemy():
    f.find_randbat()
    fight()


def fight_k_enemies(k):
    for i in range(0,k):
        fight_random_enemy()
        time.sleep(3)


def start():
    f.start()


def make_state():
    """For debugging purposes"""
    return s.State(f.own_team, f.opponent_team, f.own_mon_out,
                   f.opponent_mon_out, True, True)
