import os, dice
from flask import abort, Flask, jsonify, request


app = Flask(__name__)


def is_request_valid(request):
    is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
    is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']
    return is_token_valid and is_team_id_valid

@app.route('/roll', methods=['POST'])

def roll():
    if not is_request_valid(request):
        abort(400)
    input_text = request.form['text']
    if not input_text:
        return jsonify(
            response_type='in_channel',
            text="What dice would you like to roll?\n" +
                 "If you want individual die rolls, try something like _/roll 3d6_.\n" +
                 "If you just want a total, add a t to the end, like this: _/roll 4d10t_.\n" +
                 "For more complex syntax, see https://pypi.org/project/dice/"
        )
    return jsonify(
        response_type='in_channel',
        text=str(dice.roll(input_text))
    )
