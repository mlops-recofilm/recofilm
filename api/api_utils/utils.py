from datetime import datetime
import os
import json
from enum import Enum
from fastapi import FastAPI, HTTPException, status, Depends, Header, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional, Annotated
from scipy.sparse import csr_matrix
from utils.path import data_folder, output_folder, input_data_folder


DATA_PATH = os.path.join(data_folder,'data_api.csv')
MIN_N_RATINGS_NEW_USER = 3

security = HTTPBasic()


def load_ratings():
    filename = os.path.join(input_data_folder, 'ratings_updated.csv')
    if os.path.exists(filename):
        ratings_df = pd.read_csv(filename)
    else:
        ratings_df = pd.read_csv(os.path.join(input_data_folder, 'ratings.csv'))
    return ratings_df, filename

ratings_df, filename = load_ratings()

def get_data(data_path=DATA_PATH):
    """
    Load and prepare the movie ratings data.

    Args:
        data_path (str): The path to the movie ratings data CSV file.

    Returns:
        tuple: A tuple containing the movie ratings data DataFrame, movie data sparse CSR matrix,
               user data sparse CSR matrix, and a dictionary mapping movie titles to IDs.
    """
    data = pd.read_csv(data_path)
    df = data[['movieId', 'rating', 'userId']].drop_duplicates()
    rating_matrix = df.pivot(index='movieId', columns='userId', values='rating').fillna(0)
    movie_data = csr_matrix(rating_matrix.values)
    user_data = df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
    title_dict = pd.Series(data.movieId.values, index=data.title).to_dict()
    return data, movie_data, user_data, title_dict


def get_user_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    """
    Validate user credentials.

    Args:
        credentials (HTTPBasicCredentials): The HTTP basic authentication credentials.

    Returns:
        str: The validated user ID.
    """
    data, _, _, _ = get_data()
    next_new_userid_filepath = os.path.join(output_folder, "next_new_userid")
    # check that credentials.username exists in DB
    existing_users = list(data['userId'].astype(str).unique())
    if os.path.exists(next_new_userid_filepath):
        mode = "r+"
        with open(next_new_userid_filepath, mode) as next_new_userid_file:  # "r+"
            next_new_userid = next_new_userid_file.read()
            next_new_userid = int(next_new_userid)
            if next_new_userid>data['userId'].max():
                other_user = [str(x) for x in range(data['userId'].max(), next_new_userid + 1)]
                existing_users.extend(other_user)

    if not (credentials.username in existing_users):
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
    Parse and return query parameters.

    Args:
        user_id (str): The user ID.
        subject (Optional[List[str]]): An optional list of subject strings to filter genres by.
        movie_name (Optional[str]): An optional movie name.

    Returns:
        Dict[str, Union[str, List[str]]]: A dictionary containing the parsed query parameters.
    """
    return {"user_id": user_id, "subject": subject, 'movie_name': movie_name}


def get_GenreEnum(df) -> Enum:
    """
    Generate an enumeration for possible values of genre.

    Args:
        df (pd.DataFrame): The movie ratings data DataFrame.

    Returns:
        Enum: An enumeration containing genre values.
    """
    genres_set = []
    for genres in df['genres'].unique():
        genres_set.extend(genres.split('|'))
    GenreEnum = Enum('GenreEnum', {f'genre{i}': genre for i, genre in enumerate(genres_set)})
    return GenreEnum


def get_unseen_movies(df, user_id, genres):
    """
    Get a list of unseen movies for a user.

    Args:
        df (pd.DataFrame): The movie ratings data DataFrame.
        user_id (str): The user ID.
        genres (List[str]): A list of genres to filter movies by.

    Returns:
        List[int]: A list of movie IDs that are unseen by the user.
    """
    if genres:
        for g in genres:
            df = df.loc[(df['genres'].str.contains(g))]
    user_movies = df[df['userId'] == int(user_id)]['movieId'].unique()
    all_movies = df['movieId'].unique()
    unseen_movies = set(all_movies) - set(user_movies)
    unseen_movies = [int(movie) for movie in list(unseen_movies)]
    return unseen_movies


class RatingsItem(BaseModel):
    """
    Represents new movie ratings provided by a user.
    """
    movieid: List[int]
    rating: List[float] = [5]


def add_ratings(userid: str, movieids: List[str], ratings: List[float]):
    """
    Add new movie ratings for a user.

    Args:
        userid (str): The user ID.
        movieids (List[str]): A list of movie IDs.
        ratings (List[float]): A list of movie ratings.
        file_path (str): The file path for storing the new ratings data.

    Returns:
        bool: True if the ratings were added successfully, False otherwise.
    """
    global ratings_df
    timestamp = int(datetime.now().timestamp())
    new_ratings_data = {
        "userId": [userid] * len(movieids),
        "movieId": movieids,
        "rating": ratings,
        "timestamp": [timestamp] * len(movieids)
    }
    new_ratings_df = pd.DataFrame(new_ratings_data)
    ratings_df = pd.concat([ratings_df, new_ratings_df], ignore_index=True)
    ratings_df.to_csv(filename, index=False)
    return True


def save_reco(user_id: int, movie_id: int):
    """
    Save movie recommendations for a user in a JSON file.

    Args:
        user_id (int): The user's identifier.
        movie_id (int): The identifier of the recommended movie.

    Returns:
        None
    """
    with open(os.path.join(output_folder,"predictions_history.json"), "r") as f:
        recommended_movies = json.loads(f.read())
    if str(user_id) in recommended_movies:
        if len(recommended_movies[str(user_id)])>20:
            recommended_movies[str(user_id)]['dates'] = recommended_movies[str(user_id)]['dates'][1:]
            recommended_movies[str(user_id)]['movies'] = recommended_movies[str(user_id)]['movies'][1:]
        recommended_movies[str(user_id)]['movies'].append(movie_id)
        recommended_movies[str(user_id)]['dates'].append(datetime.now().strftime("%m/%d/%Y"))
    else:
        recommended_movies[str(user_id)] = {"dates": [datetime.now().strftime("%m/%d/%Y")],
                                            "movies":[movie_id]}
    with open(os.path.join(output_folder,"predictions_history.json"), "w") as json_file:
        json.dump(recommended_movies, json_file)
