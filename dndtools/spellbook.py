from flask import abort, Blueprint, current_app, jsonify, request
from spell import Spell
from dndtools import is_request_valid
from dndtools.db import get_db

bp = Blueprint('spellbook', __name__)


def search_spell(search_str):
    db = get_db()
    result = db.execute(
        'SELECT * FROM spell WHERE LOWER(name) = LOWER(?)', (search_str,)
    ).fetchone()
    return result


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
            text=Spell.from_db(result).format_slack_message()
        )
    else:
        return jsonify(
            response_type='in_channel',
            text="No spell by that name found."
        )
