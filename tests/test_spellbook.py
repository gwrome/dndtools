def test_lowercase_spell(client):
    assert "Fireball" in client.post('/spellbook',
                                     data=dict(text="fireball",
                                               team_id='test-team-id',
                                               token='test-token',
                                               user_id='asdf')).get_json()['text']


def test_uppercase_spell(client):
    assert "Fireball" in client.post('/spellbook',
                                     data=dict(text="FIREBALL",
                                               team_id='test-team-id',
                                               token='test-token',
                                               user_id='asdf')).get_json()['text']


def test_titlecase_spell(client):
    assert "Fireball" in client.post('/spellbook',
                                     data=dict(text="Fireball",
                                               team_id='test-team-id',
                                               token='test-token',
                                               user_id='asdf')).get_json()['text']


def test_apostrophe_spell(client):
    assert "Tiny Hut" in client.post('/spellbook',
                                     data=dict(text="Leomund's Tiny Hut",
                                               team_id='test-team-id',
                                               token='test-token',
                                               user_id='asdf')).get_json()['text']


def test_blank(client):
    error_message = "You have to tell me what spell to look up for you. I'm not a mind flayer."
    assert error_message in client.post('/spellbook',
                                        data=dict(text="",
                                                  team_id='test-team-id',
                                                  token='test-token',
                                                  user_id='asdf')).get_json()['text']


def test_bad_input(client):
    error_message = "No spell by that name found."
    assert error_message in client.post('/spellbook',
                                        data=dict(text="asdfasdfasdf",
                                                  team_id='test-team-id',
                                                  token='test-token',
                                                  user_id='asdf')).get_json()['text']


