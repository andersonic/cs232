from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import os

driver = None


def open_window(url):
    my_dir = os.path.dirname(__file__)
    chrome_path = os.path.join(my_dir, 'chromedriver')
    new_driver = webdriver.Chrome(chrome_path)
    new_driver.get(url)
    global driver
    driver = new_driver
    driver.implicitly_wait(3)


def log_out():
    driver.find_element_by_name("openOptions").click()
    try:
        driver.find_element_by_name("logout").click()
        driver.find_element_by_tag_name("strong").click()
    except common.exceptions.NoSuchElementException:
        pass
    driver.refresh()


def log_in(username, password):
    log_out()

    logged_in = False

    driver.find_element_by_name("login").click()
    username_field = driver.find_element_by_name("username")
    username_field.send_keys(username)
    username_field.send_keys(Keys.RETURN)

    try:
        password_field = driver.find_element_by_name("password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
    except common.exceptions.NoSuchElementException:
        logged_in = True

    try:
        driver.find_element_by_name("input")
        logged_in = False
    except common.exceptions.NoSuchElementException:
        logged_in = True

    return logged_in


def find_randbat():
    driver.find_element_by_name("search").click()


def act(action, switch=False):
    if switch:
        pokemon_buttons = driver.find_elements_by_name("chooseSwitch")
        for pokemon in pokemon_buttons:
            if pokemon.text == action:
                pokemon.click()
                return True
    else:
        move_buttons = driver.find_elements_by_name("chooseMove")
        for move in move_buttons:
            if move.text.split('\n')[0] == action:
                move.click()
                return True
    return False


def send_out_team_preview(pokemon_name):
    pokemon_buttons = driver.find_elements_by_name("chooseTeamPreview")
    for pokemon in pokemon_buttons:
        if pokemon.text == pokemon_name:
            pokemon.click()
            return True
    return False


def send_out_after_KO(pokemon_name):
    act(pokemon_name, True)


def mega_evolve():
    try:
        driver.find_element_by_class("megaevo").click()
        return True
    except common.exceptions.NoSuchElementException:
        return False


def get_preview_options():
    options = []
    pokemon_buttons = driver.find_elements_by_name("chooseTeamPreview")
    for pokemon in pokemon_buttons:
        options.append(pokemon.text)
    return options


def get_move_options():
    moves = []
    move_buttons = driver.find_elements_by_name("chooseMove")
    for move in move_buttons:
        moves.append(move.text.split('\n')[0])
    return moves


def get_switch_options():
    pokemon_list = []
    pokemon_buttons = driver.find_elements_by_name("chooseSwitch")
    for pokemon in pokemon_buttons:
        pokemon_list.append(pokemon.text)
    return pokemon_list


def get_own_team():
    """Precondition: first turn. Returns all Pokémon, including stats, moves and items."""

    pokemon_list = []

    current_mon = driver.find_element_by_name("chooseDisabled")
    hover = ActionChains(driver).move_to_element(current_mon)
    hover.perform()
    pokemon_text = driver.find_element_by_id("tooltipwrapper").text
    pokemon_list.append(parse_tooltip_text(pokemon_text))

    benched_mons = driver.find_elements_by_name("chooseSwitch")

    for mon in benched_mons:
        hover = ActionChains(driver).move_to_element(mon)
        hover.perform()
        pokemon_text = driver.find_element_by_id("tooltipwrapper").text
        pokemon_list.append(parse_tooltip_text(pokemon_text))

    return pokemon_list


def parse_tooltip_text(text):
    text = text.split("\n")
    level = int(text[0].split(" ")[len(text[0].split(" ")) - 1][1:])
    current_health = int(text[1].split(" ")[2].split("/")[0][1:])

    total_health_text = text[1].split(" ")[2].split("/")[1]

    total_health = int(total_health_text[0:len(total_health_text) - 1])

    temp = text[2].split(" / ")
    ability = " ".join(temp[1].split(" ")[1:])
    item = " ".join(temp[1].split(" ")[1:])

    stats = text[3].split("/")
    temp = []
    for i in range(0,5):
        pieces = stats[i].split(" ")
        for piece in pieces:
            if piece != "":
                temp.append(int(piece))
                break
    stats = temp

    moves = []
    try:
        for i in range(4, 8):
            moves.append(text[i][2:])
    except IndexError:
        pass

    return Pokemon(level, moves, item, ability, current_health, total_health, stats)


class Pokemon():
    def __init__(self, level, moves, item, ability, presenthealth, totalhealth, stats):
        self.level = level
        self.type = []
        self.moves = moves
        self.item = item
        self.ability = ability
        self.stats = stats
        self.present_health = presenthealth
        self.total_health = totalhealth
        self.health_percent = presenthealth/totalhealth