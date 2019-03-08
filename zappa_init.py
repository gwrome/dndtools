"""
" This file is a workaroudn because zappa doesn't play nice calling a Flask app-factory pattern app directly.
" This will likely be fixed soon, see pull request here: https://github.com/Miserlou/Zappa/pull/1775
" For now, in zappa_settings.json, point "app_function" to "zappa_init.app", which then calls the app factory
"""
from dndtools import create_app

app = create_app()
