from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import random
import math
import time
import os
import demjson

driver = None
all_pokemon_data = demjson.decode(open('pokemon_data.txt', 'r').read())


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


def start():
    open_window("https://play.pokemonshowdown.com")
    log_in("cs232-test-1", "cs232")


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
    pokemon = driver.find_element_by_id("tooltipwrapper")
    pokemon_list.append(parse_own_team(pokemon))

    benched_mons = driver.find_elements_by_name("chooseSwitch")

    for mon in benched_mons:
        hover = ActionChains(driver).move_to_element(mon)
        hover.perform()
        pokemon_list.append(parse_own_team(driver.find_element_by_id("tooltipwrapper")))

    return pokemon_list


def parse_own_team(element):
    text = element.text

    # Get health
    text = text.split("\n")
    level = int(text[0].split(" ")[len(text[0].split(" ")) - 1][1:])
    current_health = int(text[1].split(" ")[2].split("/")[0][1:])
    total_health_text = text[1].split(" ")[2].split("/")[1]
    total_health = int(total_health_text[0:len(total_health_text) - 1])

    # Get ability and item
    temp = text[2].split(" / ")
    ability = " ".join(temp[1].split(" ")[1:])
    item = " ".join(temp[1].split(" ")[1:])

    # Get stats
    stats = text[3].split("/")
    temp = []
    for i in range(0,5):
        pieces = stats[i].split(" ")
        for piece in pieces:
            if piece != "":
                temp.append(int(piece))
                break
    stats = temp

    # Get moves
    moves = []
    try:
        for i in range(4, 8):
            moves.append(text[i][2:])
    except IndexError:
        pass

    for move in moves:
        query_data(move)
    time.sleep(1)

    moves = [parse_move_text(i) for i in moves]

    images = element.find_elements_by_tag_name("img")
    types = []
    for image in images:
        if image.get_attribute("alt") is not "M" and image.get_attribute("alt") is not "F":
            types.append(image.get_attribute("alt"))
    if len(types) == 1:
        types.append('none')

    return Pokemon(level, types, moves, item, ability, current_health, total_health, stats)


def query_data(data):
    textbox = driver.find_element_by_class_name("battle-log-add").find_elements_by_class_name("textbox")[1]
    textbox.send_keys("/data " + data)
    textbox.send_keys(Keys.ENTER)


def retrieve_data():
    return driver.find_elements_by_class_name("utilichart")


def calc_stats(base_stats, level):
    stats = []
    stats.append(math.floor((31 + 2 * base_stats[0] + 21) * level/100 + 10 + level))

    for i in range(1, 5):
        stats.append(math.floor((31 + 2 * base_stats[i] + 21) * level/100 + 5))

    return stats


def get_base_stats(mon):
    query_data(mon)
    time.sleep(1)
    all_mons = retrieve_data()
    base_stats = []
    for pokemon in all_mons:
        if pokemon.text.split('\n')[1] == mon:
            stat_list = pokemon.find_elements_by_class_name("statcol")
            for stat in stat_list:
                base_stats.append(int(stat.text.split("\n")[1]))
    return base_stats


def get_possible_moves(name):
    return all_pokemon_data[name.replace(" ", "").lower()]['randomBattleMoves']


def handle_list_moves(moves):
    for move in moves:
        query_data(move)
    time.sleep(1)
    parsed_moves = [parse_move_text(i) for i in moves]
    return parsed_moves


def parse_opposing_mon():
    # Get element with data
    enemy_mon = driver.find_element_by_class_name("foehint").find_elements_by_tag_name("div")[2]
    hover = ActionChains(driver).move_to_element(enemy_mon)
    hover.perform()
    tooltip = driver.find_element_by_id("tooltipwrapper")

    help_text = tooltip.text.split("\n")

    name_temp = help_text[0].split(" ")
    name = " ".join(name_temp[:len(name_temp) - 1])

    level = int(name_temp[len(name_temp) - 1][1:])

    base_stats = get_base_stats(name)

    stats = calc_stats(base_stats, level)

    images = tooltip.find_elements_by_tag_name("img")
    types = []
    for image in images:
        if image.get_attribute("alt") is not "M" and image.get_attribute("alt") is not "F":
            types.append(image.get_attribute("alt"))

    if len(types) == 1:
        types.append('none')

    moves = handle_list_moves(get_possible_moves(name))

    return Pokemon(level, types, moves, None, None, stats[0], stats[0], stats[1:])



class Pokemon:
    def __init__(self, level, type, moves, item, ability, presenthealth, totalhealth, stats):
        self.level = level
        self.type = type
        self.moves = moves
        self.item = item
        self.ability = ability
        self.stats = stats
        self.present_health = presenthealth
        self.total_health = totalhealth
        self.health_percent = presenthealth/totalhealth

    def damage_calc(self, enemy_move, enemy_mon):
        rand_number = random.randint(85,100)
        damage = 0
        if enemy_move.category == 'Physical':
            damage = \
                (((2*enemy_mon.level/5 + 2) * enemy_mon.stats[0]*enemy_move.power/self.stats[1])/50 + 2) * 93/100
        elif enemy_move.category == 'Special':
            damage = \
                (((2*enemy_mon.level/5 + 2) * enemy_mon.stats[2]*enemy_move.power/self.stats[3])/50 + 2) * 93/100
        if enemy_move.type in enemy_mon.type:
            damage *= 1.5
        damage *= self.calculate_type_multiplier(enemy_move.type)
        return damage

    def calculate_type_multiplier(self, move_type):
        type_chart = {
            "Normal": {"Rock": .5, "Steel": .5, "Ghost": 0},
            "Fighting":{"Normal": 2, "Rock": 2, "Steel": 2, "Ice": 2, "Dark": 2, "Psychic": .5,
                        "Flying": .5, "Poison": .5, "Bug": .5, "Fairy": .5, "Ghost": 0},
            "Dragon":{"Dragon": 2, "Steel": .5, "Fairy": 0},
            "Fairy":{"Dragon": 2, "Fighting": 2, "Dark": 2, "Poison": .5, "Steel": .5, "Fire": .5},
            "Steel":{"Fairy": 2, "Rock": 2, "Ice": 2, "Steel": .5, "Fire": .5, "Water": .5, "Electric": .5},
            "Fire": {"Grass": 2, "Bug": 2, "Steel": 2, "Water": .5, "Rock": .5, "Fire": .5, "Dragon": .5},
            "Water":{"Fire": 2, "Rock": 2, "Ground": 2, "Grass": .5, "Water": .5, "Dragon": .5},
            "Grass":{"Water": 2, "Rock": 2, "Ground": 2, "Flying": .5, "Fire": .5, "Grass": .5, "Bug": .5,
                     "Poison": .5, "Steel": .5, "Dragon": .5},
            "Bug":{"Grass": 2, "Psychic": 2, "Dark": 2, "Fighting": .5, "Flying": .5, "Poison": .5, "Ghost": .5,
                   "Steel": .5, "Fire": .5, "Fairy": .5},
            "Rock":{"Ice": 2, "Fire": 2, "Flying": 2, "Bug": 2, "Steel": .5, "Fighting": .5, "Ground": .5},
            "Ground":{"Fire": 2, "Electric": 2, "Rock": 2, "Steel": 2, "Poison": 2, "Grass": .5, "Bug": .5,
                      "Flying": 0},
            "Electric":{"Water": 2, "Flying": 2, "Grass": .5, "Electric": .5, "Dragon": .5, "Ground": 0},
            "Dark":{"Psychic": 2, "Ghost": 2, "Fighting": .5, "Dark": .5, "Fairy": .5},
            "Ghost":{"Ghost": 2, "Psychic": 2, "Dark": .5, "Normal": 0},
            "Flying":{"Bug": 2, "Grass": 2, "Fighting": 2, "Rock": .5, "Steel": .5, "Electric": .5},
            "Poison":{"Grass": 2, "Fairy": 2, "Poison": .5, "Ground": .5, "Rock": .5, "Ghost": .5, "Steel": 0},
            "Psychic":{"Fighting": 2, "Poison": 2, "Psychic": .5, "Steel": .5, "Dark": 0},
            "Ice":{"Dragon": 2, "Flying": 2, "Ground": 2, "Grass": 2, "Steel": .5, "Fire": .5,
                   "Water": .5, "Ice": .5}
        }

        multiplier = 1
        if self.type[0] in type_chart[move_type]:
            multiplier *= type_chart[move_type][self.type[0]]
        if self.type[1] in type_chart[move_type]:
            multiplier *= type_chart[move_type][self.type[1]]

        return multiplier


class Move:
    def __init__(self, type, power, category):
        self.type = type
        self.power = power
        self.category = category


def parse_move_text(move):
    all_stuff = retrieve_data()
    move_data = None
    for item in all_stuff:
        move_name = item.text.split('\n')[0]
        if move_name == move or move_name.replace(" ", "").lower() == move:
            move_data = item

    images = move_data.find_element_by_class_name("typecol").find_elements_by_tag_name("img")
    type = images[0].get_attribute("alt")
    category = images[1].get_attribute("alt")
    power = 0

    if category != "Status":
        try:
            power = int(move_data.text.split("\n")[2])
        except ValueError:
            pass


    return Move(type, power, category)