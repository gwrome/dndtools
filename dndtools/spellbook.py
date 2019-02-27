import json
from string import capwords
import os

from flask import abort, Blueprint, current_app, jsonify, request
from spell import Spell
from dndtools import is_request_valid

bp = Blueprint('spellbook', __name__)


def search_spell(search_str):
    # If merged-spells.json doesn't exist, it can be generated from 5e.tools source files with merge-json-files.py
    with current_app.open_instance_resource('merged-spells.json') as f:
        spells = json.load(f)
        result = [spell for spell in spells['spell'] if spell['name'] == capwords(search_str)]
        if result:
            return result[0]
        else:
            return []


@bp.route('/spellbook', methods=['POST'])
def spellbook():
    if not is_request_valid(request):
        abort(401)
    input_text = request.form['text']

    # Handle calls to /spellbook without any spell name
    if not input_text:
        return jsonify(
            response_type='in_channel',
            text="You have to tell me what spell to look up for you. I'm not a mind flayer."
        )

    # Replace unicode right-hand quotation mark with ASCII '
    input_text = input_text.replace("’", "'")
    # Search and respond
    result = search_spell(input_text)
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
