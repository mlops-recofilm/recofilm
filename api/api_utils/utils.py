from datetime import datetime
import os
from enum import Enum
from fastapi import FastAPI, HTTPException, status, Depends, Header, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional, Annotated
from scipy.sparse import csr_matrix
import sys
sys.path.append('..')
from utils.path import data_folder


DATA_PATH = os.path.join(data_folder,'data_api.csv')
MIN_N_RATINGS_NEW_USER = 3

security = HTTPBasic()


def get_data(data_path=DATA_PATH):
    data = pd.read_csv(data_path)
    df = data[['movieId', 'rating', 'userId']].drop_duplicates()
    rating_matrix = df.pivot(index='movieId', columns='userId', values='rating').fillna(0)
    movie_data = csr_matrix(rating_matrix.values)
    rating_matrix = df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
    user_data = csr_matrix(rating_matrix.values)
    title_dict = pd.Series(data.movieId.values, index=data.title).to_dict()
    return data, movie_data, user_data, title_dict


def get_user_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    """Checks user's credentials - authentification_dict is used as a user database.
    """
    data = get_data()
    # check that credentials.username exists in DB
    existing_users = data['userId'].unique()
    if not (int(credentials.username) in existing_users):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username", #  or password
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


async def query_params(
    user_id: str,
    subject: Optional[List[str]] = Query(None),
    movie_name: Optional[str] = None,
):
    """
    Returns a dictionary containing the given `use` parameter and an optional `subject` list.

    Args:
        user_id : str
            The user_id
        subject : Optional[List[str]], default=None
            An optional list of subject strings to filter genres by.
        movie_name : Optional[str], default=None
            An optional str of movie.
    Returns:
        Dict[str, Union[str, List[str]]]
            A dictionary containing the given `use` and optional `subject` parameters.
    """
    return {"user_id": user_id, "subject": subject, 'movie_name': movie_name}


def get_GenreEnum(df) -> Enum:
    """Enumeration for possible values of genre"""
    genres_set = []
    for genres in df['genres'].unique():
        genres_set.extend(genres.split('|'))
    GenreEnum = Enum('GenreEnum', {f'genre{i}': genre for i, genre in enumerate(genres_set)})
    return GenreEnum


def get_unseen_movies(df, user_id, genres):
    if genres:
        df = df.loc[(df['genres'].str.contains('|'.join(genres)))]
    user_movies = df[df['userId'] == int(user_id)]['movieId'].unique()
    all_movies = df['movieId'].unique()
    unseen_movies = set(all_movies) - set(user_movies)
    unseen_movies = [int(movie) for movie in list(unseen_movies)]
    return unseen_movies


class RatingsItem(BaseModel):
    """New question structure"""
    movieid: List[int]
    # title: str # letting users input movie if only
    rating: List[float] = [5]


def add_ratings(userid: str, movieids: List[str], ratings: List[float], file_path = '../ml-20m/'):
    if not isinstance(movieids, list): movieids = [movieids]
    if not isinstance(ratings, list): ratings = [ratings]

    timestamp = int(datetime.now().timestamp())
    filename = file_path + f'ratings_{timestamp}.csv'

    new_ratings_df = pd.DataFrame({
        "userId": userid,
        "movieId": movieids,
        "rating": ratings,
        "timestamp": timestamp
    })
    new_ratings_df.to_csv(filename, index=False)
    return True
