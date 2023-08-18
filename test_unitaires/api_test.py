import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path,os.pardir))
sys.path.insert(0,parent_dir_path)

import pytest
import requests
from fastapi.testclient import TestClient
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from requests.auth import HTTPBasicAuth
import time


def test_api_starting():
    """check if the API is running."""
    url = 'http://127.0.0.1:8000'
    response = requests.get(url)

    assert response.status_code == 200
    assert response.json() == {"message": "API is up and running"}


def test_api_unique_genre():
    """check if the list of unique movies genres is not empty"""
    url = 'http://127.0.0.1:8000/unique_genres'
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json() != None


def test_api_unique_movies():
    """check if the list of unique movies genres is not empty"""
    url = 'http://127.0.0.1:8000/unique_movies' 
    response = response = requests.get(url)
    assert response.status_code == 200
    assert response.json() != None

def test_api_get_random():
    """check if the api gives always a random movie with an user known"""
    url = 'http://127.0.0.1:8000/random?user_id=1644'
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json() != {'message': 'no movie for you:('}

def test_api_movie_model():
    """check if the api_movie_model gives always a movie advised by the model movie with an user and a movie known:
    user_id : 1644
    movie : Star Wars: Episode IV - A New Hope (1977) """

    url = 'http://127.0.0.1:8000/movie_model?user_id=1644&subject=Adventure&movie_name=Star%20Wars%3A%20Episode%20IV%20-%20A%20New%20Hope%20%281977%29'
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json() != {'message': 'no movie for you:('}

def test_api_user_model():
    """ check if the api_user_model gives always a movie advised by the model movie with an user and a movie known:
    user_id : 1644"""
    url = 'http://127.0.0.1:8000/user_model?user_id=1644'
    response = requests.get(url)
    assert response.status_code == 200
    assert response.json() != {'message': 'no movie for you:('}


def  test_api_reminder_1():
   """ check the security of the api_reminder """
   url = 'http://127.0.0.1:8000/remindMe/10'
   basic = HTTPBasicAuth('fake_user','fake_password')
   response = requests.get(url,auth=basic)
   assert response.status_code == 401
   
def  test_api_reminder_2():
   """ check if api_reminder gives 10 movies with k = 10 (parameter) and userId = 1644 """
   url = 'http://127.0.0.1:8000/remindMe/10'
   basic = HTTPBasicAuth('1644','fds')
   response = requests.get(url,auth=basic)
   assert response.status_code == 200
   assert len(response.json().get('movie')) == 10
