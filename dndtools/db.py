import json
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

from spell import Spell


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('spell-schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the empty database.')
    db = get_db()
    with current_app.open_resource('spells.json') as f:
        spells = json.load(f)
        for s in spells['spell']:
            db.execute(
                'INSERT INTO spell (name, spell_level, school, source, cast_time, range, components, duration, ritual, '
                'description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', Spell(s).export_for_db(s)
            )
            db.commit()
    click.echo('Added spells.')
    click.echo('Initialization complete!')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
