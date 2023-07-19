from datetime import datetime
from enum import Enum
from fastapi import FastAPI, HTTPException, status, Depends, Header, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional, Annotated


DATA_PATH = '../ml-20m/final.csv'
MIN_N_RATINGS_NEW_USER = 3

security = HTTPBasic()


def get_data(data_path=DATA_PATH):
    return pd.read_csv(data_path)


def get_user_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    """Checks user's credentials - authentification_dict is used as a user database.
    """
    data = get_data()
    # check that credentials.username exists in DB
    existing_users = data['userId'].astype(str).unique()
    if not (credentials.username in existing_users): #int(
        # print(existing_users)
        # print(credentials.username, type(credentials.username))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username", #  or password
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


async def query_params(
    user_id: str,
    subject: Optional[List[str]] = Query(None),
):
    """
    Returns a dictionary containing the given `use` parameter and an optional `subject` list.

    Args:
        user_id : str
            The user_id
        subject : Optional[List[str]], default=None
            An optional list of subject strings to filter genres by.

    Returns:
        Dict[str, Union[str, List[str]]]
            A dictionary containing the given `use` and optional `subject` parameters.
    """
    return {"user_id": user_id, "subject": subject}


def get_GenreEnum(df) -> Enum:
    """Enumeration for possible values of genre"""
    genres_set = []
    for genres in df['genres'].unique():
        genres_set.extend(genres.split('|'))
    GenreEnum = Enum('GenreEnum', {f'genre{i}': genre for i, genre in enumerate(genres_set)})
    return GenreEnum


def get_unseen_movies(user_id, df):
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
