base_url = "https://play.pokemonshowdown.com/"
websocket_uri = "ws://sim.smogon.com:8000/showdown/websocket"
action_url = "https://play.pokemonshowdown.com/~~showdown/action.php"


# Config stuff.
bot_challenger = {"username": "insert_username", "password": None, "log_path": "C:/Path/To/textfile.txt"}
bot_accepter = {"username": "insert_username", "password": None, "log_path": "C:/Path/To/textfile.txt"}

sleep_between_turns = 8    # How many seconds the bot will wait for between choosing moves.
chrome_browser_exe_path = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"    # Your path to chrome.exe. Set to False/None if you don't want to open browser.