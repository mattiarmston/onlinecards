import database

from websockets.legacy.server import WebSocketServerProtocol

# `GAMES` links from a `gameID` to a set of connected `userID`s
# GAMES = {
#     gameID: {
#         userID: int,
#         ...
#     },
#     ...
# }

GAMES: dict[int, set[int]] = {}

# `USERS` links from a `userID` to a websocket connection
# USERS = {
#     userID: Websocket,
#     ...
# }

USERS: dict[int, WebSocketServerProtocol] = {}

def init_game(gameID: int) -> None:
    GAMES[gameID] = set()

def get_userIDs(gameID: int) -> set[int]:
    return GAMES[gameID]

def set_userIDs(gameID: int, userIDs: set[int]) -> None:
    GAMES[gameID] = userIDs
    return

def websockets_from_gameID(gameID: int) -> dict[int, WebSocketServerProtocol]:
    websockets = {}
    for userID in get_userIDs(gameID):
        try:
            websockets[userID] = USERS[userID]
        except KeyError:
            print(f"Error: could not find userID {userID}")
    return websockets

def get_websocket(userID: int) -> WebSocketServerProtocol:
    return USERS[userID]

def set_websocket(userID: int, websocket) -> None:
    USERS[userID] = websocket

def get_username(userID: int, app) -> str:
    with app.app_context():
        cursor = database.get_db().cursor()
        result = cursor.execute(
            "SELECT username FROM users WHERE userID = ?",
            [userID]
        ).fetchone()
        username = result["username"]
        return username

