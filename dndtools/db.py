import json
# import sqlite3
import time

import click
from flask import current_app, g
from flask.cli import with_appcontext

from spell import Spell


def get_db():
    # for sqlite backend
    # if 'db' not in g:
    #     g.db = sqlite3.connect(
    #         current_app.config['DATABASE'],
    #         detect_types=sqlite3.PARSE_DECLTYPES
    #     )
    #     g.db.row_factory = sqlite3.Row
    # return g.db
    return current_app.extensions['dynamo']

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    with current_app.app_context():
        db = get_db()
        db.destroy_all(wait=True)
        db.create_all(wait=True)

    # For sqlite implementations
    #
    # db = get_db()
    #
    # with current_app.open_resource('spell-schema.sql') as f:
    #     db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@click.option('--infile', default='srd-spells.json', help='JSON input file relative to dndtools directory')
@click.option('--tools', is_flag=True)
@with_appcontext
def init_db_command(infile, tools):
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the empty database.')
    # for sqlite backend
    # db = get_db()
    db = current_app.extensions['dynamo']
    with current_app.open_resource(infile) as f:
        spells = json.load(f)
        if tools:
            for s in spells['spell']:
                db.tables['spells'].put_item(Item=Spell(s, from_tools=True).export_for_dynamodb())
        else:
            for s in spells:
                db.tables['spells'].put_item(Item=Spell(s).export_for_dynamodb())
        # for sqlite backend
        # db.execute(
        #     'INSERT INTO spell (name, spell_level, school, source, cast_time, range, components, duration, ritual, '
        #     'description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', Spell(s).export_for_sqlite()
        # )
        # db.commit()
    click.echo('Added spells.')
    click.echo('Initialization complete!')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
