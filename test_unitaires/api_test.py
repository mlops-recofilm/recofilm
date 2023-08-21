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

def get_data_mock():
    """
    Load and prepare the movie ratings data for unit test.
    Returns:
        tuple: A tuple containing the movie ratings data DataFrame, movie data sparse CSR matrix,
               user data sparse CSR matrix, and a dictionary mapping movie titles to IDs.
    """
    data = pd.DataFrame([[1,3.5,1644,
                           'Adventure|Animation|Children|Comedy|Fantasy','Toy Story (1995)'],
                           [2122,3.0,13494,'Horror|Thriller','Children of the Corn (1984)']],
                           index=['1','2'],
                           columns=['movieId','rating','userId','genres','title'])
    df = data[['movieId', 'rating', 'userId']].drop_duplicates()
    rating_matrix = df.pivot(index='movieId', columns='userId', values='rating').fillna(0)
    movie_data = csr_matrix(rating_matrix.values)
    user_data = df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
    title_dict = pd.Series(data.movieId.values, index=data.title).to_dict()
    return data, movie_data, user_data, title_dict

mock_data,mock_movie_data,mock_user_data,mock_title_dict_data = get_data_mock()

print(mock_data)


client = TestClient(app)


def test_api_starting():
    """Test if the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is up and running"}

def test_unique_genres():
    """test if the list of unique movies genres is not empty"""
    with patch('api.api.data',mock_data):
        response = client.get("/unique_genres")
        assert response.status_code == 200
        assert response.json() != None

def test_unique_movies():
    """test if the list of unique movies genres is not empty"""
    with patch('api.api.data',mock_data):
        response = client.get("/unique_movies")
        assert response.status_code == 200
        assert response.json() != None


def test_random_output():
    """test if random_output gives always a random movie with an user known"""
    with patch('api.api.data',mock_data):
        with patch('api.api.title_dict',mock_title_dict_data):
            response = client.get("/random",params={'user_id':'1644'})
            assert response.status_code == 200
            assert response.json() == {'ids': 2122, 'message': 'ok', 'movie': ['Children of the Corn (1984)']}
            

def test_api_reminder():
    """ test the security of the api_reminder """
    response = client.get("/remindMe",params={'k':10},headers={"Authorization": "fake"})
    assert response.status_code == 404


