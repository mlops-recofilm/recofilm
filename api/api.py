import sys,os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path,os.pardir))
sys.path.insert(0,parent_dir_path)
sys.path.insert(0,'../api')

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, HTTPException, Response, status, Depends, Header, Query
import json
import os
import numpy as np
import random
from joblib import load
from utils.path import model_folder, output_folder
from api_utils.utils import *


data, movie_data, user_data, title_dict = get_data()


def get_next_new_userid():
    """
    Get the next available new user ID.

    Returns:
        int: The next available new user ID.
    """
    NEXT_NEW_USERID = os.getenv('NEXT_NEW_USERID')
    if not NEXT_NEW_USERID: # variable not defined
        NEXT_NEW_USERID = data.userId.max() + 1
        os.environ['NEXT_NEW_USERID'] = str(NEXT_NEW_USERID)
    return NEXT_NEW_USERID


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
app.state.NEW_USERID = -1

GenreEnum = get_GenreEnum(data)


@app.get("/", tags=['home'])
def read_root():
    """
     Returns a JSON response with a message indicating that the API is up and running.

    Returns:
        dict: A dictionary containing a message key with the value "API is up and running".
    """
    return {"message": "API is up and running"}


@app.get("/unique_genres", tags=['utils'])
def unique_genres():
    """
    Get the list of unique movie genres.

    Returns:
        dict: A dictionary containing a key 'genres' with a list of unique movie genres.
    """
    all_genres = data['genres'].str.split('|', expand=True).stack().tolist()
    unique_genres = sorted(set(all_genres))
    return {"genres": unique_genres}


@app.get("/unique_movies", tags=['utils'])
def unique_movies():
    """
    Get the list of unique movie titles.

    Returns:
        dict: A dictionary containing a key 'movies' with a list of unique movie titles.
    """
    all_movies = data['title'].unique().tolist()
    return {"movies": all_movies}


@app.get("/random", tags=['model'])
def random_output(query_params: dict = Depends(query_params)):
    """
    Generate a random movie recommendation for a user.

    Args:
        query_params (dict): The query parameters containing 'user_id' and 'subject'.

    Returns:
        dict: A dictionary containing a key 'movie' with the recommended movie title.
    """
    unseen_movies = get_unseen_movies(data, query_params['user_id'], query_params['subject'])
    try:
        random_movie = random.choice(unseen_movies)
        print(random_movie)
        save_reco(int(query_params['user_id']), random_movie)
        return {"movie": [k for k, v in title_dict.items() if v == random_movie], 'ids': random_movie, 'message': 'ok'}
    except IndexError:
        return {'message': 'No movie for you :('}


@app.get("/movie_model", tags=['model'])
def movie_model(query_params: dict = Depends(query_params)):
    """
    Generate a random movie recommendation using the movie recommendation model.

    Args:
        query_params (dict): The query parameters containing 'user_id' and 'movie_name'.

    Returns:
        dict: A dictionary containing a key 'movie' with the recommended movie title.
    """
    model = load(os.path.join(model_folder, 'movie_model.joblib'))
    movie_id = title_dict[query_params['movie_name']]
    distances, indices = model.kneighbors(movie_data[movie_id], n_neighbors=50)
    unseen_movies = get_unseen_movies(data[data['movieId'].isin(indices[0])], query_params['user_id'], query_params['subject'])
    try:
        random_movie = random.choice(unseen_movies)
        save_reco(int(query_params['user_id']), random_movie)
        return {"movie": [k for k, v in title_dict.items() if v == random_movie], 'ids': random_movie, 'message': 'ok'}
    except IndexError:
        return {'message': 'No movie for you :('}


@app.get("/user_model", tags=['model'])
def user_model(query_params: dict = Depends(query_params)):
    """
    Generate a movie recommendation using the user recommendation model.

    Args:
        query_params (dict): The query parameters containing 'user_id' and 'subject'.

    Returns:
        dict: A dictionary containing a key 'movie' with the recommended movie title and 'ids' with the movie IDs.
    """
    model = load(os.path.join(model_folder, 'user_model.joblib'))
    distances, indices = model.kneighbors(user_data[user_data.index == int(query_params['user_id'])],
                                          n_neighbors=15 + 1)
    similar_user_list = []
    for i in range(1, len(distances[0])):
        user = user_data.index[indices[0][i]]
        similar_user_list.append(user)
    indices = indices.flatten()[1:]
    weightage_list = distances.flatten()[1:] / np.sum(distances.flatten()[1:])
    similar_user_list.append(int(query_params['user_id']))
    mov_rtngs_sim_users = user_data.values[indices]
    movies_list = user_data.columns
    weightage_list = weightage_list[:, np.newaxis] + np.zeros(len(movies_list))
    new_rating_matrix = weightage_list * mov_rtngs_sim_users
    mean_rating_list = new_rating_matrix.sum(axis=0)
    n = min(len(mean_rating_list), 100)
    movies_ids = list(movies_list[np.argsort(mean_rating_list)[::-1][:n]])
    unseen_movies = get_unseen_movies(data[data['movieId'].isin(movies_ids)],query_params['user_id'], query_params['subject'])
    try:
        random_movie = random.choice(unseen_movies)
        save_reco(int(query_params['user_id']), random_movie)
        return {"movie": [k for k, v in title_dict.items() if v == random_movie], 'ids': random_movie, 'message': 'ok'}
    except IndexError:
        return {'message': 'No movie for you :('}


@app.get("/remindMe/{k}", tags=['historical'])
def remind_reco(k: int, userid: Annotated[str, Depends(get_user_credentials)]):
    """
    Get the last k unique recommended movies for a user.

    Args:
        k (int): The number of unique recommended movies to retrieve.
        userid (str): The user ID.

    Returns:
        Dict[str, List[str]]: A dictionary containing a list of last unique recommended movie titles.
    """

    with open(os.path.join(output_folder,"predictions_history.json"), "r") as f:
        recommended_movies = json.loads(f.read())
    list_movies = recommended_movies[str(userid)]['movies']
    j=k
    last_unique_k = []
    while len(last_unique_k) < k or len(list(set(list_movies[-j:])))==0:
        last_unique_k = list(set(list_movies[-j:]))
        j += 1
    filtered_titles = [title for title, movie_id in title_dict.items() if movie_id in last_unique_k]
    return {"movie": filtered_titles, 'ids': last_unique_k}


@app.post("/addRating", tags=['add data'])
def add_rating(movieid: list, rating: list, userid: Annotated[str, Depends(get_user_credentials)]) -> bool:
    """
    Add a movie rating for a user.

    Args:
        movieid (list): The list of movie IDs.
        rating (list): The list of movie ratings.
        userid (str): The user ID.

    Returns:
        bool: True if the rating was added successfully, False otherwise.
    """
    success = add_ratings(userid, movieid, rating)
    return success


@app.get("/bestMoviesByGenre", tags=['add data'])
def get_best_movies_by_genre(genre: GenreEnum):
    """
    Get the best movies of a specific genre for a user.

    Args:
        genre (GenreEnum): The movie genre.
    Returns:
        Dict[List, List]: A dictionary containing a list of top movies and a list of their associated ids.
    """
    top_movies_by_genre = data[data['genres'].str.contains(genre.value)]\
                           .groupby('movieId')['rating'].mean()\
                           .reset_index()\
                           .sort_values('rating', ascending=False)\
                           .drop_duplicates(subset='movieId')\
                           .head(10)

    top_movies_by_genre = top_movies_by_genre.merge(data[['movieId', 'title']], on='movieId')[['movieId', 'title', 'rating']]
    top_movies_by_genre.drop_duplicates(inplace = True)
    top_movies_by_genre_dict = top_movies_by_genre.to_dict('split')['data']
    top_id, top_movies_by_genre_list = zip(*[(i[0], i[1]) for i in top_movies_by_genre_dict])
    return {'movies': list(top_movies_by_genre_list), 'ids': list(top_id)}


@app.post("/createUser", tags=['add data'])
def create_user():
    """
    Create a new user.

    Returns:
        dict: A dictionary containing the newly created user's ID.
    """
    data, _, _, _ = get_data()

    next_new_userid_filepath = os.path.join(output_folder,"next_new_userid")

    # create file if doesn't exist
    if os.path.exists(next_new_userid_filepath):
        mode = "r+"
    else:
        mode = "x+"

    with open(next_new_userid_filepath, mode) as next_new_userid_file:  # "r+"
        next_new_userid = next_new_userid_file.read()
        if next_new_userid:
            next_new_userid = int(next_new_userid)
        else:
            next_new_userid = data['userId'].max() + 1
        next_new_userid_file.seek(0)
        next_new_userid_file.truncate(0)
        next_new_userid_file.write(str(next_new_userid + 1))
    return {'id': str(next_new_userid)}
  