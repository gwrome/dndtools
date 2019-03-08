import os

import pytest

from dndtools import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test"""
    app = create_app({
        'TESTING': True,
        'SLACK_VERIFICATION_TOKEN': 'test-token',
        'SLACK_TEAM_ID': 'test-team-id',
        'SECRET_KEY': 'flask-secret-key',
        'DYNAMO_ENABLE_LOCAL': True,
        'DYNAMO_LOCAL_HOST': 'localhost',
        'DYNAMO_LOCAL_PORT': 8000,
    })

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
