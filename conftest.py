import os
import logging
import pytest
import requests
from api.booking_api import BookingAPI

pytest_plugins = ["runner.runner_plugin"]


base_url = 'https://restful-booker.herokuapp.com'


@pytest.fixture(scope='session')
def credentials():
    username = os.getenv('BOOKER_USERNAME')
    password = os.getenv('BOOKER_PASSWORD')
    if not username or not password:
        pytest.fail('BOOKER_USERNAME/BOOKER_PASSWORD env vars are not set.')
    return {'username': username, 'password': password}

@pytest.fixture(scope='session')
def booking_api(endpoint_health_check, credentials):
    booking_api = BookingAPI(base_url, credentials['username'],credentials['password'])
    booking_api.create_token()
    yield booking_api
    booking_api.close_session()

@pytest.fixture(scope='session')
def endpoint_health_check():
    url = f'{base_url}/ping'
    response = requests.get(url)
    print(response.text)
    if response.status_code != 201 and response.text != 'Created':
        pytest.fail('Health check failed exiting testcases.')


@pytest.fixture
def context():
    return {}



