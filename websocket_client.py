import websockets
import asyncio
import requests
import json
import re
import time
import random
import os
import webbrowser

import constants as CONSTANSTS
import utils


class Websocket():
    
    @classmethod
    async def create(cls, username, password=None, log_path=None):
        self = Websocket()
        self.username = username
        self.password = password
        self.log_path = log_path

        self.challstr = ""
        self.battle_id = ""
        self.player = ""
        self.rqid = 0
        self.websocket = await websockets.connect(CONSTANSTS.websocket_uri)

        self.random_messages = ["Idiot", "Nice move", "Ez", "I got this"]

        await self.connect()
        await self.login()

        return self
    
    async def connect(self):
        response = await self.recieve_message()

        await self.send_message("|/cmd rooms")
        await self.send_message("|/autojoin ")

        response = await self.recieve_message()
        self.challstr = self.get_challstr(response)

        await self.recieve_message()
    
    async def send_message(self, message):
        await self.websocket.send(message)
    
    def log_message(self, message):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(message)
    
    async def recieve_message(self):
        message = await self.websocket.recv()

        if self.log_path is not None:
            self.log_message(message)

        return message
    
    async def login(self):
        data = {
            "act": "getassertion",
            "userid": self.username,
            "challstr": self.challstr
        } if self.password is None else {
            "act": "login",
            "name": self.username,
            "pass": self.password,
            "challstr": self.challstr
        }

        response = requests.post(CONSTANSTS.action_url, data=data)

        if response.status_code == 200:
            if self.password is None:
                assertion = response.text
            else:
                assertion = json.loads(response.text[1:])["assertion"]

        change_name_command = f"|/trn {self.username},0,{assertion}"
        await self.send_message(change_name_command)
    
    def must_switch(self, message: str) -> bool:
        return 'forceSwitch":[true]' in message
    
    def get_battle_link(self) -> str:
        return "/".join([CONSTANSTS.base_url, self.battle_id])

    async def battle(self):
        while True:
            message = await self.recieve_message()

            # Toxic bot ftw lmao.
            if f"|faint|{utils.opposite_player(self.player)}" in message:
                await self.chat("Ez KO!")

            if self.must_switch(message):
                # Change poke
                pokemon_info = utils.get_json_from_string(message)
                available_pokemon = [index + 2 for index, pokemon in enumerate(pokemon_info["side"]["pokemon"][1:]) if "fnt" not in pokemon["condition"]]

                await self.switch_pokemon(random.choice(available_pokemon))

                await asyncio.sleep(CONSTANSTS.sleep_between_turns)
            elif '|request|{"active":' in message:
                move_message = utils.get_json_from_string(message)
                self.rqid = move_message["rqid"]

                moves = move_message["active"][0]["moves"]
                if any("disabled" not in move.keys() for move in moves):
                    await self.choose_move(1)
                else:
                    available_moves = [index + 1 for index, move in enumerate(moves) if not move["disabled"]]
                    await self.choose_move(random.choice(available_moves))
                
                await asyncio.sleep(CONSTANSTS.sleep_between_turns)
            elif "|win|" in message:
                print(f"Game over! We {'Won' if self.username in message else 'Lost'}!")
                break
    
    async def challenge_player(self, name, battle_format="gen8randombattle"):
        self.player = "p1"
        challenge_command = f"|/challenge {name}, {battle_format}"

        print("Challenging:", name)
        await self.send_message(challenge_command)
        self.battle_id = utils.get_battle_id(await self.check_for_regex(r"battle-.*?-\d+"))
        
        if CONSTANSTS.chrome_browser_exe_path:
            webbrowser.get(CONSTANSTS.chrome_browser_exe_path).open(self.get_battle_link())

        await self.battle()
    
    async def accept_challenge(self):
        self.player = "p2"
        print("Waiting for challenger!")

        message = await self.check_for_keyword('"challengesFrom":{"')
        challenger = list(utils.get_json_from_string(message)["challengesFrom"].keys())[0]
        
        await self.send_message(message=f"|/accept {challenger}")
        self.battle_id = utils.get_battle_id(await self.check_for_regex(r"battle-.*?-\d+"))

        await self.battle()
    
    # Don't know if this works, have not tested it.
    async def forfeit_battle(self):
        await self.send_message(f"{self.battle_id}|/forfeit")
    
    async def choose_move(self, index):
        if index < 1 or index > 4:
            raise Exception(f"Cannot choose move with index greater than 4 or lower than 1 (got {index})")

        move_command = f"{self.battle_id}|/choose move {index}|{self.rqid}"
        await self.send_message(message=move_command)
    
    async def switch_pokemon(self, index):
        if index < 1 or index > 6:
            raise Exception(f"Cannot choose pokemon with index lower than 1 og greater than 6 (got {index})")

        switch_command = f"{self.battle_id}|/choose switch {index}|{self.rqid + 2}"
        await self.send_message(message=switch_command)
        await self.recieve_message()


    def get_challstr(self, string: str) -> str:
        res = re.findall('(?<=challstr\|).*(?="?)', string)

        if res:
            return res[0]
        else:
            raise Exception(f"Could not find challstr in {string}")
    
    async def check_for_keyword(self, keyword):
        message = await self.recieve_message()

        while keyword not in message:
            message = await self.recieve_message()
        
        return message
    
    async def check_for_regex(self, regex):
        message = await self.recieve_message()
        results = re.findall(regex, message)

        while not results:
            results = re.findall(regex, await self.recieve_message())
        
        return results[0]
    
    async def chat(self, message):
        command = "|".join([self.battle_id, message])
        await self.send_message(command)
    
    async def get_room(self):
        return self.check_for_keyword("queryresponse|roomlist")
    
    async def get_battles(self, battle_format, start, end=float("inf")):
        command = f"|/cmd roomlist {battle_format},none,"
        await self.send_message(command)

        battles = utils.get_json_from_string(await self.get_room())["rooms"]
        battles = {key: value for key, value in battles.items() if "minElo" in value.keys() and isinstance(value["minElo"], int) and value["minElo"] > start and value["minElo"] < end}

        for key, value in sorted(battles.items(), key=lambda x: x[1]["minElo"], reverse=True):
            print(f"{CONSTANSTS.base_url}{key} (rated {value['minElo']})")