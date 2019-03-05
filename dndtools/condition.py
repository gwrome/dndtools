from flask import abort, Blueprint, jsonify, request
from dndtools import is_request_valid

bp = Blueprint('condition', __name__)


@bp.route('/condition', methods=['POST'])
def condition():
    # Source: D&D 5e handbook
    conditions = {
        "blinded": "* A blinded creature can't see and automatically fails any ability check that requires "
                   "sight.\n"
                   "* Attack rolls against the creature have advantage, "
                   "and the creature's attack rolls have disadvantage.",
        "charmed": "* A charmed creature can't attack the charmer or target the charmer with harmful "
                   "abilities or magical effects.\n"
                   "* The charmer has advantage on any ability check to interact socially with the creature.",
        "deafened": "A deafened creature can't hear and automatically fails any ability check that requires "
                    "hearing.",
        "frightened": "* A frightened creature has disadvantage on ability checks and attack rolls while the "
                      "source of its fear is within line of sight.\n"
                      "* The creature can't willingly move closer to the source of its fear.",
        "grappled": "* A grappled creature's speed becom es 0, and it can't benefit from any bonus to its "
                    "speed.\n"
                    "* The condition ends if the grappler is incapacitated (see the condition).\n"
                    "* The condition also ends if an effect removes the grappled creature from the reach "
                    "of the grappler or grappling effect, such as when a creature is hurled away by "
                    "the _thunderwave_ spell.",
        "incapacitated": "An incapacitated creature can't take actions or reactions.",
        "invisible": "* An invisible creature is impossible to see without the aid of magic or a special sense. "
                     "For the purpose of hiding, the creature is heavily obscured. The creature's location can "
                     "be detected by any noise it makes or any tracks it leaves.\n"
                     "* Attack rolls against the creature have disadvantage, and the creature's attack rolls "
                     "have advantage.",
        "paralyzed": "* A paralyzed creature is incapacitated (see the condition) and can't move or speak.\n"
                     "* The creature automatically fails Strength and Dexterity saving throws.\n"
                     "* Attack rolls against the creature have advantage.\n"
                     "* Any attack that hits the creature is a critical hit if the attacker is within 5 feet "
                     "of the creature.",
        "petrified": "* A petrified creature is transformed, along with any nonmagical object it is wearing or "
                     "carrying, into a solid inanimate substance (usually stone). Its weight increases by a "
                     "factor of ten, and it ceases aging.\n"
                     "* The creature is incapacitated (see the condition), can't move or speak, and is unaware "
                     "of its surroundings.\n"
                     "* Attack rolls against the creature have advantage.\n"
                     "* The creature automatically fails Strength and Dexterity saving throws.\n"
                     "* The creature has resistance to all damage.\n"
                     "* The creature is immune to poison and disease, although a poison or disease already in "
                     "its system is suspended, not neutralized.",
        "poisoned": "A poisoned creature has disadvantage on attack rolls and ability checks.",
        "prone": "* A prone creature's only Movement option is to crawl, unless it stands up and thereby "
                 "ends the condition.\n"
                 "* The creature has disadvantage on Attack rolls.\n"
                 "* An Attack roll against the creature has advantage if the attacker is within 5 feet of "
                 "the creature. Otherwise, the Attack roll has disadvantage.",
        "restrained": "* A restrained creature's speed becomes 0, and it can't benefit from any bonus to its "
                      "speed.\n"
                      "* Attack rolls against the creature have advantage, and the creature's Attack rolls "
                      "have disadvantage.\n"
                      "* The creature has disadvantage on Dexterity Saving Throws.",
        "stunned": "* A stunned creature is incapacitated (see the condition), can't move, and can speak only "
                   "falteringly.\n"
                   "* The creature automatically fails Strength and Dexterity Saving Throws.\n"
                   "* Attack rolls against the creature have advantage.",
        "unconscious": "* An unconscious creature is incapacitated (see the condition), can't move or speak,"
                       " and is unaware of its surroundings.\n"
                       "* The creature drops whatever it's holding and falls prone.\n"
                       "* The creature automatically fails Strength and Dexterity Saving Throws.\n"
                       "* Attack rolls against the creature have advantage.\n"
                       "* Any attack that hits the creature is a critical hit if the attacker is within 5 feet "
                       "of the creature.",
        "exhaustion": "Some special abilities and environmental hazards, such as starvation and the long-term "
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
                      "*3:* Disadvantage on Attack rolls and Saving Throws\n"
                      "*4:* Hit point maximum halved\n"
                      "*5:* Speed reduced to 0\n"
                      "*6:* Death"
    }

    if not is_request_valid(request):
        abort(401)
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