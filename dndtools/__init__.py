"""5Etools slash commands for slack
This module implements several slash commands for D&D groups using Slack:
    * /condition - a reference for conditions
    * /roll - a dice roller
    * /spellbook - a reference for spell text
Environment variables required:
    * SLACK_VERIFICATION_TOKEN = bot OAUTH token from api.slack.com/apps
    * SLACK_TEAM_ID = Slack team id, which can be found by viewing/searching source on the web client
TO RUN:
    * SLACK_VERIFICATION_TOKEN=[VERIFICATION TOKEN] SLACK_TEAM_ID=[TEAM_ID] FLASK_APP=dndtools.py flask run
    * If running behind a NAT firewall, use ngrok to tunnel
    * Set appropriate slack app slash command URLs to point to the ngrok tunnel or server with route at the end
    * See https://renzo.lucioni.xyz/serverless-slash-commands-with-python/ for help/outline of how this was developed
TODO:
    * Do something about spells with charts (e.g., Confusion). Maybe direct users to the source material?
    * Implement better searching. Right now, it only responds to perfect case insensitive searches. It would be
      a lot better if "firebal" would say something like "I didn't find 'firebal.' Did you mean this?" and print
      the entry for fireball.
    * Update db init script to take file argument so users can use different JSON files as desired
    * Put SRD spells JSON file in the repo? Would have to add Open Gaming License
"""

import os

from flask import current_app, Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask dndtools application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'spells.sql')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        app.config['SLACK_VERIFICATION_TOKEN'] = os.environ.get('SLACK_VERIFICATION_TOKEN', None)
        app.config['SLACK_TEAM_ID'] = os.environ.get('SLACK_TEAM_ID', None)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import condition
    app.register_blueprint(condition.bp)

    from . import roll
    app.register_blueprint(roll.bp)

    from . import spellbook
    app.register_blueprint(spellbook.bp)

    return app


def is_request_valid(request):
    if not current_app.config['SLACK_VERIFICATION_TOKEN'] or not current_app.config['SLACK_TEAM_ID']:
        return False
    is_token_valid = request.form['token'] == current_app.config['SLACK_VERIFICATION_TOKEN']
    is_team_id_valid = request.form['team_id'] == current_app.config['SLACK_TEAM_ID']
    return is_token_valid and is_team_id_valid
