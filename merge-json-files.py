"""Merge 5e.tools spell files into one

This module takes an arbitrary number of JSON files from the 5e.tools spell database
in the data/unmerged folder and ouputs them all into a single file in the data folder
called merged-spells.json.

"""
import os, json

my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "data/unmerged/")
base = {"spell": []}
for directory, subdirectories, files in os.walk(path):
    for file in files:
        base['spell'] += json.load(open(os.path.join(path, file)))['spell']
with open(os.path.join(my_path, "data/merged-spells.json"), "w") as outfile:
    json.dump(base, outfile)
