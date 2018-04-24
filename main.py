from selenium import common
import random
import interface as i


def random_switch():
    options = i.get_switch_options()
    selection = options[random.randint(0, len(options) - 1)]
    i.act(selection, True)


def random_move():
    options = i.get_move_options()
    selection = options[random.randint(0, len(options) - 1)]
    i.act(selection)


def start():
    i.open_window("https://play.pokemonshowdown.com")
    i.log_in("cs232-test-1", "cs232")
    i.find_randbat()


def random_action():
    switch_prob = 30
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
            random_switch()
        else:
            random_move()
    elif switch_allowed:
        random_switch()
    elif move_allowed:
        random_move()
    else:
        print("Can't do anything")