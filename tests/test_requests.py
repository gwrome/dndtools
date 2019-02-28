from dndtools import create_app, is_request_valid

def test_no_env_vars(client):
    app = create_app()
    with app.app_context():
        app.config['SLACK_VERIFICATION_TOKEN'] = None
        app.config['SLACK_TEAM_ID'] = None
        dummy_request = {}
        assert not is_request_valid(dummy_request)


def test_no_app_verification_token(client):
    app = create_app()
    with app.app_context():
        app.config['SLACK_VERIFICATION_TOKEN'] = None
        dummy_request = {}
        assert not is_request_valid(dummy_request)


def test_no_app_team_id(client):
    app = create_app()
    with app.app_context():
        app.config['SLACK_TEAM_ID'] = None
        dummy_request = {}
        assert not is_request_valid(dummy_request)


def test_request_tokens(client):
    for route in 'condition roll spellbook'.split():
        assert '401' in str(client.post('/{}'.format(route),
                                        data=dict(text="",
                                                  team_id='wrong-test-team-id',
                                                  token='test-token',
                                                  user_id='asdf')))

        assert '401' in str(client.post('/{}'.format(route),
                                        data=dict(text="",
                                                  team_id='test-team-id',
                                                  token='wrong-test-token',
                                                  user_id='asdf')))

        assert '401' in str(client.post('/{}'.format(route),
                                        data=dict(text="",
                                                  team_id='wrong-test-team-id',
                                                  token='wrong-test-token',
                                                  user_id='asdf')))
