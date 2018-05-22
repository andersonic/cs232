# -*- coding: cp1252 -*-
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import math
import time
import os
import json

USERNAME = "cs232-test-3"
PASSWORD = "cs232"

driver = None
#all_pokemon_data = demjson.decode(open('pokemon_data.txt', 'r').read())
with open('pokemon_data.txt') as r:
    all_pokemon_data = json.load(r)
own_team = []
opponent_team = []

own_mon_out = None
opponent_mon_out = None

# game_state = {'rocks':False, 'spikes': 0, 'tspikes': 0, 'weather':'none', 'trickroom':False, 'terrain':'none'}


def open_window(url):
    """Opens window."""
    my_dir = os.path.dirname(__file__)
    chrome_path = os.path.join(my_dir, 'chromedriver')
    new_driver = webdriver.Chrome(chrome_path)
    new_driver.get(url)
    global driver
    driver = new_driver
    driver.implicitly_wait(1)


def log_out():
    """Log out of Pokémon Showdown. Refresh to ensure logout goes through."""
    driver.find_element_by_name("openOptions").click()
    try:
        driver.find_element_by_name("logout").click()
        driver.find_element_by_tag_name("strong").click()
    except common.exceptions.NoSuchElementException:
        pass
    driver.refresh()


def log_in(username, password):
    """Log in to Pokémon Showdown."""
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
    """Open window and log in using global USERNAME and PASSWORD"""
    open_window("https://play.pokemonshowdown.com")
    time.sleep(2)
    log_in(USERNAME, PASSWORD)


def find_randbat():
    """Find a random battle. Return when battle has started."""
    driver.find_element_by_name("search").click()

    started = False

    while not started:
        try:
            move_buttons = driver.find_elements_by_name("chooseMove")
            switch_buttons = driver.find_elements_by_name("chooseSwitch")
            disabled = driver.find_element_by_name("chooseDisabled")
            started = True
        except common.exceptions.NoSuchElementException:
            started = False
            time.sleep(2)


def act(action, switch=False):
    """Take an action (a move name or a Pokémon name) as a parameter and whether the action is a switch."""
    mega_evolve()

    if switch:
        pokemon_buttons = driver.find_elements_by_name("chooseSwitch")
        for pokemon in pokemon_buttons:
            if pokemon.text in action:
                pokemon.click()
                return True
    else:
        move_buttons = driver.find_elements_by_name("chooseMove")
        for move in move_buttons:
            if move.text.split('\n')[0] == action:
                move.click()
                return True
    return False


def mega_evolve():
    try:
        evo_button = driver.find_element_by_name("megaevo")
        evo_button.click()
        return True
    except common.exceptions.NoSuchElementException:
        return False


def get_own_team():
    """Precondition: first turn. Returns all Pok�mon, including stats, moves and items."""

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
    text = element.text.split("\n")
    types = get_types_tooltip(element)
    stats = read_stats(text)
    moves = get_own_mon_moves(text)

    # Get types
    images = element.find_elements_by_tag_name("img")
    types = []
    for image in images:
        if image.get_attribute("alt") is not "M" and image.get_attribute("alt") is not "F":
            types.append(image.get_attribute("alt"))
    if len(types) == 1:
        types.append('none')

    # Get health
    name = " ".join(text[0].split(" ")[:len(text[0].split(" "))-1])

    if "(" in name:
        name = name.split("(")[1].split(")")[0]

    try:
        level = int(text[0].split(" ")[len(text[0].split(" ")) - 1][1:])
    except ValueError:
        level = 100
    current_health = int(text[1].split(" ")[2].split("/")[0][1:])
    total_health_text = text[1].split(" ")[2].split("/")[1]
    total_health = int(total_health_text[0:len(total_health_text) - 1])

    # Get ability and item
    temp = text[2].split(" / ")
    try:
        ability = " ".join(temp[0].split(" ")[1:])
        item = " ".join(temp[1].split(" ")[1:])
    except IndexError:
        ability = " ".join(temp[0].split(" ")[1:])
    return Pokemon(name, level, types, moves, None, ability, total_health, stats)


def get_types_tooltip(element):
    images = element.find_elements_by_tag_name("img")
    types = []
    for image in images:
        if image.get_attribute("alt") is not "M" and image.get_attribute("alt") is not "F":
            types.append(image.get_attribute("alt"))
    return types


def read_stats(text):
    stats = text[3].split("/")
    temp = []
    for i in range(0, 5):
        pieces = stats[i].split(" ")
        for piece in pieces:
            if piece != "":
                temp.append(int(piece))
                break
    return temp


def get_own_mon_moves(text):
    # Get moves
    moves = []
    try:
        for i in range(4, 8):
            move = text[i][2:]
            if "(" in move:
                move = move[:move.index("(") - 1]
            moves.append(move)
    except IndexError:
        pass

    for move in moves:
        query_data(move)
    time.sleep(2)
    data = retrieve_data()
    return [parse_move_text(i, data) for i in moves]


def query_data(data):
    textbox = driver.find_element_by_class_name("battle-log-add").find_elements_by_class_name("textbox")[1]
    textbox.send_keys("/data " + data)
    textbox.send_keys(Keys.ENTER)


def retrieve_data():
    return driver.find_elements_by_class_name("utilichart")


def parse_opposing_mon():
    # Get element with data
    enemy_mon = driver.find_element_by_class_name("foehint").find_elements_by_tag_name("div")[2]
    hover = ActionChains(driver).move_to_element(enemy_mon)
    hover.perform()
    tooltip = driver.find_element_by_id("tooltipwrapper")

    help_text = tooltip.text.split("\n")

    name_temp = help_text[0].split(" ")
    name = " ".join(name_temp[:len(name_temp) - 1])

    if "(" in name:
        name = name.split("(")[1].split(")")[0]

    try:
        level = int(name_temp[len(name_temp) - 1][1:])
    except ValueError:
        level = 100


    base_stats = get_base_stats(name)

    stats = calc_stats(base_stats, level)

    ability_text = help_text[2].split(" ")
    ability = None
    if ability_text[0] == "Ability:":
        ability = " ".join(ability_text[1:])
    else:
        # Try to figure out which ability it has
        abilities = " ".join(ability_text).split(": ")[1].split(", ")
        if "Huge Power" in abilities:
            ability = "Huge Power"
        elif "Pure Power" in abilities:
            ability = "Pure Power"
        elif "Levitate" in abilities:
            ability = "Levitate"
        elif "Pixilate" in abilities:
            ability = "Pixilate"
        elif "Aerilate" in abilities:
            ability = "Aerilate"

    images = tooltip.find_elements_by_tag_name("img")
    types = []
    for image in images:
        if image.get_attribute("alt") is not "M" and image.get_attribute("alt") is not "F":
            types.append(image.get_attribute("alt"))

    if len(types) == 0:
        #grr
        data = retrieve_data()
        for item in data:
            try:
                if item.find_element_by_class_name("pokemonnamecol").text == name:
                    for type in item.find_element_by_class_name("typecol").find_elements_by_tag_name("img"):
                        types.append(type.get_attribute("alt"))
            except common.exceptions.NoSuchElementException:
                pass
    if len(types) == 1:
        types.append('none')

    moves = handle_list_moves(get_possible_moves(name))

    new_mon = Pokemon(name, level, types, moves, None, ability, stats[0], stats[1:])
    if new_mon not in opponent_team:
        opponent_team.append(new_mon)
    return new_mon


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
    try:
        assert len(base_stats) != 0
    except AssertionError:
        time.sleep(2)
        base_stats = get_base_stats(mon)
    return base_stats


def calc_stats(base_stats, level):
    """Calculate a Pokémon's stats based on its base stats and level"""
    stats = []
    stats.append(math.floor((31 + 2 * base_stats[0] + 21) * level/100 + 10 + level))

    for i in range(1, 6):
        stats.append(math.floor((31 + 2 * base_stats[i] + 21) * level/100 + 5))

    return stats


def get_possible_moves(name):
    name = name.replace(" ", "").replace("-", "").lower()
    if name == "zygarde10%":
        name="zygarde10"
    return all_pokemon_data[name]['randomBattleMoves']


def handle_list_moves(moves):
    for move in moves:
        query_data(move)
    time.sleep(3)
    data = retrieve_data()
    parsed_moves = [parse_move_text(i, data) for i in moves]
    return parsed_moves


def parse_move_text(move, all_stuff=None, depth=0):
    if all_stuff is None:
        all_stuff = retrieve_data()
    move_data = None
    move_name = None
    for item in all_stuff:
        move_name = item.text.split('\n')[0]
        if move_name == move or move_name.replace(" ", "").replace("-", "").replace("\'", "").lower() == move:
            move_data = item
            break

    try:
        assert move_data is not None
        images = move_data.find_element_by_class_name("typecol").find_elements_by_tag_name("img")
        type = images[0].get_attribute("alt")
        category = images[1].get_attribute("alt")
        power = 0
        text = move_data.text.split("\n")

        user_boosts = [0 for i in range(0, 5)]
        target_boosts = [0 for i in range(0, 5)]
        user_effects = None
        target_effects = None

        if category == "Status":
            detail_text = text[5]
        else:
            try:
                detail_text = text[7]
            except IndexError:
                detail_text = ""
            try:
                power = int(text[2])
            except ValueError:
                pass

        if "Lowers the user's" in detail_text:
            boosts = parse_boosts(detail_text)
            for i in range(0, 5):
                user_boosts[i] -= boosts[i]
        elif "Raises the user's" in detail_text:
            boosts = parse_boosts(detail_text)
            for i in range(0, 5):
                user_boosts[i] += boosts[i]
        if detail_text == "Paralyzes the target.":
            target_effects = "PAR"
        elif detail_text == "Burns the target.":
            target_effects = "BRN"
        elif detail_text == "Puts the target to sleep.":
            target_effects = "SLP"
        elif detail_text == "Poisons the target.":
            target_effects = "PSN"
        elif detail_text == "Badly poisons the target.":
            target_effects = "TOX"

        if move_name == "Shell Smash":
            user_boosts = [2, -1, 2, -1, 2]
        return Move(type, power, category, name=move_name, user_boosts=user_boosts, target_effects=target_effects)
    except AssertionError:
        if depth > 3:
            query_data(move)
        time.sleep(2)
        return parse_move_text(move, retrieve_data(), depth + 1)


def parse_boosts(text):
    stat_names = ["Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    boosts = [0 for i in range(0,5)]
    for i in range(0,5):
        if stat_names[i] in text:
            name_index = text.index(stat_names[i])
            temp = text[name_index:]
            boost_amount = int(temp[text[name_index:].index("by") + 3])

            boosts[i] += boost_amount
    return boosts


class Pokemon:
    def __init__(self, name=None, level=None, type=None, moves=None, item=None, ability=None,
                 totalhealth=None, stats=None):
        self.name = name
        self.level = level
        self.type = type
        self.moves = moves
        self.item = item
        self.ability = ability
        self.stats = stats
        self.present_health = totalhealth
        self.total_health = totalhealth
        self.boosts = [0 for i in range(0,5)]
        self.status = None
        self.available_moves = moves
        self.floating = False

    def __eq__(self, other):
        """Note that this definition of equality breaks down when comparing Pokémon on opposite teams"""
        if self is None:
            return False
        elif other is None:
            return False
        else:
            return self.name == other.name

    def damage_calc(self, enemy_move, enemy_mon):
        """Legacy method. Use damage calc method from the Move class"""

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
        """Legacy method."""
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

    def calc_real_stats(self):
        """Calculate effective stats based on stats and boosts, using +x
        instead of multipliers for boosts."""
        real_stats = []
        for i in range(0, len(self.stats)):
            stat = self.stats[i] * Pokemon.calc_boost_multiplier(self.boosts[i])
            if i == 0 and "BRN" == self.status:
                stat *= 0.5
            elif i == 4 and "PAR" == self.status:
                stat *= 0.25
            real_stats.append(stat)
        if self.status is not None and self.ability == "Guts":
            real_stats[0] *= 2
        if self.ability == "Huge Power" or self.ability == "Pure Power":
            real_stats[0] *= 2
        return real_stats

    @staticmethod
    def calc_boost_multiplier(mod):
        """Given a modifier in the form of +x, calculate the multiplier"""
        temp = 2 + math.fabs(mod)
        if mod < 0:
            return 2/temp
        else:
            return temp/2

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
        try:
            if self.type[1] in type_chart[move_type]:
                multiplier *= type_chart[move_type][self.type[1]]
        except IndexError:
            pass

        if move_type == "Ground" and (self.ability == "Levitate" or self.floating):
            multiplier = 0

        if self.ability == "Wonder Guard" and multiplier < 1.9:
            multiplier = 0

        return multiplier

    def calc_effective_stats(self):
        """Legacy method. Calculate effective stats based on stats and boosts."""
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


class Move:
    def __init__(self, type, power, category, name=None, user_boosts=None, target_boosts=None,
                 user_effects=None, target_effects=None):
        self.type = type
        self.power = power
        self.category = category
        self.name = name
        self.target_effects = target_effects
        self.user_effects = user_effects
        if user_boosts is None:
            self.user_boosts = [0 for i in range(0,5)]
        else:
            self.user_boosts = user_boosts
        if target_boosts is None:
            self.target_boosts = [0 for i in range(0,5)]
        else:
            self.target_boosts = target_boosts

    def __eq__(self, other):
        return self.type == other.type and self.power == other.power and self.category == other.category
    
    def apply_move(self, user, target):
        target.present_health -= self.damage_calc(user, target)
        self.apply_boosts(user, target)
        self.apply_effects(user, target)

    def damage_calc(self, user, target):
        """Calculate the damager user does to target using this move."""
        target_stats = target.calc_real_stats()
        user_stats = user.calc_real_stats()

        power = self.calc_real_power(user, target)
        damage = 0

        if self.category == "Physical":
            damage = \
                (((2 * user.level / 5 + 2) * user_stats[0] * power / target_stats[1]) / 50 + 2) * 93 / 100
        elif self.category == 'Special':
            damage = \
                (((2*user.level/5 + 2) * user_stats[2]*power/target_stats[3])/50 + 2) * 93/100
        if self.type in user.type:
            damage *= 1.5
        if self.type == "Normal":
            if user.ability == "Pixilate":
                self.type = "Fairy"
                damage *= 1.2
            elif user.ability == "Aerilate":
                self.type = "Flying"
                self.power *= 1.2
        damage *= target.calculate_type_multiplier(self.type)
        return damage

    def calc_real_power(self, user, target):
        base_power = self.power
        if self.name == "Knock Off" and target.item is not None:
            return base_power * 2
        elif self.name == "Facade" and user.status is not None:
            return base_power * 2
        elif user.item is None and self.name == "Acrobatics":
            return base_power * 2
        return base_power

    def apply_boosts(self, user, target):
        for i in range(0, 5):
            user.boosts[i] += self.user_boosts[i]
            target.boosts[i] += self.target_boosts[i]
        if user.ability == "Contrary":
            for i in range(0, 5):
                user.boosts[i] -= 2 * self.user_boosts[i]
        if target.ability == "Contrary":
            for i in range(0, 5):
                target.boosts[i] -= 2 * self.target_boosts[i]

    def apply_effects(self, user, target):
        if self.name == "Explosion" or self.name == "Self-Destruct" \
                or self.name == "Lunar Dance" or self.name == "Healing Wish":
            user.present_health = 0
        elif self.name == "Knock Off" and target.ability != "Sticky Hold":
            target.item = None
        elif self.name == "Pain Split":
            pooled_health = target.present_health + user.present_health
            target.present_health = pooled_health / 2
            user.present_health = pooled_health / 2

        if self.target_effects is not None and target.status is None:
            target.status = self.target_effects
        if self.user_effects is not None and target.status is None:
            user.status = self.user_effects

    def __eq__(self, other):
        return self.type == other.type and self.power == other.power and self.category == other.category


def update(on_last_turn=False):
    """Pre-condition: battle state is up to date until turn_to_parse - 1.
    Post-condition: battle state is up to date. Except it probably misses loads of stuff"""

    first_line = 0
    logs = [log.text for log in driver.find_elements_by_class_name("battle-history")]
    turns = [log for log in logs if "Turn " in log]

    try:
        most_recent_turn = turns[len(turns) - 2]
    except IndexError:
        most_recent_turn = turns[len(turns) - 1]

    if on_last_turn:
        most_recent_turn = turns[len(turns)-1]

    for i in range(0, len(logs)):
        if logs[i] == most_recent_turn:
            first_line = i
    logs = logs[first_line:]

    my_fainted_mon = None
    your_fainted_mon = None

    for log in logs:
        if " fainted!" in log and " opposing " in log:
            # An opposing Pokémon has fainted
            temp = log.split(" ")
            name = " ".join(temp[2:len(temp) - 1])
            for mon in opponent_team:
                if name in mon.name:
                    your_fainted_mon = mon
                    break
            # Can't assert because you might send an unrevealed mon in to die right away
            if your_fainted_mon is None:
                your_fainted_mon = Pokemon(name=name, totalhealth=1)
                opponent_team.append(your_fainted_mon)
            your_fainted_mon.present_health = 0
        elif " fainted!" in log and on_last_turn:
            # One of my Pokémon has fainted
            temp = log.split(" ")
            name = " ".join(temp[:len(temp) - 1])
            for mon in own_team:
                if name in mon.name:
                    my_fainted_mon = mon
                    break
            assert my_fainted_mon is not None
            my_fainted_mon.present_health = 0

    if your_fainted_mon is not None and my_fainted_mon is not None:
        # We both fainted
        return
    elif your_fainted_mon is not None and my_fainted_mon is None:
        # You fainted, I didn't. Might still have sustained damage
        update_opponent()
        update_own_mon()
        return
    elif your_fainted_mon is None and my_fainted_mon is not None:
        # I fainted, you didn't
        update_opponent()
        return
    else:
        # Neither of us fainted
        update_own_mon()
        update_opponent()
        return


def update_own_mon():
    try:
        statbar = driver.find_element_by_class_name("rstatbar")
        firstline = " ".join(statbar.text.split("\n")[0].split(" "))
        mon = " ".join(firstline.split(" ")[:len(firstline.split(" ")) - 1])
        global own_mon_out

        if "mega" in [a.get_attribute("alt") for a in statbar.find_elements_by_tag_name("img")]:
            # It's a mega
            print("mega")

            current_mon = driver.find_element_by_name("chooseDisabled")
            hover = ActionChains(driver).move_to_element(current_mon)
            hover.perform()
            pokemon = driver.find_element_by_id("tooltipwrapper")
            mega_mon = parse_own_team(pokemon)
            own_team.remove(own_mon_out)
            own_team.append(mega_mon)
            own_mon_out = mega_mon

        try:
            if mon not in own_mon_out.name:
                for pokemon in own_team:
                    if mon in pokemon.name:
                        own_mon_out = pokemon
        except AttributeError:
            for pokemon in own_team:
                if mon in pokemon.name:
                    own_mon_out = pokemon
        assert own_mon_out is not None

        hptext = statbar.find_element_by_class_name("hptext").text
        health_percent = int(hptext[:len(hptext) - 1]) / 100
        own_mon_out.present_health = own_mon_out.total_health * health_percent
        update_status(own_mon_out, statbar)

        try:
            move_names = [move.text.split('\n')[0] for move in driver.find_elements_by_name("chooseMove")]
        except common.exceptions.StaleElementReferenceException:
            time.sleep(2)
            moves = driver.find_elements_by_name("chooseMove")
            move_names = []
            for move in moves:
                move_names.append(move.text.split("\0"))
        own_mon_out.available_moves = [move for move in own_mon_out.moves if move.name in move_names]

    except common.exceptions.NoSuchElementException:
        # Your Pokémon is not there due to self-switch/forced switch
        pass


def update_opponent():
    statbar = driver.find_element_by_class_name("lstatbar")
    firstline = " ".join(statbar.text.split("\n")[0].split(" "))
    mon = " ".join(firstline.split(" ")[:len(firstline.split(" ")) - 1])

    already_parsed = False
    opp_mon_out = None

    if "mega" in [a.get_attribute("alt") for a in statbar.find_elements_by_tag_name("img")]:
        # It's a mega
        print("It's a mega")
        mon = "-".join([mon, "Mega"])

    for pokemon in opponent_team:
        try:
            if mon == pokemon.name or mon in pokemon.name:
                already_parsed = True
                opp_mon_out = pokemon
        except AttributeError:
            pass
    return Move(type, power, category, name=move_name)


def update(on_last_turn=False):
    """Pre-condition: battle state is up to date until turn_to_parse - 1.
    Post-condition: battle state is up to date. Except it probably misses loads of stuff"""

    first_line = 0
    logs = [log.text for log in driver.find_elements_by_class_name("battle-history")]
    turns = [log for log in logs if "Turn " in log]

    try:
        most_recent_turn = turns[len(turns) - 2]
    except IndexError:
        most_recent_turn = turns[len(turns) - 1]

    if on_last_turn:
        most_recent_turn = turns[len(turns)-1]

    for i in range(0, len(logs)):
        if logs[i] == most_recent_turn:
            first_line = i
    logs = logs[first_line:]

    my_fainted_mon = None
    your_fainted_mon = None

    for log in logs:
        if " fainted!" in log and " opposing " in log:
            # An opposing Pok�mon has fainted
            name = log.split(" ")[2]
            for mon in opponent_team:
                if mon.name == name:
                    your_fainted_mon = mon
            # Can't assert because you might send an unrevealed mon in to die right away
            if your_fainted_mon is None:
                your_fainted_mon = Pokemon(name=name)
                opponent_team.append(your_fainted_mon)
        elif " fainted!" in log and on_last_turn:
            # One of my Pok�mon has fainted
            name = log.split(" ")[0]
            for mon in own_team:
                if mon.name == name:
                    my_fainted_mon = mon
            assert my_fainted_mon is not None

    if your_fainted_mon is not None and my_fainted_mon is not None:
        # We both fainted
        print("double faint")
        your_fainted_mon.present_health = 0
        my_fainted_mon.present_health = 0
        return
    elif your_fainted_mon is not None and my_fainted_mon is None:
        # You fainted, I didn't. Might still have sustained damage
        print("you fainted")
        update_opponent()
        update_own_mon()
        return
    elif your_fainted_mon is None and my_fainted_mon is not None:
        # I fainted, you didn't
        print("i fainted")
        update_opponent()
        return
    else:
        print("no faints")
        # Neither of us fainted
        update_own_mon()
        update_opponent()
        return


def update_own_mon():
    try:
        statbar = driver.find_element_by_class_name("rstatbar")
        firstline = " ".join(statbar.text.split("\n")[0].split(" "))
        mon = " ".join(firstline.split(" ")[:len(firstline.split(" ")) - 1])
        global own_mon_out

        if "mega" in [a.get_attribute("alt") for a in statbar.find_elements_by_tag_name("img")]:
            # It's a mega
            print("mega")

            current_mon = driver.find_element_by_name("chooseDisabled")
            hover = ActionChains(driver).move_to_element(current_mon)
            hover.perform()
            pokemon = driver.find_element_by_id("tooltipwrapper")
            mega_mon = parse_own_team(pokemon)
            own_team.remove(own_mon_out)
            own_team.append(mega_mon)
            own_mon_out = mega_mon

    global opponent_mon_out
    if "mega" in [a.get_attribute("alt") for a in statbar.find_elements_by_tag_name("img")] and not already_parsed:
        print("Parsing mega")
        opponent_team.remove(opponent_mon_out)
        mega_mon = parse_opposing_mon()
        opponent_mon_out = mega_mon
    elif not already_parsed:
        opponent_mon_out = parse_opposing_mon()
    elif opponent_mon_out is None or opponent_mon_out.name != mon:
        opponent_mon_out = opp_mon_out

    hptext = statbar.find_element_by_class_name("hptext").text
    health_percent = int(hptext[:len(hptext) - 1]) / 100
    opponent_mon_out.present_health = opponent_mon_out.total_health * health_percent
    update_status(opponent_mon_out, statbar)


def update_status(pokemon, statbar):
    pokemon.floating = False
    status = statbar.find_element_by_class_name("status")
    statuses = status.find_elements_by_tag_name("span")
    statuses = [i.text for i in statuses]
    status = None
    stat_boosts = [0 for i in range(0,6)]
    for s in statuses:
        try:
            text = s.split(" ")
            stat_name = text[1]
            stat_mod = float(text[0][:len(text[0]) - 1])
            stat_boosts[map_stat_to_position(stat_name)] = map_mod_to_boost(stat_mod)
        except ValueError:
            if s == "BRN" or s == "PAR" or s == "TOX" or s == "PSN" or s == "SLP" or s == "FRZ":
                status = s
        except IndexError:
            if s == "BRN" or s == "PAR" or s == "TOX" or s == "PSN" or s == "SLP" or s == "FRZ":
                status = s
            elif s == "Magnet Rise" or s == "Balloon":
                pokemon.floating = True
    pokemon.status = status
    pokemon.boosts = stat_boosts


def map_mod_to_boost(mod):
    for i in range(-6,7):
        if i < 0:
            if 2/(2 - i) - mod < 0.01:
                return i
        if i > 0:
            if (2 + i) / 2 - mod < 0.01:
                return i
    return False


def map_stat_to_position(name):
    if name == "Atk":
        return 0
    elif name == "Def":
        return 1
    elif name == "SpA":
        return 2
    elif name == "SpD":
        return 3
    elif name == "Spe":
        return 4
    return False


def extract_percent(text):
    """Given a string with exactly one percent, return the percent as a float."""
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


def get_move_options():
    """Return the names of the moves you are able to use"""
    moves = []
    move_buttons = driver.find_elements_by_name("chooseMove")
    for move in move_buttons:
        moves.append(move.text.split('\n')[0])
    return moves


def get_switch_options():
    """Return a list of the Pokémon you can switch in."""
    pokemon_list = []
    pokemon_buttons = driver.find_elements_by_name("chooseSwitch")
    for pokemon in pokemon_buttons:
        pokemon_list.append(pokemon.text)
    return pokemon_list

