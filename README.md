# Websocket Test
Simple Pokémon Showdown bot written in Python using websockets. The bot can play random genbattles given an opponents name. Currently the bot just chooses random moves until it loses/wins. Might add sensible decision making in the future.

## How to use
1 Install needed libraries (requests and websockets, the rest is probably included with Python).  
2 Set up the config file (See next segment)  
3 Run main.py. If run with no arguments, 2 bots will battle each other which can be viewed via a link. If run with an argument, the bot will try to challenge that player to a battle.  

## Set up config
To set the bot names, change the username value in the dictionaries in constants.py. If logging is desired, a path to a text file can be specified in the same dictionary. This will log every message that is sent from the websocket server to a textfile. Note that the program currently empties the log files before each battle. 
![alt text](https://i.imgur.com/gbkbJ1U.png)
