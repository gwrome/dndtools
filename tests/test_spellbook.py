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


def test_durations(client):
    hut_response = client.post('/spellbook',
                               data=dict(text="Leomund's Tiny Hut",
                                         team_id='test-team-id',
                                         token='test-token',
                                         user_id='asdf')).get_json()['text']
    assert '*Duration:* 8 hours' in hut_response

    fireball_response = client.post('/spellbook',
                                     data=dict(text="Fireball",
                                               team_id='test-team-id',
                                               token='test-token',
                                               user_id='asdf')).get_json()['text']
    assert '*Duration:* Instant' in fireball_response

    cloud_response = client.post('/spellbook',
                                 data=dict(text="Incendiary Cloud",
                                           team_id='test-team-id',
                                           token='test-token',
                                           user_id='asdf')).get_json()['text']
    assert '*Duration:* 1 minute (concentration)' in cloud_response

    imprisonment_response = client.post('/spellbook',
                                        data=dict(text="Imprisonment",
                                                  team_id='test-team-id',
                                                  token='test-token',
                                                  user_id='asdf')).get_json()['text']
    assert '*Duration:* Permanent' in imprisonment_response

def test_cantrip(client):
    assert "cantrip" in client.post('/spellbook',
                                    data=dict(text="Shocking Grasp",
                                              team_id='test-team-id',
                                              token='test-token',
                                              user_id='asdf')).get_json()['text']
