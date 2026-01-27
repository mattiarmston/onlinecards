import random, json, asyncio, websockets

from flask import Flask, render_template, request, redirect, make_response
from sqlite3 import Connection
from typing import Any

import database

def create_app():
    # Gives current path to flask
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/rules/")
    def rules():
        return render_template("rules.html")

    @app.get("/rules/whist")
    def rules_whist():
        return render_template("rules_whist.html")

    @app.get("/games/new")
    def games_new_get():
        return render_template("games_new.html")

    def new_gameID(db: Connection) -> int:
        cursor = db.cursor()
        while True:
            gameID = random.randint(1, 999999)
            existing_game = cursor.execute(
                "SELECT gameID FROM games WHERE gameID = ?",
                [gameID]
            ).fetchone()
            if existing_game == None:
                break
        return gameID

    def create_config(form):
        game_type = form["game_type"]
        match game_type:
            case "whist":
                return {
                    "game_type": game_type,
                    "scoring": form["scoring"],
                    "length": form["length"],
                }
            case _:
                return {"game_type": game_type}

    def create_game() -> int:
        db = database.get_db()
        gameID = new_gameID(db)
        config = create_config(request.form)
        configJSON = json.dumps(config)
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO games(gameID, config) VALUES (?, ?)",
            [gameID, configJSON]
        )
        db.commit()
        return gameID

    async def ws_create_game(gameID):
        async with websockets.connect("ws://ws_server:8001") as ws:
            data = {
                "type": "create",
                "gameID": gameID,
            }
            await ws.send(json.dumps(data))

    @app.post("/games/new")
    def games_new_post():
        game_type = request.form["game_type"]
        if game_type not in ["chatroom", "whist"]:
            return "Unsupported game {}".format(game_type), 400
        gameID = create_game()
        asyncio.run(ws_create_game(gameID))
        return redirect(f"/games/join/{gameID}")

    @app.get("/games/join/")
    def games_join_get(error_msg=""):
        return render_template("games_join.html", error=error_msg)

    def get_game_template(game_type, gameID, configJSON=""):
        match game_type:
            case "chatroom":
                return render_template(
                    "chatroom.html", gameID=gameID
                )
            case "whist":
                return render_template(
                    "whist.html", gameID=gameID
                )
            case _:
                return render_template(
                    # This should be removed / replaced later with an error message
                    "games_join_post.html", gameID=gameID, config=configJSON
                )

    def config_from_gameID(gameID: int) -> dict[str, Any]:
        db = database.get_db()
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT * FROM games WHERE gameID = ?",
            [gameID]
        ).fetchone()
        if result == None:
            raise ValueError
        configJSON = result["config"]
        config = json.loads(configJSON)
        return config

    def new_userID(db: Connection) -> int:
        cursor = db.cursor()
        while True:
            userID = random.randint(1, 999999)
            existing_user = cursor.execute(
                "SELECT userID FROM users WHERE userID = ?",
                [userID]
            ).fetchone()
            if existing_user == None:
                break
        return userID

    def create_user() -> int:
        db = database.get_db()
        userID = new_userID(db)
        username = request.form["username"]
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users(userID, username) VALUES (?, ?)",
            [userID, username]
        )
        db.commit()
        return userID

    @app.get("/games/join/<gameID>")
    def games_join_ID_get(gameID):
        try:
            config = config_from_gameID(gameID)
        except ValueError:
            return games_join_get(error_msg=f"Error: game {gameID} cannot be found")
        userID = request.cookies.get("userID")
        if userID == None:
            return render_template(
                "username.html"
            )
        return get_game_template(config["game_type"], gameID)
    
    @app.post("/games/join/<gameID>")
    def games_join_ID_post(gameID):
        try:
            config = config_from_gameID(gameID)
        except ValueError:
            return games_join_get(error_msg=f"Error: game {gameID} cannot be found")
        userID = create_user()
        response = make_response(
            get_game_template(config["game_type"], gameID)
        )
        response.set_cookie("userID", str(userID))
        return response

    @app.after_request
    def set_cached(response):
        if request.method == "GET":
            if request.path.startswith("/static/cards-fancy") or \
               request.path.startswith("/static/card-simple"):
                # Cache is valid for an arbitrarily long time (1 year)
                response.cache_control.max_age = 60 * 60 * 24 * 365
                response.cache_control.no_cache = False
                response.cache_control.immutable = True
        return response

    database.init_db(app)

    return app

app = create_app()
