import sys
import os
sys.path.append('..')
sys.path.append('../api')
sys.path.append('../api/api_utils')
sys.path.append('../utils')



from scipy.sparse import csr_matrix
import pandas as pd
import pytest
import requests
from fastapi import Depends
from fastapi.testclient import TestClient
import importlib
import base64


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

client = TestClient(app)

def test_response_time():
    start_time = time.time()
    response = client.get("/")
    elapsed_time = time.time() - start_time
    assert response.status_code == 200
    assert elapsed_time < 1


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
        #assert response.json() != None
        assert response.json() == {"genres": ['Adventure','Animation','Children','Comedy','Fantasy','Horror','Thriller']}

def test_unique_movies():
    """test if the list of unique movies genres is not empty"""
    with patch('api.api.data',mock_data):
        response = client.get("/unique_movies")
        #assert response.status_code == 200
        assert response.json() == {"movies" : ['Toy Story (1995)','Children of the Corn (1984)']}


def test_random_output():
    """test if random_output gives always a random movie with an user known"""
    with patch('api.api.data',mock_data):
        with patch('api.api.title_dict',mock_title_dict_data):
            response = client.get("/random",params={'user_id':'1644'})
            assert response.status_code == 200
            assert response.json() == {'ids': 2122, 'message': 'ok', 'movie': ['Children of the Corn (1984)']}

