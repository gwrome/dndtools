"""Flask blueprint for /roll command, which rolls dice and sends the results"""

import dice
from dndtools import is_request_valid
from flask import abort, Blueprint, jsonify, request

bp = Blueprint('roll', __name__)


@bp.route('/roll', methods=['POST'])
def roll():
    """Rolls dice and reports the results.

    Raises:
        DiceException: if the input is invalid

    Returns:
        json dict with the roll results, a help message, or an error message
    """
    if not is_request_valid(request):
        abort(401)
    input_text = request.form['text']
    if not input_text:
        return jsonify(
            response_type='in_channel',
            text="What dice would you like to roll?\n" +
                 "If you want individual die rolls, try something like _/roll 3d6_.\n" +
                 "If you just want a total, add a t to the end, like this: _/roll 4d10t_.\n" +
                 "For more complex syntax, see https://pypi.org/project/dice/"
        )
    try:
        roll_result = str(dice.roll(input_text))
    except dice.DiceException:
        roll_result = "Invalid roll. Try again."
    return jsonify(
        response_type='in_channel',
        text=roll_result
    )
