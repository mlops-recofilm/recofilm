
from enum import Enum
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, HTTPException, Response, status, Depends, Header, Query
import json
from typing import List, Optional, Annotated
# from pydantic import BaseModel
import pandas as pd
import random
import uvicorn

from utils import *


app = FastAPI(
    title="Reco API",
    description="The Reco API is designed to provide a simple interface to recommande movies to an user based on various criteria.",
    version="1.0.1",
    openapi_tags=[
        {
            'name': 'home',
            'description': 'default functions'
        },
        {
            'name': 'model',
            'description': 'model available'
        }
    ]
)

data = get_data()

GenreEnum = get_GenreEnum(data)

# Route de base pour vérifier le fonctionnement de l'API
@app.get("/", tags=['home'])
def read_root():
    """
     Returns a JSON response with a message indicating that the API is up and running.

    Returns:
        dict: A dictionary containing a message key with the value "API is up and running".
    """
    return {"message": "API is up and running"}


@app.get("/random", tags=['model'])
def random_output(query_params: dict = Depends(query_params)):
# def random_output(userid: Annotated[str, Depends(get_user_credentials)], query_params: dict = Depends(query_params)):    
    if query_params['subject']:
        unseen_movies = get_unseen_movies(query_params['user_id'], data)
    else:
        unseen_movies = get_unseen_movies(query_params['user_id'], data)
    random_movie = random.choice(unseen_movies)
    return {"movie": random_movie}


@app.get("/remindMe/{k}", tags=['historical'])
def remind_reco(k: int, userid: Annotated[str, Depends(get_user_credentials)]) -> List[str]:
    """Remind last k unique recommended movies"""

    with open ("../data/outputs/predictions_history.json", "r") as f:
        recommended_movies = json.loads(f.read())

    list_movies = recommended_movies[userid]['movies']
    j=k
    last_unique_k = []
    while len(last_unique_k) < k and j < len(list_movies):
        last_unique_k = list(set(list_movies[-j:]))
        j += 1
    return last_unique_k


@app.post("/addRating", tags=['add data'])
def add_rating(movieid: str, rating: float, userid: Annotated[str, Depends(get_user_credentials)]) -> bool:
    success = add_ratings(userid, movieid, rating)
    return success


@app.get("/bestMoviesByGenre", tags=['add data'])
def get_best_movies_by_genre(genre: GenreEnum, userid: Annotated[str, Depends(get_user_credentials)]) -> List[str]:
    top_movies_by_genre = data[data['genres'].str.contains(genre.value)]\
                               .sort_values('rating', ascending=False)\
                                .head(10)[['movieId','title']]
    top_movies_by_genre_dict = top_movies_by_genre.to_dict('split')['data']
    top_movies_by_genre_list = [f'{i[1]} (id = {i[0]})' for i in top_movies_by_genre_dict]
    print(top_movies_by_genre_list)
    return top_movies_by_genre_list


@app.post("/createUser", tags=['add data'])
def create_user(new_ratings: RatingsItem) -> int:
    """Creates a new user by adding
    Returns freshly created user id."""
    # make sure to have the latest version of data
    data = get_data()

    new_userId = int(data.userId.max()) + 1
    #TODO how to manage possible multiple edits of the file ? lock it ?

    # check that there are at least MIN_N_RATINGS_NEW_USER movie ratings provided
    if len(set(new_ratings.movieid)) != len(set(new_ratings.rating)) \
        or len(set(new_ratings.movieid)) < MIN_N_RATINGS_NEW_USER \
            or len(set(new_ratings.movieid)) != len(new_ratings.movieid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 3 unique movies (ids) should be provided with their corresponding ratings",
        )
    
    for movieid in new_ratings.movieid:
        if movieid not in data.movieId.unique():
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Movie with id {movieid} doesn't exist, please enter an existing movie",
        )

    #TODO add userid to db

    # add new ratings
    add_ratings(userid=new_userId, movieids=new_ratings.movieid, ratings=new_ratings.rating)
    return new_userId
