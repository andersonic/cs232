# CS232 Final Project

### data.txt
Holds a dictionary in JSON format with Pokémon names as keys and a list of the Pokémon's possible moves as the value.

### expectimax.py
Contains methods to determine the best action using a modified expectimax; makes use of state.py.

###interface.py
Contains all methods necessary to interface with the Pokémon Showdown server.

### interface_legacy.py
Version of interface.py that is compatible with tree_battle.py.

### main.py
Once used to start battles. No longer in use.

### random_battle.py
Contains the methods necessary for (quasi)random battling.

### pokemon_data_text.txt
Holds the raw data that was used to make data.txt; has superfluous data not in data.txt.

### state.py
Module containing the class State, which is comprised of both players' teams (current health, etc. included), the Pokémon currently on the battlefield, whether the bot can switch Pokémon and whether the bot's current Pokémon can use a move.

### tree_battle.py