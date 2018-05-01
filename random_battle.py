from selenium import common
import random
import interface as i
import time

"""Plays randbats randomly, with a set probability to switch. Does not store game state,
as the game state does not affect its actions."""


def start():
    i.open_window("https://play.pokemonshowdown.com")
    i.log_in("cs232-test-3", "cs232")


def random_switch():
    options = i.get_switch_options()
    selection = options[random.randint(0, len(options) - 1)]
    i.act(selection, True)


def random_move():
    options = i.get_move_options()
    selection = options[random.randint(0, len(options) - 1)]
    i.act(selection)


def random_action(prob=30):
    switch_prob = prob
    switch_allowed = True
    move_allowed = True

    try:
        i.driver.find_element_by_class_name("switchmenu")
    except common.exceptions.NoSuchElementException:
        switch_allowed = False

    try:
        i.driver.find_element_by_class_name("movemenu")
    except common.exceptions.NoSuchElementException:
        move_allowed = False

    if switch_allowed and move_allowed:
        if random.randint(1, 100) < switch_prob:
            try:
                random_switch()
            except ValueError:
                random_move()
        else:
            random_move()
    elif switch_allowed:
        random_switch()
    elif move_allowed:
        random_move()
    else:
        print("Can't do anything")


def feist():
    switch_prob = 30
    battle_over = False

    while not battle_over:
        try:
            i.driver.find_element_by_class_name("movemenu")
            random_action(switch_prob)
        except common.exceptions.NoSuchElementException:
            try:
                i.driver.find_element_by_class_name("switchmenu")
                random_action(switch_prob)
            except:
                pass

        logs = i.driver.find_elements_by_class_name("battle-history")
        for log in logs:
            log_text = log.text
            if "won the battle!" in log_text:
                battle_over = True


def feist_random_enemy():
    i.find_randbat()
    feist()


def feist_k_enemies(k=1):
    for count in range(0,k):
        feist_random_enemy()
        i.driver.find_element_by_name("closeRoom").click()
        time.sleep(2)
