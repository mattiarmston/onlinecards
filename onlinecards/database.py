import sqlite3

from flask import g

def get_db():
    # database = "dev.sqlite3"
    database = "http://flask_server/static/db.sqlite3"
    if "db" not in g:
        g.db = sqlite3.connect(
            database,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Return rows that behave like python dicts
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(error=None):
    # return None rather than a key error
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    # Call after every response
    app.teardown_appcontext(close_db)
