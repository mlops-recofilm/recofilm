from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, HTTPException, Response, status, Depends, Header, Query
import json
from typing import List, Optional, Annotated
from pydantic import BaseModel
import pandas as pd
import random
import uvicorn


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
security = HTTPBasic()

data = pd.read_csv('../ml-20m/final.csv')

def get_user_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    """Checks user's credentials - authentification_dict is used as a user database.
    """
    # check that credentials.username exists - in DB ?
    existing_users = data['userId'].unique()
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

# Route de base pour vérifier le fonctionnement de l'API
@app.get("/", tags=['home'])
def read_root():
    """
     Returns a JSON response with a message indicating that the API is up and running.

    Returns:
        dict: A dictionary containing a message key with the value "API is up and running".
    """
    return {"message": "API is up and running"}


def get_unseen_movies(user_id, df):
    user_movies = df[df['userId'] == int(user_id)]['movieId'].unique()
    all_movies = df['movieId'].unique()
    unseen_movies = set(all_movies) - set(user_movies)
    unseen_movies = [int(movie) for movie in list(unseen_movies)]
    return unseen_movies


@app.get("/random", tags=['model'])
def random_output(query_params: dict = Depends(query_params)):
    if query_params['subject']:
        unseen_movies = get_unseen_movies(query_params['user_id'], data)
    else:
        unseen_movies = get_unseen_movies(query_params['user_id'], data)
    random_movie = random.choice(unseen_movies)
    return {"movie": random_movie}


@app.get("/remind_me/{k}/{userid}", tags=['historical'])
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

