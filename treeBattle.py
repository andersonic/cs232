from selenium import common
import random
import interface as i
import time

"""Plays randbats randomly, with a set probability to switch. Does not store game state,
as the game state does not affect its actions. This is version 2 of the original tree_battle"""


def start():
    i.open_window("https://play.pokemonshowdown.com")
    i.log_in("cs232-test-2", "cs232") #only test 1 or test 2 not 3 (bc random)

#### RANDOM MOVES ####
def random_switch():
    options = i.get_switch_options()
    selection = options[random.randint(0, len(options) - 1)]
    i.act(selection, True)

def random_move():
    options = i.get_move_options()
    selection = options[random.randint(0, len(options) - 1)]
    i.act(selection)
    
#### HELPERS OF THE DECISION TREE: CALCULATORS AND IMPLEMENTORS ####
def calc_max_damage(moves):
    
    maxMove = moves[0];
    maxDamage = 0;
    print ("now in: CALC_MAX_DAMAGE")
    
    #loops through all of the attack moves, and picks the one that
    # does the most damage
    for move in moves:
        moveDamage = i.opponent_mon_out.damage_calc(move,i.own_mon_out)
        if moveDamage > maxDamage:
            maxDamage = moveDamage
            maxMove = move
            
    #returns Move object, and int maxDamage
    return maxMove, maxDamage

def calc_switch(mon):
    #switches according to the pokemon specified by the tree or otherwise
    #will be either the best, next best, or next next best depending on
    #what pokemon is expected to die or not
    
    if mon is not None:
        try:
            #switch to pokemon specified by user
            options = i.get_switch_options()
            #account for u'Name' format when we call get_switch_options()
            ammendedOptions = [op.encode("ascii") for op in options]
            
            print "ammended options and options[index]"
            print ammendedOptions.index(mon)
            print options[index]
            
            index = ammendedOptions.index(mon)
            selection = options[index]
            print("IN CALC_SWITCH: pokemon to be acted upon is " + selection)
            i.act(selection, True)   
            
        except AttributeError:
            print("Unable to switch to designated mon. Random_switch called")
            random_switch()
        else:
            print("Unable to switch to designated mon. Random_switch called")
            random_switch()
    else:
        try:
            print("Sorting pokemon to select switch option")
            #sort our team's pokemon by strongest move
            sortedRunnerUps = insertionSort_pokemon(i.own_team)
            
            #get available switch options
            options = i.get_switch_options()
            #account for u'Name' format when we call get_switch_options()
            ammendedOptions = [op.encode("ascii") for op in options] 

            # loop through sorted pokemon until we find one that is not on the field
            k=0
            while True:
                print ("inside of while loop")
                k=k+1
                pokemon = sortedRunnerUps[i].name
                
                print "ammended options of pokemonand options[index]"
                print ammendedOptions.index(pokemon)
                print options[index]
                
                if pokemon in ammendedOptions:
                    index = ammendedOptions.index(pokemon)
                    calc_switch(options[index])
                    break
        except AttributeError:
            pass
        else:
            print("Unable to switch to sorted pokemon. Random_switch called")
            random_switch()

# Function to do insertion sort. sorts pokemon by their best move/damage
def insertionSort_pokemon():
    print("ENTERED INSERTIONSORT")
    pokemon_and_damages = []
    team = i.own_team
    for mon in team:
        options = mon.moves
        move, damage = calc_max_damage(options)
        print move,damage 
        #add the pokemon and its best move to an index of the list
        pokemon_and_damages.append([mon,damage])
    print "our team is:"
    print [mon.name for mon in team]
    print "^^^"
    print pokemon_and_damages
    
    # Traverse through 1 to len(team)
    for i in range(1, len(pokemon_and_damages)-1):
        
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
    #returns Pokemon object list
    return  [pokemon_and_damages[0] for mon in pokemon_and_damages]
    
def calc_danger_of_knockout(opponentMoves):
    print("IN: CALC_DANGER_OF_KNOCKOUT")
    #calculates damage opponent can deal to current_mon_out
    #if at any time opponent damage exceedes health, we are in danger
    for move in opponentMoves:
        moveDamage = i.current_mon_out.damage_calc(move,i.opponent_mon_out)
        if moveDamage > i.current_mon_out.present_health:
            return True
    return False 

def has_heal(moves):
    print("IN: HAS_HEAL")
    #checks to see if the pokemon has a healing move by looping through
    # and checking if there is a move with 0 power
    
    for move in moves:
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
        calc_switch(None)

    elif move_allowed:
        try:
            #find our pokemon's best damage move and use it
            print("in tree_battle: only moves allowed. calculating move")
            options = i.get_move_options()
            #account for u'Name' format when we call get_switch_options()
            ammendedOptions = [op.encode("ascii") for op in options] 
            
            bestMove, bestDamage = calc_max_damage(i.own_moves)
            moveIndex = ammendedOptions.index(bestMove)
            i.act(options[moveIndex])
        except ValueError:
            random_move()
        else:
            print("Decision tree did not work. Pokemon used a random move")
    else:
        print("Can't do anything")

def available_pokemon(sortedTeam,position): 
    #looks for an available pokemon in the position specificed
    #for example: if we wanted the best available pokemon, we would 
    #do available_pokemon(sortedTeam,1). if we wanted the second best
    # , then position = 2
    
    options = i.get_switch_options()
    #account for u'Name' format when we call get_switch_options()
    ammendedOptions = [op.encode("ascii") for op in options] 
    
    available = 1
    # loop through sorted pokemon until we find one that is not on the field
    k=0
    while True:
        print ("inside of while loop")
        k=k+1
        pokemon = sortedTeam[i].name
        if pokemon in ammendedOptions:
            index = ammendedOptions.index(pokemon)
            if available == position:
                return index, pokemon
            available = available + 1
    return None, None

### THE HEART OF TREE_BATTLE: A DECISION TREE ###
def calc_switch_and_move():
    print("We are in calc_switch_and_move")
    treeStatement = "" #keep track of where we go in tree
    try:
        options = i.get_move_options()
        
        # initialize team if we have not
        if i.own_mon_out == None:
             i.get_own_team()
             print("Team initalized.")
        
        i.update()
        print ("update completed.")
        
        ourPokemon = i.own_mon_out
        opponentPokemon = i.opponent_mon_out
        print ("fetched our mon and opponent mon")
        ourMoves = ourPokemon.moves
        opponentMoves = opponentPokemon.moves
        print ("fetched our mon and opponent mon moves")
        
        move, damage = calc_max_damage(ourMoves)
        print ("max move calculated")
        
        if calc_danger_of_knockout(opponentMoves):
            treestatement = treeStatement + "Current pokemon in danger of knockout--> "
            
            if ourPokemon.health_percent ==1:
                treeStatement = treeStatement + "pokemon at full health-->Switch"
                print treeStatement
                calc_switch(None)
            else:
                treeStatement = treeStatement + "pokemon not at full health--> "
            
                heal = has_heal(options)
                if heal == False:
                    treeStatement = treeStatement + "no healing move-->Attack"
                    print treeStatement
                    i.act(move)
                else:
                    treeStatement = treeStatement + "healing move available-->Heal"
                    print treeStatement
                    i.act(heal)
        else:
            sortedPokemon = insertionSort_pokemon()
            bestIndex, bestPokemon = available_pokemon(sortedPokemon,1)
            nextBestIndex, nextBestPokemon = available_pokemon(sortedPokemon,2)
            
            if (ourPokemon == bestPokemon):
                treeStatement = treeStatement \
                + "our pokemon is the best out of available pokemon-->Attack"
                print treeStatement
                i.act(move)
            else:
                treeStatement = treeStatement \
                + "pokemon is not the best out of available pokemon-->" 
                
                if(calc_danger_of_knockout(opponentMoves,nextBestPokemon)):
                    treeStatement = treeStatement \
                    + "best pokemon in danger of knockout-->"
                    
                    if (ourPokemon == nextBestPokemon):
                        treeStatement = treeStatement \
                        + "our pokemon is the next best-->Attack"
                        print treeStatement
                        i.act(move)
                    else:
                        treeStatement = treeStatement \
                        + "our pokemone is not the next best-->"
            
                        if (calc_danger_of_knockout(opponentMoves,nextBestPokemon)):
                            treeStatement = treeStatement \
                            + "next best pokemon in danger of knockout-->Attack"
                            print treeStatement
                            i.act(move)
                        else:
                            calc_switch(nextBestPokemon)
                else:
                    treeStatement = treeStatement \
                    + "best pokemon in not danger of knockout-->Switch"
                    print treeStatement
                    calc_switch(nextBestPokemon)
        
        
    except AttributeError:
        pass
    else:
        print("random move: we didn't get anywhere in the tree")
        random_move()
#### FEIST, USED FOR STARTING A GAME AND INITIATING A MOVE ###
def feist():
    
    battle_over = False
    print("!!!! FEST !!!!")
    while not battle_over:
        try:
            try:
                i.driver.find_element_by_class_name("movemenu")
                print("in feist: call tree_battle")
                tree_battle()
            except common.exceptions.NoSuchElementException:
                try:
                    i.driver.find_element_by_class_name("switchmenu")
                    print("in feist: call tree_battle")
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