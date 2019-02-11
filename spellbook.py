"""Spellbook slash command for slack

This module implements the /spellbook slash command for slack. Includes a mechanism for excluding certain users by id.

Environment variables required:
    * SLACK_VERIFICATION_TOKEN = bot OAUTH token from api.slack.com/apps
    * SLACK_TEAM_ID = Slack team id, which can be found by viewing/searching source on the web client

TO RUN:
    * SLACK_VERIFICATION_TOKEN=[VERIFICATION TOKEN] SLACK_TEAM_ID=[TEAM_ID] FLASK_APP=spellbook.py flask run
    * If running behind a NAT firewall, use ngrok to tunnel
    * Set slack app slash command URL to point to the ngrok tunnel or server with /spellbook at the end

TODO:
    * Handle spell names with apostrophes (unicode issues somewhere)
    * Do something about spells with charts (e.g., Confusion). Maybe direct users to the source material?
    * Implement better searching. Right now, it only responds to perfect case insensitive searches. It would be
        a lot better if "firebal" would say something like "I didn't find 'firebal.' Did you mean this?" and print
        the entry for fireball.

"""

import os
import json
import objectpath
from flask import abort, Flask, jsonify, request
from unidecode import unidecode
from spell import Spell


app = Flask(__name__)

# Load the data files and make a tree that's searchable with objectpath
my_path = os.path.abspath(os.path.dirname(__file__))
# If merged-spells.json doesn't exist, it can be generated from 5e.tools source files with merge-json-files.py
data_path = os.path.join(my_path, "data/merged-spells.json")
spells = json.load(open(data_path))
tree_obj = objectpath.Tree(spells)

def search_spell(search_str):
    result = tuple(tree_obj.execute("$.spell[@.name is '{}']".format(search_str.lower().title())))
    if result:
        return result[0]

def is_request_valid(request):
    is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
    is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']
    return is_token_valid and is_team_id_valid

@app.route('/spellbook', methods=['POST'])

def spellbook():
    if not is_request_valid(request):
        abort(400)
    input_text = request.form['text']

    # Deny certain users access
    if request.form['user_id'] == "U0JCUDM5F":
        return jsonify(
            response_type='in_channel',
            text="Eat shit, {}.".format(request.form['user_name'])
        )

    # Handle calls to /spellbook without any spell name
    if not input_text:
        return jsonify(
            response_type='in_channel',
            text="You have to tell me what spell to look up for you. I'm not a mind flayer."
        )

    # Search and respond
    result = search_spell(unidecode(input_text))
    if result:
        return jsonify(
            response_type='in_channel',
            text=Spell(result).format_slack_message()
        )
    else:
        return jsonify(
            response_type='in_channel',
            text="No spell by that name found."
        )