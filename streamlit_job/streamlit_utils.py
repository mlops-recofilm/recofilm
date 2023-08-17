import requests
import os
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid

baseurl = os.environ['api_address']

res = requests.get(url=f"{baseurl}unique_genres")
genres_list = res.json()["genres"]

res = requests.get(url=f"{baseurl}unique_movies")
movies_list = res.json()["movies"]


def build_url(baseurl, endpoint, userid, genres=None, movie=None):
    if genres:
        genre_query = '&subject='.join(genres)
        return f"{baseurl}{endpoint}?user_id={userid}&subject={genre_query}&movie_name={movie}"
    else:
        return f"{baseurl}{endpoint}?user_id={userid}&movie_name={movie}" if movie else f"{baseurl}{endpoint}?user_id={userid}"


def get_response(url):
    res = requests.get(url)
    return res

def data_upload(reco_movie, reco_ids):
    return pd.DataFrame({'movie': reco_movie, 'ids': reco_ids, 'rating': ["-"] * len(reco_movie)})

def show_grid(reco_movie, reco_ids):
    df = data_upload(reco_movie, reco_ids)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_default_column(editable=False, groupable=True)
    gb.configure_column(
        "rating",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": ["0", "1", "2", "3", "4", "5"]},
    )
    gb.configure_grid_options(autoSizeColumn=True, autoHeight=True)
    gb.configure_column("ids", hide=True)

    gridOptions = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        height=500,
        fit_columns_on_grid_load=False,
        columns_auto_size_mode="FIT_CONTENTS",
        allow_unsafe_jscode=True,
        sideBar=True
    )
    return grid_response

def update(grid_table, headers):
    movies_id = grid_table["data"].loc[grid_table["data"]["rating"] != "-"].to_dict(orient="list")
    post_data = {"movieid": movies_id["ids"], "rating": movies_id["rating"]}
    res = requests.post(url=f"{baseurl}addRating", json=post_data, headers=headers)