from flask import abort, Blueprint, current_app, jsonify, request
from boto3.dynamodb.conditions import Attr
from spell import Spell
from dndtools import is_request_valid
from dndtools.db import get_db

bp = Blueprint('spellbook', __name__)


def search_spell(search_str):
    db = get_db()
    # for sqlite backend
    # result = db.execute(
    #     'SELECT * FROM spell WHERE LOWER(name) = LOWER(?)', (search_str,)
    # ).fetchone()
    # return result
    # return db.tables['spells'].get_item(Key={'search_name': search_str.lower()}).get('Item', None)
    perfect_match = db.tables['spells'].scan(FilterExpression=Attr('search_name').eq(search_str.lower()))['Items']
    if perfect_match:
        return perfect_match[0]
    contains_match = db.tables['spells'].scan(FilterExpression=Attr('search_name').contains(search_str.lower()))[
        'Items']
    return next(iter(contains_match), None)


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
            text=Spell.from_dynamodb(result).format_slack_message()
        )
    else:
        return jsonify(
            response_type='in_channel',
            text="No spell by that name found."
        )
