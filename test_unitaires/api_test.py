import sys
import os

#ajout pour lire les fichiers
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path,os.pardir))
sys.path.insert(0,parent_dir_path)
sys.path.append('../api')
#fin ajout
from scipy.sparse import csr_matrix
import pandas as pd
import pytest
import requests
from fastapi import Depends
from fastapi.testclient import TestClient
import importlib

# Reload the api module to ensure the patch takes effect
from api.api import app
from requests.auth import HTTPBasicAuth
import time
from unittest.mock import Mock, patch


data = pd.DataFrame([[1, 3.5, 1644,
                      'Adventure|Animation|Children|Comedy|Fantasy', 'Toy Story (1995)']],
                    index=['1'],
                    columns=['movieId', 'rating', 'userId', 'genres', 'title'])

client = TestClient(app)


def test_unique_genres():
    with patch('api.api.data', data):
        response = client.get("/unique_genres")
        result = response.json()
    expected_result = {'genres': ['Adventure', 'Animation','Children','Comedy', 'Fantasy']}

    assert result == expected_result


def test_unique_movies():
    with patch('api.api.data', data):
        response = client.get("/unique_movies")
        result = response.json()
    expected_result = {"movies":['Toy Story (1995)']}
    assert result == expected_result

