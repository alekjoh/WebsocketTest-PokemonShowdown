import asyncio
from threading import Thread
from sys import argv

from websocket_client import Websocket
from constants import bot_challenger, bot_accepter


async def accept_challenge():
    if bot_accepter["log_path"]:
        with open(bot_accepter["log_path"], "w") as f:
            f.write("")
            
    websocket = await Websocket.create(username=bot_accepter["username"], password=bot_accepter["password"], log_path=bot_accepter["log_path"])
    await websocket.accept_challenge()

async def challenge_player(name):
    if bot_challenger["log_path"]:
        with open(bot_challenger["log_path"], "w") as f:
            f.write("")
    
    websocket = await Websocket.create(username=bot_challenger["username"], password=bot_challenger["password"], log_path=bot_challenger["log_path"])
    await asyncio.sleep(1)
    await websocket.challenge_player(name=name)

async def bot_vs_bot():
    if bot_challenger["log_path"]:
        with open(bot_challenger["log_path"], "w") as f:
            f.write("")
    
    if bot_accepter["log_path"]:
        with open(bot_accepter["log_path"], "w") as f:
            f.write("")

    await asyncio.gather(
        accept_challenge(),
        challenge_player(bot_accepter["username"])
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    try:
        if len(argv) == 1:
            loop.run_until_complete(bot_vs_bot())
        else:
            loop.run_until_complete(challenge_player(argv[1]))
        
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        loop.close()
