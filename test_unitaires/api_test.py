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
import base64

# Reload the api module to ensure the patch takes effect
from api.api import app
from requests.auth import HTTPBasicAuth
import time
from unittest.mock import Mock, patch

client = TestClient(app)

credentials = "1644:"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
auth_string = f"Basic {encoded_credentials}"

def test_api_starting():
    """Test if the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is up and running"}

def test_unique_genres():
    """test if the list of unique movies genres is not empty"""
    response = client.get("/unique_genres")
    assert response.status_code == 200
    assert response.json() != None

def test_unique_movies():
    """test if the list of unique movies genres is not empty"""
    response = client.get("/unique_movies")
    assert response.status_code == 200
    assert response.json() != None


def test_random_output():
    """test if random_output gives always a random movie with an user known"""
    response = client.get("/unique_genres",params={'user_id':'1644'})
    assert response.status_code == 200
    assert response.json() != {'message': 'no movie for you:('}

def test_get_movie_model():
    """test if the movie_model gives always a movie advised by the model movie with an user and a movie known"""
    response = client.get("/movie_model",params={'user_id':1644,'movie_name':'Star Wars: Episode IV - A New Hope (1977)'})
    assert response.status_code == 200
    assert response.json() != {'message': 'no movie for you:('}

def test_get_user_model():
    """ test if the user_model gives always a movie advised by the model movie with an user known"""
    response = client.get("/user_model",params={'user_id':1644})
    assert response.status_code == 200
    assert response.json() != {'message': 'no movie for you:('}


def test_api_reminder():
    """ test the security of the api_reminder """
    response = client.get("/remindMe",params={'k':10},headers={'Authentification': "fake_id"})
    assert response.status_code == 404

