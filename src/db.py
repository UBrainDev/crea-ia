import sqlite3
import click
from flask import current_app, g


def get_db():

    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

        # si la base de données est vide, on l'initialise
        if g.db.execute('SELECT COUNT(*) FROM sqlite_schema').fetchone()[0] == 0:
            init_db()

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():

    print('Initialisation de la base de données...')

    db = get_db()

    with current_app.open_resource('src/ressources/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        db.commit()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
