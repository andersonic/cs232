# -*- coding: cp1252 -*-
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import math
import time
import os
import json

driver = None
#all_pokemon_data = demjson.decode(open('pokemon_data.txt', 'r').read())
with open('pokemon_data.txt') as r:
    all_pokemon_data = json.load(r)
own_team = []
opponent_team = []
game_state = {'rocks':False, 'spikes': 0, 'tspikes': 0, 'weather':'none', 'trickroom':False, 'terrain':'none'}
turn = 0
own_mon_out = None
opponent_mon_out = None
driver = None


def open_window(url):
    chrome_path = os.path.join(os.getcwd() ,'driver/chromedriver')
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
    """Take an action (a move name or a Pokémon name) as a parameter and whether the action is a switch."""
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

    global own_team
    own_team = pokemon_list
    return pokemon_list


def parse_own_team(element):
    text = element.text

    # Get health
    text = text.split("\n")
    name = " ".join(text[0].split(" ")[:len(text[0].split(" "))-1])
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
    time.sleep(2)

    moves = [parse_move_text(i) for i in moves]

    images = element.find_elements_by_tag_name("img")
    types = []
    for image in images:
        if image.get_attribute("alt") is not "M" and image.get_attribute("alt") is not "F":
            types.append(image.get_attribute("alt"))
    if len(types) == 1:
        types.append('none')

    return Pokemon(name, level, types, moves, item, ability, current_health, total_health, stats)


def query_data(data):
    textbox = driver.find_element_by_class_name("battle-log-add").find_elements_by_class_name("textbox")[1]
    textbox.send_keys("/data " + data)
    textbox.send_keys(Keys.ENTER)


def retrieve_data():
    return driver.find_elements_by_class_name("utilichart")


def calc_stats(base_stats, level):
    stats = []
    stats.append(math.floor((31 + 2 * base_stats[0] + 21) * level/100 + 10 + level))

    for i in range(1, 6):
        stats.append(math.floor((31 + 2 * base_stats[i] + 21) * level/100 + 5))

    return stats


def get_base_stats(mon):
    query_data(mon)
    time.sleep(1)
    all_mons = retrieve_data()
    base_stats = []
    for pokemon in all_mons:
        try:
            if pokemon.text.split('\n')[1] == mon:
                stat_list = pokemon.find_elements_by_class_name("statcol")
                for stat in stat_list:
                    base_stats.append(int(stat.text.split("\n")[1]))
                break
        except IndexError:
            pass
    return base_stats


def get_possible_moves(name):
    return all_pokemon_data[name.replace(" ", "").lower()]['randomBattleMoves']


def handle_list_moves(moves):
    for move in moves:
        query_data(move)
    time.sleep(2)
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

    new_mon = Pokemon(name, level, types, moves, None, None, stats[0], stats[0], stats[1:])
    if new_mon not in opponent_team:
        opponent_team.append(new_mon)
    return new_mon


class Pokemon:
    def __init__(self, name=None, level=None, type=None, moves=None, item=None, ability=None, presenthealth=None,
                 totalhealth=None, stats=None, statuses={}, mon=None):
        if mon is None:
            self.name = name
            self.level = level
            self.type = type
            self.moves = moves
            self.item = item
            self.ability = ability
            self.stats = stats
            self.present_health = presenthealth
            self.total_health = totalhealth
            self.health_percent = presenthealth/totalhealth
            self.statuses = statuses
        else:
            # For form changes ????
            self.name = name
            self.level = mon.level
            self.type = type
            self.moves = mon.moves
            self.ability = ability
            self.present_health = mon.presenthealth
            self.total_health = mon.totalhealth
            self.stat = stats
            self.statuses = mon.statuses

    def get_health_percent(self):
        self.health_percent = self.present_health/self.total_health
        return self.health_percent

    def __eq__(self, other):
        """Note that this definition of equality breaks down when comparing Pokémon on opposite teams"""
        return self.name == other.name

    def __str__(self):
        return self.name

    def damage_calc(self, enemy_move, enemy_mon):
        enemy_stats = enemy_mon.calc_effective_stats()
        my_stats = self.calc_effective_stats()
        damage = 0
        if enemy_move.category == 'Physical':
            damage = \
                (((2*enemy_mon.level/5 + 2) * enemy_stats[0]*enemy_move.power/my_stats[1])/50 + 2) * 93/100
        elif enemy_move.category == 'Special':
            damage = \
                (((2*enemy_mon.level/5 + 2) * enemy_stats[2]*enemy_move.power/my_stats[3])/50 + 2) * 93/100
        if enemy_move.type in enemy_mon.type:
            damage *= 1.5
        damage *= self.calculate_type_multiplier(enemy_move.type)
        return damage

    def calc_effective_stats(self):
        real_stats = []
        for i in range(0, len(self.stats)):
            if i == 0:
                # dealing with attack
                atk_mod = 1
                if "BRN" in self.statuses:
                    atk_mod *= 0.5
                if "Atk" in self.statuses:
                    atk_mod *= self.statuses["Atk"]
                real_stats.append(self.stats[i] * atk_mod)
            elif i == 1:
                # dealing with defense
                try:
                    real_stats.append(self.stats[i] * self.statuses["Def"])
                except KeyError:
                    real_stats.append(self.stats[i])
            elif i == 2:
                try:
                    real_stats.append(self.stats[i] * self.statuses["SpA"])
                except KeyError:
                    real_stats.append(self.stats[i])
            elif i == 3:
                try:
                    real_stats.append(self.stats[i] * self.statuses["SpD"])
                except KeyError:
                    real_stats.append(self.stats[i])
            elif i == 4:
                spe_mod = 1
                if "PAR" in self.statuses:
                    spe_mod *= 0.25
                if "Spe" in self.statuses:
                    spe_mod *= self.statuses["Spe"]
                real_stats.append(self.stats[i] * spe_mod)
        return real_stats

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
        if move_name == move or move_name.replace(" ", "").replace("-", "").lower() == move:
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


def update():
    """Pre-condition: battle state is up to date until turn_to_parse - 1.
    Post-condition: battle state is up to date. Except it probably misses loads of stuff"""

    # Below is the log-reading method
    """first_line = 0
    last_line = 0
    logs = driver.find_elements_by_class_name("battle-history")
    logs = [log.text for log in logs]
    for i in range(0, len(logs)):
        if logs[i] == "Turn " + str(turn_to_parse):
            first_line = i
        if logs[i] == "Turn " + str(turn_to_parse + 1):
            last_line = i
    relevant_logs = logs[first_line:last_line]
    for log in relevant_logs:
        if " used " in log:
            # someone used a move
            # Do I care?
            pass
        elif " lost " in log:
            # someone lost health, due to being hit or life orb
            percent = extract_percent(log)
            if " opposing " in log:
                # opponent lost health
                opponent_mon_out.current_health *= percent
            else:
                # own pokemon lost health. find percent and multiply
                own_mon_out.current_health *= percent
        elif " restored " in log:
            # someone recovered health
        elif "Pointed stones dug into " in log:
            # someone took stealth rocks damage
            if "the opposing" in log:
                # opposing mon took rocks damage
        elif " had its energy drained!" in log:
            # someone recovered health through draining
        elif " fainted " in log:
            # someone fainted
            # should be detected elsewhere
            pass
        elif "Go! " in log:
            # player send someone out. switch out pokemon
        elif " sent out " in log:
            # opponent sent someone out. see if they need to be added to opponent team. switch out mon"""

    first_line = 0
    logs = [log.text for log in driver.find_elements_by_class_name("battle-history")]
    turns = [log for log in logs if "Turn " in log]
    most_recent_turn = turns[len(turns) - 1]
    for i in range(0, len(logs)):
        if logs[i] == most_recent_turn:
            first_line = i
    logs = logs[first_line:]

    my_fainted_mon = None
    your_fainted_mon = None
    for log in logs:
        if " fainted!" and " opposing " in log:
            # An opposing Pokémon has fainted
            name = log.split(" ")[2]
            for mon in opponent_team:
                if mon.name == name:
                    your_fainted_mon = mon
            # Harder because you might send an unrevealed mon in to die right away
        elif " fainted!" in log:
            # One of your Pokémon has fainted
            name = log.split(" ")[0]
            for mon in own_team:
                if mon.name == name:
                    my_fainted_mon = mon
            assert my_fainted_mon is not None

    if your_fainted_mon is not None:
        your_fainted_mon.present_health = 0
        if my_fainted_mon is None:
            update_opponent()
    if my_fainted_mon is not None:
        my_fainted_mon.present_health = 0
    else:
        update_own_mon()



def update_own_mon():
    try:
        statbar = driver.find_element_by_class_name("rstatbar")
        mon = " ".join(statbar.text.split(" ")[:len(statbar.text.split(" ")) - 1])
        global own_mon_out

        try:
            if own_mon_out.name != mon:
                for pokemon in own_team:
                    if pokemon.name == mon:
                        own_mon_out = pokemon
        except AttributeError:
            for pokemon in own_team:
                if pokemon.name == mon:
                    own_mon_out = pokemon
        hptext = statbar.find_element_by_class_name("hptext").text
        health_percent = int(hptext[:len(hptext) - 1]) / 100
        own_mon_out.present_health = own_mon_out.total_health * health_percent
        update_status(own_mon_out, statbar)
    except common.exceptions.NoSuchElementException:
        # Your Pokémon is not there, either because it fainted or because you have used a switching move
        # For now, assume it is due to fainting
        own_mon_out.present_health = 0


def update_opponent():
    statbar = driver.find_element_by_class_name("lstatbar")
    mon = " ".join(statbar.text.split(" ")[:len(statbar.text.split(" ")) - 1])

    already_parsed = False
    opp_mon_out = None

    for pokemon in opponent_team:
        if mon == pokemon.name:
            already_parsed = True
            opp_mon_out = pokemon
    
    global opponent_mon_out
    if not already_parsed:
        opponent_mon_out = parse_opposing_mon()
    elif opponent_mon_out == None or opponent_mon_out.name != mon:
        opponent_mon_out = opp_mon_out

    hptext = statbar.find_element_by_class_name("hptext").text
    health_percent = int(hptext[:len(hptext) - 1]) / 100
    opponent_mon_out.present_health = opponent_mon_out.total_health * health_percent
    update_status(opponent_mon_out, statbar)


def update_status(pokemon, statbar):
    status = statbar.find_element_by_class_name("status")
    statuses = status.find_elements_by_tag_name("span")
    statuses = [i.text for i in statuses]
    stat_dict = {}
    for s in statuses:
        try:
            text = s.split(" ")
            stat_dict[text[1]] = float(text[0][:len(text[0]) - 1])
        except ValueError:
            stat_dict[s] = True
    pokemon.statuses = stat_dict


def extract_percent(text):
    percent_as_int = 0
    percent_index = 0
    for i in range(0, len(text)):
        if text[i] == "%":
            percent_index = i
    for i in range(percent_index - 1, 0, -1):
        try:
            percent_as_int += int(text[i]) * 10 ** (percent_index - i - 1)
        except ValueError:
            break
    return percent_as_int / 100