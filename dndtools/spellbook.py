"""Flask blueprint for /spell command, which provides the text of D&D spells"""

from flask import abort, Blueprint, current_app, jsonify, request
from boto3.dynamodb.conditions import Attr
from spell import Spell
from dndtools import is_request_valid
from dndtools.db import get_db

bp = Blueprint('spellbook', __name__)


def search_spell(search_str):
    """Look up a spell by name

    Args:
        search_str: a string containing some or all of the name of the spell the user wants

    Returns:
        a dict containing the requested spell data from the database or None
    """
    db = get_db()
    # TODO: Remove code for sqlite or set up app to allow for either database
    # for sqlite backend
    # result = db.execute(
    #     'SELECT * FROM spell WHERE LOWER(name) = LOWER(?)', (search_str,)
    # ).fetchone()
    # return result
    # return db.tables['spells'].get_item(Key={'search_name': search_str.lower()}).get('Item', None)

    # If there's a perfect match, return that. Otherwise search for the text in the spell name.
    perfect_match = db.tables['spells'].scan(FilterExpression=Attr('search_name').eq(search_str.lower()))['Items']
    if perfect_match:
        return perfect_match[0]
    contains_match = db.tables['spells'].scan(FilterExpression=Attr('search_name').contains(search_str.lower()))[
        'Items']
    return next(iter(contains_match), None)


@bp.route('/spellbook', methods=['POST'])
def spellbook():
    """Look for the spell a user requests and provide its information

    Returns:
        a json dict containing the spell's details formatted for Slack, a diagnostic message, or an error message
    """
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
            text=Spell.from_dynamodb(result).format_slack_message()
        )
    else:
        return jsonify(
            response_type='in_channel',
            text="No spell by that name found."
        )
