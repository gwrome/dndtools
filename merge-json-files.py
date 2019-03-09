"""Merge 5e.tools spell files into one

This module takes an arbitrary number of JSON files from the 5e.tools spell database
in the data/unmerged folder and ouputs them all into a single file in the application folder
as merged-spells.json.
"""

import os
import json

my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "data/unmerged/")
base = {"spell": []}
for directory, subdirectories, files in os.walk(path):
    for file in files:
        base['spell'] += json.load(open(os.path.join(path, file)))['spell']
with open(os.path.join(os.path.join(my_path, "dndtools/"), "merged-spells.json"), "w") as outfile:
    json.dump(base, outfile)
