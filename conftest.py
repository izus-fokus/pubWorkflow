import pytest
import json
import sys
from pubworkflowApi import app, Publication


def pytest_addoption(parser):
    parser.addoption('--apikey', action='store', default='<add Dataverse API-Key>', help='add Dataverse API-Key')
    parser.addoption('--apiurl', action='store', default='http://localhost:8080', help='add Dataverse API-URL')


@pytest.fixture(scope='session')
def pub():
    pub = Publication()
    return pub


@pytest.fixture(scope='session')
def client():
    app.testing = True
    client = app.test_client()
    return client


@pytest.fixture(scope='session')
def credentials():
    with open("cred/credentials.json", "r") as cred_file:
        credentials = json.load(cred_file)
        credentials["darus"]["apiKey"] = sys.argv[1][len("--apikey="):]
        credentials["darus"]["apiBaseUrl"] = sys.argv[2][len("--apiurl="):]
        return credentials
