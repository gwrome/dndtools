"""5Etools slash commands for slack

This module implements severak slash commands for D&D groups using Slack:
    * /condition - a reference for conditions
    * /roll - a dice roller
    * /spellbook - a reference for spell text

Environment variables required:
    * SLACK_VERIFICATION_TOKEN = bot OAUTH token from api.slack.com/apps
    * SLACK_TEAM_ID = Slack team id, which can be found by viewing/searching source on the web client

TO RUN:
    * SLACK_VERIFICATION_TOKEN=[VERIFICATION TOKEN] SLACK_TEAM_ID=[TEAM_ID] FLASK_APP=DnDtools.py flask run
    * If running behind a NAT firewall, use ngrok to tunnel
    * Set appropiate slack app slash command URLs to point to the ngrok tunnel or server with route at the end
    * See https://renzo.lucioni.xyz/serverless-slash-commands-with-python/ for help/outline of how this was developed

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
import dice
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
    try:
        roll_result = str(dice.roll(input_text))
    except dice.DiceException:
        roll_result = "Invalid roll. Try again."
    return jsonify(
        response_type='in_channel',
        text=roll_result
    )

@app.route('/condition', methods=['POST'])
def condition():
    # Source: D&D 5e handbook
    conditions = {
        "blinded":          "* A blinded creature can't see and automatically fails any ability check that requires "
                            "sight.\n"
                            "* Attack rolls against the creature have advantage, "
                            "and the creature's attack rolls have disadvantage.",
        "charmed":          "* A charmed creature can't attack the charmer or target the charmer with harmful "
                            "abilities or magical effects.\n"
                            "* The charmer has advantage on any ability check to interact socially with the creature.",
        "deafened":         "A deafened creature can't hear and automatically fails any ability check that requires "
                            "hearing.",
        "frightened":       "* A frightened creature has disadvantage on ability checks and attack rolls while the "
                            "source of its fear is within line of sight.\n"
                            "* The creature can't willingly move closer to the source of its fear.",
        "grappled":         "* A grappled creature's speed becom es 0, and it can't benefit from any bonus to its "
                            "speed.\n"
                            "* The condition ends if the grappler is incapacitated (see the condition).\n"
                            "* The condition also ends if an effect removes the grappled creature from the reach "
                            "of the grappler or grappling effect, such as when a creature is hurled away by "
                            "the _thunderwave_ spell.",
        "incapacitated":    "An incapacitated creature can't take actions or reactions.",
        "invisible":        "* An invisible creature is impossible to see without the aid of magic or a special sense. "
                            "For the purpose of hiding, the creature is heavily obscured. The creature's location can "
                            "be detected by any noise it makes or any tracks it leaves.\n"
                            "* Attack rolls against the creature have disadvantage, and the creature's attack rolls "
                            "have advantage.",
        "paralyzed":        "* A paralyzed creature is incapacitated (see the condition) and can't move or speak.\n"
                            "* The creature automatically fails Strength and Dexterity saving throws.\n"
                            "* Attack rolls against the creature have advantage.\n"
                            "* Any attack that hits the creature is a critical hit if the attacker is within 5 feet "
                            "of the creature.",
        "petrified":        "* A petrified creature is transformed, along with any nonmagical object it is wearing or "
                            "carrying, into a solid inanimate substance (usually stone). Its weight increases by a "
                            "factor of ten, and it ceases aging.\n"
                            "* The creature is incapacitated (see the condition), can't move or speak, and is unaware "
                            "of its surroundings.\n"
                            "* Attack rolls against the creature have advantage.\n"
                            "* The creature automatically fails Strength and Dexterity saving throws.\n"
                            "* The creature has resistance to all damage.\n"
                            "* The creature is immune to poison and disease, although a poison or disease already in "
                            "its system is suspended, not neutralized.",
        "poisoned":         "A poisoned creature has disadvantage on attach rolls and ability checks.",
        "prone":            "* A prone creature's only Movement option is to crawl, unless it stands up and thereby "
                            "ends the condition.\n"
                            "* The creature has disadvantage on Attack rolls.\n"
                            "* An Attack roll against the creature has advantage if the attacker is within 5 feet of "
                            "the creature. Otherwise, the Attack roll has disadvantage.",
        "restrained":       "* A restrained creature's speed becomes 0, and it can't benefit from any bonus to its "
                            "speed.\n"
                            "* Attack rolls against the creature have advantage, and the creature's Attack rolls "
                            "have disadvantage.\n"
                            "* The creature has disadvantage on Dexterity Saving Throws.",
        "stunned":          "* A stunned creature is incapacitated (see the condition), can't move, and can speak only "
                            "falteringly.\n"
                            "* The creature automatically fails Strength and Dexterity Saving Throws.\n"
                            "* Attack rolls against the creature have advantage.",
        "unconscious":      "* An unconscious creature is incapacitated (see the condition), can't move or speak,"
                            " and is unaware of its surroundings.\n"
                            "* The creature drops whatever it's holding and falls prone.\n"
                            "* The creature automatically fails Strength and Dexterity Saving Throws.\n"
                            "* Attack rolls against the creature have advantage.\n"
                            "* Any attack that hits the creature is a critical hit if the attacker is within 5 feet "
                            "of the creature.",
        "exhaustion":       "Some special abilities and environmental hazards, such as starvation and the long-term "
                            "effects of freezing or scorching temperatures, can lead to a special condition called "
                            "exhaustion. Exhaustion is measured in six levels. An effect can give a creature one or "
                            "more levels of exhaustion, as specified in the effect's description.\n"
                            "If an already exhausted creature suffers another effect that causes exhaustion, its "
                            "current level of exhaustion increases by the amount specified in the effect's "
                            "description.\n"
                            "A creature suffers the effect of its current level of exhaustion as well as all lower "
                            "levels. For example, a creature suffering level 2 exhaustion has its speed halved and "
                            "has disadvantage on Ability Checks.\n"
                            "An effect that removes exhaustion reduces its level as specified in the effect's "
                            "description, with all exhaustion Effects ending if a creature's exhaustion level is "
                            "reduced below 1.\n"
                            "Finishing a Long Rest reduces a creature's exhaustion level by 1, provided that the "
                            "creature has also ingested some food and drink.\n\n"
                            "*Exhaustion Effects:*\n"
                            "*1:* Disadvantage on Ability Checks\n"
                            "*2:* Speed halved\n"
                            "*3:* Disadvantage on Attach rolls and Saving Throws\n"
                            "*4:* Hit point maximum halved\n"
                            "*5:* Speed reduced to 0\n"
                            "*6:* Death"
    }

    if not is_request_valid(request):
        abort(400)
    input_text = request.form['text'].lower()
    if input_text in conditions.keys():
        return jsonify(
            response_type='in_channel',
            text="*" + input_text.title() + "*\n\n" + conditions[input_text]
        )
    # if the user doesn't input a condition or inputs a typo/nonexistent condition
    else:
        return jsonify(
            response_type='in_channel',
            text="What condition are you asking me about?\n" +
                 "* " + "\n* ".join([c.title() for c in sorted(conditions.keys())])
        )