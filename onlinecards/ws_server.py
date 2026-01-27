import websockets, asyncio, json

import database
from server import app

import handlers.utils as utils
from handlers.chatroom import handle_chatroom
from handlers.whist import handle_whist

from websockets.legacy.server import WebSocketServerProtocol

async def handler(websocket):
    async for eventJSON in websocket:
        print(eventJSON)
        event = json.loads(eventJSON)
        match event["type"]:
            case "create":
                await create(websocket, event)
            case "join":
                await join(websocket, event)

        gameID = int(event["gameID"])
        config = utils.get_config(gameID)
        game_handler = get_game_handler(config["game_type"])
        await game_handler(websocket, event)

def get_game_handler(game_type):
    async def error(*_):
        print(f"Error could not find handler for '{game_type}'")

    map = {
        "chatroom": handle_chatroom,
        "whist": handle_whist,
    }
    try:
        return map[game_type]
    except KeyError:
        return error

async def create(websocket, event):
    gameID = int(event["gameID"])
    utils.init_game(gameID)
    print(f"Created Game {gameID}")

async def join(websocket: WebSocketServerProtocol, event):
    gameID = int(event["gameID"])
    userID = int(event["userID"])
    # Replace the previous connection, this is desired when a user reloads the page
    utils.set_websocket(userID, websocket)
    try:
        connected: set[int] = utils.get_userIDs(gameID)
        utils.set_userIDs(gameID, connected | { userID })
        print(f"Player {userID} joined game {gameID}")
    except KeyError:
        print(f"Error could not find game {gameID}")
        event = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(event))

async def main():
    # In the case that we are running inside a docker container, we need to bind
    # to the container's external IP address so that we can receive messages
    async with websockets.serve(handler, "0.0.0.0", 8001):
        # Wait for a promise that will never be fulfilled - run forever
        print("Websocket server running")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
