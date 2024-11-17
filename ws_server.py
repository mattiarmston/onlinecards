import websockets, asyncio, json

import database
import server
import games

from chatroom import handle_chatroom
from whist import handle_whist

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
            case _:
                with server.app.app_context():
                    gameID = int(event["gameID"])
                    cursor = database.get_db().cursor()
                    result = cursor.execute(
                        "SELECT config FROM games WHERE gameID = ?",
                        [gameID]
                    ).fetchone()
                    config = json.loads(result["config"])
                game_handler = get_game_handler(config["game"])
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
    games.GAMES[gameID] = set()
    print(f"Created Game {gameID}")

async def join(websocket, event):
    gameID = int(event["gameID"])
    try:
        connected: set[WebSocketServerProtocol] = games.GAMES[gameID]
        games.GAMES[gameID] = connected | { websocket }
        print(f"New player joined game {gameID}")
    except KeyError:
        print(f"Error could not find {gameID}")
        event = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(event))

async def main():
    async with websockets.serve(handler, "", 8001):
        # Wait for a promise that will never be fulfilled - run forever
        print("Websocket server running")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
