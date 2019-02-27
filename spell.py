"""D&D 5e spell

This module implements a python object representing the attributes of a D&D 5e spell. It takes the JSON information
from the 5e.tools website and provides a method to output the spell information to slack message format.

TODO:
    * Helper methods to strip out or implement special commands from the source data, e.g., {@ dice 6d6} in Fireball
"""


class Spell:

    def __init__(self, json_dict):
        """
        Builds the spell object from a dictionary imported from the 5e.tools JSON source files

        :param json_dict: dictionary containing a single spell loaded from JSON source files
        """
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
            if json_dict['duration'][0].get('concentration', False):
                self.duration += " (C)"
        else:
            self.duration = json_dict['duration'][0]['type']
        self.duration = self.duration.title()

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

    def format_slack_message(self):
        """Formats the spell's info for sending as a slack message
        :return:
            string: Contains the spell's info formatted for sending as slack message
        """
        # Name
        output = "*{}*\n".format(self.name)

        # Level/School/Ritual
        if self.level is not "0":
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
        output += self.description + "\n"

        # Source
        output += "_" + self.source + "_"

        return output


    def export_for_db(self, json_dict):
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
