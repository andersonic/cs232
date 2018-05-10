from selenium import common
import random
import interface as i
import time

"""Plays randbats randomly, with a set probability to switch. Does not store game state,
as the game state does not affect its actions."""


def start():
    i.open_window("https://play.pokemonshowdown.com")
    i.log_in("cs232-test-2", "cs232") #only test 1 or test 2 not 3 (bc random)

def random_switch():
    options = i.get_switch_options()
    selection = options[random.randint(0, len(options) - 1)]
    i.act(selection, True)

def random_move():
    options = i.get_move_options()
    selection = options[random.randint(0, len(options) - 1)]
    i.act(selection)

def calc_switch_and_move():
    try:
        print("We are in calc_switch_and_move")
        options = i.get_move_options()
        print("options parsed. now updating game state")
        
        # checking to see if we initalized our team before we update
        if i.own_mon_out == None:
             i.get_own_team()
             print("Team initalized.")
        i.update()
        print("Team updated.")
        opponentMoves = i.opponent_mon_out.moves
        #i.update_own_mon()
        
        sortedRunnerUps = insertionSort_pokemon(i.own_team)
        print("Team sorted.")
        
        current_mon = i.own_mon_out
        move = calc_max_damage(options)[0] #get our pokemon's best move
        
        print("WE ARE OUTSIDE THE LOOP")
        if calc_danger_of_knockout(opponentMoves,current_mon):
            #yes, danger of knockout
            print("WE ARE INSIDE THE LOOP, IF")
            if current_mon.health_percent == 1:
                # if we are at full health and are the best pokemon, switch to next best
                if current_mon == sortedRunnerUps[0]:
                    calc_switch(sortedRunnerUps[1])
                    print("pokemon at full health--> next best pkmn selected")
                else:
                    # else, switch to the best damage dealer
                    calc_switch(sortedRunnerUps[0])
                    print("pokemon at full health--> next best pkmn selected")
            else:
                heal = has_heal(options)
                if heal != False:
                #yes, has heal. heal or you are in danger of dying!!!!
                    print("pokemon in danger of knockout--> heal")
                    i.act(heal)
                else:
                    print("pokemon in danger of knockout--> no healing move--> attack")
                    i.act(move) #act based on best move
        else:
            #NO, we are not in danger of knockout. does our pokemon do the most damage?
            print("WE ARE INSIDE THE LOOP, ELSE")
            if current_mon == sortedRunnerUps[0]:
                #yes, our best pokemon is out in the field
                print("pokemon is the best on the field--> attack")
                #i.update_own_mon
                #i.update_opponent
                i.act(move)
            else: 
                #no, our best pokemon is not on the field
                best_mon = sortedRunnerUps[0]
                if (calc_danger_of_knockout(opponentMoves, best_mon)):
                    #yes, danger of knockout
                    if current_mon == sortedRunnerUps[1]:
                        #yes, our pokemon is the next best pokemon
                        print("pokemon is not the best on the field-->best pokemon in danger of knockout"
                        + "-->attack with current pokemon")
                        i.act(move)
                        
                    else:
                        next_best_mon = sortedRunnerUps[1]
                        if (calc_danger_of_knockout(opponentMoves,next_best_mon)):
                            #yes, next best pokemon is in danger of knockout
                            print("pokemon is not the best on the field-->best pokemon in danger of knockout"
                                    + "-->next best pokemon in danger of knockout-->attack with current pokemon")
                            i.act(move)
                        else:
                            #no danger for next best pokemon
                            print("pokemon is the best on the field-->best pokemon in danger of knockout"
                            +"-->next best pokemon not in danger of knockout-->switch to next best pokemon")
                            calc_switch(next_best_mon)
                else:
                    #no danger for best pokemon
                    print("pokemon is not best on battle field--> best pokemon not in danger of knockout"
                    + "-->switch to best pokemon")
                    calc_switch(best_mon)
    except AttributeError:
        pass
    else:
        print("random move: we didn't get anywhere in the tree")
        random_move()

def calc_max_damage(options):
    
    maxMove = options[0];
    maxDamage = 0;
    print ("now in: CALC_MAX_DAMAGE")
    print options
    #loops through all of the attack moves, and picks the one that
    # does the most damage
    for move in options:
        moveDamage = i.opponent_mon_out.damage_calc(move,i.own_mon_out)
        if moveDamage > maxDamage:
            maxDamage = moveDamage
            print maxDamage
            maxMove = move
    print maxMove, maxDamage
    return maxMove, maxDamage

def calc_switch(mon):
    #switches according to the pokemon specified by the tree or otherwise
    #will be either the best, next best, or next next best depending on
    #what pokemon is expected to die or not
    
    options = i.get_switch_options()
    selection = options.index(mon)
    print("IN CALC_SWITCH: pokemon to be acted upon is " + selection)
    i.act(selection, True)
    

# Function to do insertion sort. sorts pokemon by their best move/damage
def insertionSort_pokemon(team):
    print("ENTERED INSERTIONSORT")
    print team
    pokemon_and_damages = []
    for mon in team:
        options = mon.moves
        move, damage = calc_max_damage(options)
        print move,damage 
        #add the pokemon and its best move to an index of the list
        pokemon_and_damages.append([mon,damage])
    
    print pokemon_and_damages
    
    # Traverse through 1 to len(team)
    for i in range(1, len(pokemon_and_damages)):
        
        key = pokemon_and_damages[i]
 
        # Move elements of arr[0..i-1], that are
        # greater than key, to one position ahead
        # of their current position
        j = i-1
        while j >=0 and key < pokemon_and_damages[j] :
                pokemon_and_damages[j+1] = pokemon_and_damages[j]
                j -= 1
        pokemon_and_damages[j+1] = key
    
    #remove damage from every pokemon in sorted list and return results
    # of just ordered pokemon
    result = [pokemon_and_damages[0] for mon in pokemon_and_damages]
    return result
    
def calc_danger_of_knockout(options,mon):
    #calculates damage opponent can deal to current_mon_out
    #if at any time opponent damage exceedes health, we are in danger
    for move in options:
        moveDamage = i.mon.damage_calc(move,i.opponent_mon_out)
        if moveDamage > i.mon.present_health:
            return True
    return False 

    
def has_heal(options):
    #checks to see if the pokemon has a healing move by looping through
    # and checking if there is a move with 0 power
    
    for move in options:
        if move.power == 0:
            return False
    return False
    
def tree_battle():
    switch_allowed = True
    move_allowed = True
    print("now in: TREE_BATTLE")
    try:
        i.driver.find_element_by_class_name("switchmenu")
    except common.exceptions.NoSuchElementException:
        switch_allowed = False

    try:
        i.driver.find_element_by_class_name("movemenu")
    except common.exceptions.NoSuchElementException:
        move_allowed = False
    # if switches and moves are allowed, use decision tree. otherwise, random
    # move so program doesn't crash
    if switch_allowed and move_allowed:
        try:
            print("in tree_battle: going to calc_switch_and_move")
            calc_switch_and_move()
        except ValueError:
            random_move()
        else:
            print("Decision tree did not work. Pokemon used a random move")
            random_move()
    elif switch_allowed:
        print("in tree_battle: only switches allowed. calculating switch")
        sortedRunnerUps = insertionSort_pokemon(i.own_team)
        options = i.get_switch_options()
        print options
        ammendedOptions = [op.encode("ascii") for op in options]
        print ammendedOptions
        k=0
        while True:
            print ("inside of while loop")
            k=k+1
            pokemon = sortedRunnerUps[i].name
            print pokemon
            if pokemon in ammendedOptions:
                index = ammendedOptions.index(pokemon)
                print index
                print options[index]
                calc_switch(options[index])
                break
            
            
    elif move_allowed:
        #find our pokemon's best damage move and use it
        print("in random_action: only moves allowed. calculating move")
        options = i.get_move_options()
        bestMove, bestDamage = calc_max_damage(options)
        i.act(bestMove)
    else:
        print("Can't do anything")


def feist():
    
    battle_over = False
    print("WE ARE IN FEIST")
    while not battle_over:
        try:
            try:
                i.driver.find_element_by_class_name("movemenu")
                print("in feist: call tree_battle")
                tree_battle()
            except common.exceptions.NoSuchElementException:
                try:
                    i.driver.find_element_by_class_name("switchmenu")
                    tree_battle()
                except:
                    pass

            logs = i.driver.find_elements_by_class_name("battle-history")
            for log in logs:
                log_text = log.text
                if "won the battle!" in log_text:
                    battle_over = True
        except common.exceptions.ElementNotVisibleException:
            time.sleep(2)


def feist_random_enemy():
    i.find_randbat()
    print("random battle acquired. starting feist")
    feist()


def feist_k_enemies(k=1):
    for count in range(0,k):
        feist_random_enemy()
        i.driver.find_element_by_name("closeRoom").click()
        time.sleep(2)