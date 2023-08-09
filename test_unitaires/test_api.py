import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
api_folder_path = os.path.join(current_directory, '..', 'api')
sys.path.append(api_folder_path)


import pytest
import requests
from fastapi.testclient import TestClient
from api_recofilm import app
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from requests.auth import HTTPBasicAuth
import time

client = TestClient(app)

def test_api_starting():
    """Test if the API is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is up and running"}
import base64
credentials = "1644:"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
auth_string = f"Basic {encoded_credentials}"

def test_bestMoviesBygenre_2():
    response = client.get("/bestMoviesByGenre",
                          params={"genre": "Adventure"},
                          headers={"Authorization": "Basic MTY0NDo="})
    assert response.status_code == 200
    assert response.json() == ["Toy Story (1995) (id = 1)"]

def test_response_time():
    start_time = time.time() 

    response = client.get("/")  

    elapsed_time = time.time() - start_time  
    assert response.status_code == 200
    assert elapsed_time < 1

def test_random_output():
    response = client.get("/random", params={"user_id": 1})
    assert response.status_code == 200
    assert 'movie' in response.json()

def test_create_user():
    response = client.post("/createUser", json={"movieid": [1, 173, 70286], "rating": [4.0, 5.0, 3.0]})
    assert response.status_code == 200

def test_create_user_less_than_min_ratings():
    response = client.post("/createUser", json={"movieid": [1, 173], "rating": [4.0, 5.0]})
    assert response.status_code == 400
    assert response.json() == {"detail": "At least 3 unique movies (ids) should be provided with their corresponding ratings"}

def test_create_user_duplicate_movies():
    response = client.post("/createUser", json={"movieid": [1, 1, 70286], "rating": [4.0, 5.0, 3.0]})
    assert response.status_code == 400
    assert response.json() == {"detail": "At least 3 unique movies (ids) should be provided with their corresponding ratings"}

def test_create_user_movie_not_exist():
    response = client.post("/createUser", json={"movieid": [9999999, 173, 70286], "rating": [4.0, 5.0, 3.0]})
    assert response.status_code == 400
    assert response.json() == {"detail": "Movie with id 9999999 doesn't exist, please enter an existing movie"}

