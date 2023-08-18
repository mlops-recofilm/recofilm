import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path,os.pardir))
sys.path.insert(0,parent_dir_path)
from unittest.mock import MagicMock, call, mock_open, patch
import pandas as pd
import pytest
import requests
from fastapi.testclient import TestClient
from api.api import *
from fastapi import FastAPI, HTTPException, Response, status, Depends, Header, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from requests.auth import HTTPBasicAuth
import time

import base64
credentials = '1644'
encoded_credentials = base64.b64encode(b"1644").decode()
auth_string = f"Basic {encoded_credentials}"

client = TestClient(app)
mock_data = pd.DataFrame([[1,3.5,1644,
                           'Adventure|Animation|Children|Comedy|Fantasy','Toy Story (1995)']],index=['1'],columns=['movieId','rating','userId','genres','title'])


def test_api_starting():
    """Test if the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is up and running"}

def test_unique_genres():
    with patch('api.api.data', mock_data):
        result = unique_genres()

    expected_result = {'genres': ['Adventure', 'Animation','Children','Comedy', 'Fantasy']}

    assert result == expected_result

def test_unique_movies():
    with patch('api.api.data', mock_data):
        result = unique_movies()

    expected_result = {"movies":['Toy Story (1995)']}
    assert result == expected_result

def test_api_get_random():
    """check if the api gives always a random movie with an user known"""
    response = client.get('/random?user_id=1644')
    assert response.status_code == 200
    assert response.json() != {'message': 'no movie for you:('}

def test_response_time():
    start_time = time.time() 

    response = client.get("/")  

    elapsed_time = time.time() - start_time  
    assert response.status_code == 200
    assert elapsed_time < 1

def test_api_movie_model():
    """check if the api_movie_model gives always a movie advised by the model movie with an user and a movie known:
    user_id : 1644
    movie : Star Wars: Episode IV - A New Hope (1977) """
    
    response = client.get('/movie_model',params={'user_id':'1644',
                          'movie_name':'Star Wars: Episode IV - A New Hope (1977)'},
                          headers={"Authorization": "Basic MTY0NDo="})
    assert response.status_code == 200
    assert response.json() != {'message': 'no movie for you:('}

def test_api_user_model():
    """ check if the api_user_model gives always a movie advised by the model movie with an user and a movie known:
    user_id : 1644"""
    response = client.get('/user_model',params={'user_id':'1644'},
                          headers={"Authorization": "Basic MTY0NDo="})
    assert response.status_code == 200
    assert response.json() != {'message': 'no movie for you:('}