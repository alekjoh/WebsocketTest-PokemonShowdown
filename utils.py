import json
import re


def get_json_from_string(string: str) -> dict:
    if not isinstance(string, str):
        raise Exception("Wot ze fook are you doing? Needs to be string!")

    if any(char not in string for char in ["{", "}"]):
        raise Exception("Found no json object in:", string)

    start, end = string.index("{"), string.rindex("}")

    return json.loads(string[start:end+1])

def get_battle_id(string: str) -> str:
    battle_id = re.findall("battle-.*-\d+", string)

    if battle_id:
        return battle_id[0]
    else:
        raise Exception("There is no battle id in", string)

def opposite_player(player):
    return "p2" if player == "p1" else "p1"