"""A Flask app to support Slack slash commands for D&D 5E players

This app implements several slash commands:
    * /condition - a reference for conditions
    * /roll - a dice roller
    * /spellbook - a reference for spell text

Environment variables required:
    * SLACK_VERIFICATION_TOKEN = bot OAUTH token from api.slack.com/apps
    * SLACK_TEAM_ID = Slack team id, which can be found by viewing/searching source on the web client

TODO:
    * Do something about spells with charts (e.g., Confusion). Maybe direct users to the source material?
    * Give the option to use SQL instead of DynamoDB
"""

import os

from flask import current_app, Flask
from flask_dynamo import Dynamo


def create_app(test_config=None):
    """Create and configure an instance of the Flask dndtools application.

    Args:
        test_config: dict containing pytest configuration settings
    """
    app = Flask(__name__, instance_relative_config=True)

    # for sqlite backend
    # app.config.from_mapping(
    #     DATABASE=os.path.join(app.instance_path, 'spells.sql')
    # )

    if os.environ.get('FLASK_ENV', None) == 'development':
        app.config['DYNAMO_ENABLE_LOCAL'] = True
        app.config['DYNAMO_LOCAL_HOST'] = 'localhost'
        app.config['DYNAMO_LOCAL_PORT'] = 8000

    app.config['DYNAMO_TABLES'] = [
        {
            'TableName': 'spells',
            'KeySchema': [dict(AttributeName='name', KeyType='HASH')],
            'AttributeDefinitions': [dict(AttributeName='name', AttributeType='S')],
            'ProvisionedThroughput': dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        }
    ]

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        app.config['SLACK_VERIFICATION_TOKEN'] = os.environ.get('SLACK_VERIFICATION_TOKEN', None)
        app.config['SLACK_TEAM_ID'] = os.environ.get('SLACK_TEAM_ID', None)
        app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', None)
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

    dynamo = Dynamo()
    dynamo.init_app(app)

    return app


def is_request_valid(request):
    """Verifies that a request contains the correct Slack security token and team ID

    Args:
        request: dict containing the HTTP POST request sent to the app

    Returns:
        True if the request is valid, False otherwise
    """
    if not current_app.config['SLACK_VERIFICATION_TOKEN'] or not current_app.config['SLACK_TEAM_ID']:
        return False
    is_token_valid = request.form['token'] == current_app.config['SLACK_VERIFICATION_TOKEN']
    is_team_id_valid = request.form['team_id'] == current_app.config['SLACK_TEAM_ID']
    return is_token_valid and is_team_id_valid
