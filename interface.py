from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import random

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


class Pokemon:
    def __init__(self, type):
        self.type = type

    """def __init__(self, level, moves, item, ability, presenthealth, totalhealth, stats):
        self.level = level
        self.type = ['normal', 'fighting']
        self.moves = moves
        self.item = item
        self.ability = ability
        self.stats = stats
        self.present_health = presenthealth
        self.total_health = totalhealth
        self.health_percent = presenthealth/totalhealth"""

    def damage_calc(self, enemy_move, enemy_mon):
        rand_number = random.randint(85,100)
        damage = 0
        if enemy_move.physical:
            damage = \
                (((2*enemy_mon.level/5 + 2) * enemy_mon.stats[0]*enemy_move.power/self.stats[1])/50 + 2) * 93/100
        else:
            damage = \
                (((2*enemy_mon.level/5 + 2) * enemy_mon.stats[2]*enemy_move.power/self.stats[3])/50 + 2) * 93/100
        if enemy_move.type in enemy_mon.type:
            damage *= 1.5
        damage *= self.calculate_type_multiplier(enemy_move.type)
        return damage

    def calculate_type_multiplier(self, move_type):
        type_chart = {
            "normal": {"rock": .5, "steel": .5, "ghost": 0},
            "fighting":{"normal": 2, "rock": 2, "steel": 2, "ice": 2, "dark": 2, "psychic": .5,
                        "flying": .5, "poison": .5, "bug": .5, "fairy": .5, "ghost": 0},
            "dragon":{"dragon": 2, "steel": .5, "fairy": 0},
            "fairy":{"dragon": 2, "fighting": 2, "dark": 2, "poison": .5, "steel": .5, "fire": .5},
            "steel":{"fairy": 2, "rock": 2, "ice": 2, "steel": .5, "fire": .5, "water": .5, "electric": .5},
            "fire": {"grass": 2, "bug": 2, "steel": 2, "water": .5, "rock": .5, "fire": .5, "dragon": .5},
            "water":{"fire": 2, "rock": 2, "ground": 2, "grass": .5, "water": .5, "dragon": .5},
            "grass":{"water": 2, "rock": 2, "ground": 2, "flying": .5, "fire": .5, "grass": .5, "bug": .5,
                     "poison": .5, "steel": .5, "dragon": .5},
            "bug":{"grass": 2, "psychic": 2, "dark": 2, "fighting": .5, "flying": .5, "poison": .5, "ghost": .5,
                   "steel": .5, "fire": .5, "fairy": .5},
            "rock":{"ice": 2, "fire": 2, "flying": 2, "bug": 2, "steel": .5, "fighting": .5, "ground": .5},
            "ground":{"fire": 2, "electric": 2, "rock": 2, "steel": 2, "poison": 2, "grass": .5, "bug": .5,
                      "flying": 0},
            "electric":{"water": 2, "flying": 2, "grass": .5, "electric": .5, "dragon": .5, "ground": 0},
            "dark":{"psychic": 2, "ghost": 2, "fighting": .5, "dark": .5, "fairy": .5},
            "ghost":{"ghost": 2, "psychic": 2, "dark": .5, "normal": 0},
            "flying":{"bug": 2, "grass": 2, "fighting": 2, "rock": .5, "steel": .5, "electric": .5},
            "poison":{"grass": 2, "fairy": 2, "poison": .5, "ground": .5, "rock": .5, "ghost": .5, "steel": 0},
            "psychic":{"fighting": 2, "poison": 2, "psychic": .5, "steel": .5, "dark": 0},
            "ice":{"dragon": 2, "flying": 2, "ground": 2, "grass": 2, "steel": .5, "fire": .5,
                   "water": .5, "ice": .5}
        }

        multiplier = 1
        if self.type[0] in type_chart[move_type]:
            multiplier *= type_chart[move_type][self.type[0]]
        if self.type[1] in type_chart[move_type]:
            multiplier *= type_chart[move_type][self.type[1]]

        return multiplier


class Move:
    def __init__(self, type, power, physical):
        self.type = type
        self.power = power
        self.physical = physical