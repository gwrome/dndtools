"""D&D 5e spell

This module implements a python object representing the attributes of a D&D 5e spell. It takes the JSON information
from a local file and creates a Spell instance.

The json file can be in a basic format or in the formate used by the 5e.tools website.
"""

import re

class Spell:

    def __init__(self, json_dict=None, from_tools=False):
        """
        Builds the spell object from a dictionary imported from a JSON source file

        :param json_dict: dictionary containing a single spell loaded from JSON source files
        """
        # When building a Spell from a DB row, we want a plain object we can set manually rather than go through
        # all the translation logic below
        if not json_dict:
            return

        if from_tools:
            # Name of the spell
            self.name = json_dict['name']

            # Spell level
            self.level = str(json_dict['level'])

            # School of Magic
            schools = {"A":"Abjuration",
                       "C": "Conjuration",
                       "D":"Divination",
                       "E":"Enchantment",
                       "V":"Evocation",
                       "I":"Illusion",
                       "N":"Necromancy",
                       "P":"Psionic",
                       "T":"Transmutation",}

            self.school = schools[json_dict['school']]

            # Source of the spell
            self.source = json_dict['source']
            if 'page' in json_dict.keys():  # add the page number, if available
                self.source += " p. " + str(json_dict['page'])

            # Casting time
            self.cast_time = " ".join([str(json_dict['time'][0]['number']), json_dict['time'][0]['unit']])
            if 'condition' in json_dict['time'][0].keys():
                self.cast_time += " " + json_dict['time'][0]['condition']

            # Range is encoded differently depending on whether it's touch/self or ranged
            if json_dict['range'].get('distance', None):
                if "amount" in json_dict['range']['distance']:
                    self.range = str(json_dict['range']['distance']['amount']) + " " + \
                                 json_dict['range']['distance']['type']
                elif "type" in json_dict['range']['distance']:
                    self.range = json_dict['range']['distance']['type'].title()
            elif json_dict['range'].get('type', None) == 'special':
                self.range = "Special"

            # Spell components - Somatic & Verbal components give boolean values
            # if a material component is required, the value is the component's name
            self.components = []
            if json_dict.get('components', None):
                if "v" in json_dict['components'].keys():
                    self.components.append("V")
                if "s" in json_dict['components'].keys():
                    self.components.append("S")
                if "m" in json_dict['components'].keys():
                    if isinstance(json_dict['components']['m'], dict):
                        self.components.append("M ({})".format(json_dict['components']['m'].get('text', json_dict['components']['m'])))
                    else:
                        self.components.append("M ({})".format(json_dict['components']['m']))
                self.components = ", ".join(self.components)
            else:
                self.components = "None"

            # Spell duration
            self.duration = ""
            if json_dict['duration'][0]['type'] == 'timed':
                self.duration = str(json_dict['duration'][0]['duration']['amount'])
                self.duration += " {}".format(json_dict['duration'][0]['duration']['type'])
                if int(json_dict['duration'][0]['duration']['amount']) > 1:
                    self.duration += "s"
                if json_dict['duration'][0].get('concentration', False):
                    self.duration += " (concentration)"
            else:
                self.duration = json_dict['duration'][0]['type']
            self.duration = self.duration.capitalize()

            # Ritual tag
            self.ritual = False
            if 'meta' in json_dict.keys() and json_dict['meta'].get('ritual', False):
                self.ritual = True

            # The meat of the spell description
            self.description = ""
            entry_string = ""
            for e in json_dict['entries']:
                if isinstance(e, dict):
                    # This handles the entries with headers in the description, e.g., Control Winds's types of winds
                    if 'name' in e.keys():
                        entry_string += "\n\t_*" + e['name'] + ".*_ " + "".join(e['entries'])
                    # This handles entries with embedded lists, e.g., Conjure Woodland Creatures
                    if 'items' in e.keys():
                        entry_string += "\n"
                        for i in e['items']:
                            entry_string += "* " + i + "\n"
                else:
                    # This is where the plain paragraph part of spell descriptions are handled
                    entry_string += "\n\t" + e
            self.description += "\t" + entry_string + "\n"

            # Handles pretty common "at higher levels" entries, which is separately encoded
            if 'entriesHigherLevel' in json_dict.keys():
                self.description += "_*At Higher Levels.*_\n\t" + \
                           "".join(json_dict['entriesHigherLevel'][0]['entries']) + "\n"

            # Strip all the {@xyz} formatting language from the 5Etools files and replace with plain text
            clean_description = self.description

            replacements = [
                re.compile('(\{@dice ([+\-\d\w\s]*)\})'),                   # {@dice 1d4 +1} => 1d4 + 1
                re.compile('(\{@condition (\w+)\})'),                       # {@condition blinded} => blinded
                re.compile('(\{@scaledice [+\-\|\d\w\s]*(\d+d\d+)\})'),     # {@scaledice 3d12|3-9|1d12} => 1d12
                re.compile('(\{@creature ([\-\w\s]*)\})'),                  # {@creature dire wolf} => dire wolf
                re.compile('(\{@filter ([/\d\w\s]+)\|.+?\})'),              # {@filter challenge rating 6 or lower...}
            ]
            for r in replacements:
                m = r.findall(clean_description)
                if m:
                    for replacement in m:
                        clean_description = clean_description.replace(replacement[0], replacement[1])
            self.description = clean_description.strip()
        else:
            self.cast_time = json_dict['casting_time']
            self.components = json_dict['components']['raw']
            self.description = json_dict['description']
            if json_dict.get('higher_levels', None):
                self.description += "\n_*At Higher Levels.*_\n" + json_dict['higher_levels']
            self.duration = json_dict['duration']
            self.name = json_dict['name']
            self.range = json_dict['range']
            self.ritual = json_dict['ritual']
            self.school = json_dict['school'].title()
            if json_dict['level'] == 'cantrip':
                self.level = 0
            else:
                self.level = int(json_dict['level'])
            self.source = None

    def format_slack_message(self):
        """Formats the spell's info for sending as a slack message
        :return:
            string: Contains the spell's info formatted for sending as slack message
        """
        # Name
        output = "*{}*\n".format(self.name)

        # Level/School/Ritual
        if int(self.level) != 0:
            output += "_Level {} {}".format(self.level, self.school)
        else:
            output += "_{} cantrip".format(self.school)
        if self.ritual:
            output += " (ritual)"
        output += "_\n"

        # Casting time
        output += "*Casting Time:* {}\n".format(self.cast_time)

        # Range
        output += "*Range:* {}\n".format(self.range)

        # Components
        output += "*Components:* {}\n".format(self.components)

        # Duration
        output += "*Duration:* {}\n".format(self.duration)

        # Description
        output += "\n\t" + self.description + "\n"

        # Source
        if self.source:
            output += "_" + self.source + "_"

        return output


    def export_for_sqlite(self):
        return (self.name,
                int(self.level),
                self.school,
                self.source,
                self.cast_time,
                self.range,
                self.components,
                self.duration,
                int(self.ritual),
                self.description)


    def export_for_dynamodb(self):
        return {
            'name': self.name,
            'level': int(self.level),
            'school': self.school,
            'source': self.source,
            'cast_time': self.cast_time,
            'range': self.range,
            'components': self.components,
            'duration': self.duration,
            'ritual': bool(self.ritual),
            'description': self.description,
            'search_name': self.name.lower(),
        }


    @classmethod
    def from_sqlite(cls, db_result):
        spell = cls()
        spell.level = db_result['spell_level']
        spell.name = db_result['name']
        spell.school = db_result['school']
        spell.source = db_result['source']
        spell.cast_time = db_result['cast_time']
        spell.range = db_result['range']
        spell.components = db_result['components']
        spell.duration = db_result['duration']
        spell.ritual = db_result['ritual']
        spell.description = db_result['description']

        return spell

    @classmethod
    def from_dynamodb(cls, db_result):
        spell = cls()
        spell.level = db_result['level']
        spell.name = db_result['name']
        spell.school = db_result['school']
        spell.source = db_result['source']
        spell.cast_time = db_result['cast_time']
        spell.range = db_result['range']
        spell.components = db_result['components']
        spell.duration = db_result['duration']
        spell.ritual = db_result['ritual']
        spell.description = db_result['description']

        return spell
