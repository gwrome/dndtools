def test_single_roll(client):
    out_of_bounds = False
    for _ in range(100):
        result = client.post('/roll',
                             data=dict(text='1d4',
                                       team_id='test-team-id',
                                       token='test-token')).get_json()['text']
        if int(''.join(result[1:-1])) > 4:
            out_of_bounds = True

    assert not out_of_bounds


def test_multiple_rolls(client):
    wrong_number = False
    for n in range(1, 21):
        result = client.post('/roll',
                             data=dict(text='{}d6'.format(n),
                                       team_id='test-team-id',
                                       token='test-token')).get_json()['text']
        if len(result[1:-1].split(",")) != n:
            wrong_number = True

    assert not wrong_number


def test_total(client):
    out_of_bounds = False
    for _ in range(100):
        result = int(client.post('/roll',
                             data=dict(text='20d8t',
                                       team_id='test-team-id',
                                       token='test-token')).get_json()['text'])
        if result < 20 or result > 160:
            out_of_bounds = True

    assert not out_of_bounds


def test_blank(client):
    error_message = "What dice would you like to roll?"
    assert error_message in client.post('/roll',
                                        data=dict(text="",
                                                  team_id='test-team-id',
                                                  token='test-token',
                                                  user_id='asdf')).get_json()['text']


def test_bad_input(client):
    error_message = "Invalid roll. Try again."
    assert error_message in client.post('/roll',
                                        data=dict(text="asdfasdfasdf",
                                                  team_id='test-team-id',
                                                  token='test-token',
                                                  user_id='asdf')).get_json()['text']
