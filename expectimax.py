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
    f.update()
    current_state = s.State(f.own_team, f.opponent_team, f.own_mon_out, f.opponent_mon_out)
    action = current_state.get_best_action()
    f.act(action.name, action.switch)


def fight():
    f.get_own_team()

    while not battle_over:
        try:
            act()

            logs = f.driver.find_elements_by_class_name("battle-history")
            for log in logs:
                log_text = log.text
                if "won the battle!" in log_text:
                    battle_over = True
        except common.exceptions.ElementNotVisibleException:
            time.sleep(2)
