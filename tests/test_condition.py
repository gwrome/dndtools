def test_conditions(client):
    conditions = "Blinded Charmed Deafened Exhaustion Frightened Grappled Incapacitated Invisible Paralyzed " \
                 "Petrified Poisoned Prone Restrained Stunned Unconscious"
    for c in conditions.split():
        assert "*{}*".format(c) in client.post('/condition',
                                               data=dict(text=c.lower(),
                                                         team_id='test-team-id',
                                                         token='test-token')).get_json()['text']


def test_blank(client):
    error_message = "What condition are you asking me about?"
    assert error_message in client.post('/condition',
                                        data=dict(text="",
                                                  team_id='test-team-id',
                                                  token='test-token',
                                                  user_id='asdf')).get_json()['text']


def test_bad_input(client):
    error_message = "What condition are you asking me about?"
    assert error_message in client.post('/condition',
                                        data=dict(text="asdfasdfasdf",
                                                  team_id='test-team-id',
                                                  token='test-token',
                                                  user_id='asdf')).get_json()['text']
