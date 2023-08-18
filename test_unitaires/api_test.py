import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path,os.pardir))
sys.path.insert(0,parent_dir_path)

import pandas as pd
import pytest
import requests
from fastapi.testclient import TestClient
from api.api import app
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from requests.auth import HTTPBasicAuth
import time

import base64
credentials = '1644'
encoded_credentials = base64.b64encode(b"1644").decode()
auth_string = f"Basic {encoded_credentials}"

client = TestClient(app)

print(encoded_credentials)


def test_api_starting():
    """Test if the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is up and running"}

