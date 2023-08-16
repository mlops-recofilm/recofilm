import base64
import json
import os

import pandas as pd
import requests
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
from yaml.loader import SafeLoader

from utils.path import output_folder

baseurl = os.environ['api_address']

st.set_page_config(layout="wide", page_title="Movie recommender")

with open(os.path.join(output_folder, 'config.yaml')) as file:
    config = yaml.load(file, Loader=SafeLoader)

res = requests.get(url=f"{baseurl}unique_genres")
genres_list = res.json()["genres"]

res = requests.get(url=f"{baseurl}unique_movies")
movies_list = res.json()["movies"]

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

def build_url(baseurl, endpoint, userid, genres=None, movie=None):
    if genres:
        genre_query = '&subject='.join(genres)
        return f"{baseurl}{endpoint}?user_id={userid}&subject={genre_query}&movie_name={movie}"
    else:
        return f"{baseurl}{endpoint}?user_id={userid}&movie_name={movie}" if movie else f"{baseurl}{endpoint}?user_id={userid}"

def get_response(url):
    res = requests.get(url)
    return res


with open(os.path.join(output_folder, "mapping_username_user_id.json"), "r") as f:
    mapping_userid = json.loads(f.read())

if authentication_status:
    authenticator.logout('Logout', 'main')

    st.title(f"Welcome *{name}* to your Personalized Movie Recommendations!")
    st.write("Hello there, Movie Enthusiast!")
    st.write(
        "Welcome to our personalized movie recommendation experience. We're excited to help you discover your next favorite film. Here's a quick guide to get you started:")
    st.write(
        "1. **User Model:** With this option, we tailor recommendations based on your unique preferences and past predictions. It's like having your very own movie oracle!")
    st.write(
        "2. **Movie Model:** Feeling adventurous? Choose a specific movie, and we'll suggest similar titles that are right up your alley.")
    st.write(
        "3. **Random Model:** Ready for a surprise? Try our random movie recommendations. You never know what cinematic gem you might uncover!")
    st.write(
        "**Genre Selection:** Don't forget to select your favorite genres. Whether you're into action-packed thrillers, heartwarming comedies, captivating dramas, or mind-bending sci-fi, we've got you covered.")
    st.write(
        "**Remind Me:** Want to revisit your previous predictions? Use the slider to choose how many recommendations you'd like us to remind you of.")
    st.write(
        "**Let's Get Started:** Dive in by selecting a model, picking your preferred genres, and exploring the world of movies that await you. Don't hesitate to click the 'Random movie' button or choose a specific movie to see what we have in store for you.")
    st.write("Lights, camera, action! 🍿🎬")
    if username not in mapping_userid:
        block_refresh = False
        res = requests.post(url=f"{baseurl}createUser")
        userid = int(res.json()['id'])
        mapping_userid[username] = str(userid)
        password = ""  # Laissez le mot de passe vide

        # Encodez le nom d'utilisateur et le mot de passe en Base64
        credentials = f"{userid}:{password}"
        base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        headers = {
            "accept": "application/json",
            "Authorization": f"Basic {base64_credentials}"
        }
        st.write('As a new user, please fill the form below')
        genres = st.multiselect('Choose your three favorites genres', genres_list, max_selections=3)
        movies_list_to_choose = []
        ids_list_to_choose = []
        for g in genres:
            res = requests.get(
                url=f"{baseurl}bestMoviesByGenre?genre={g}", headers=headers)
            movies_list_to_choose.extend(res.json()['movies'])
            ids_list_to_choose.extend(res.json()['ids'])
        title_to_id = dict(zip(movies_list_to_choose, ids_list_to_choose))
        movies_selected = st.multiselect('Choose your favorites movies', movies_list_to_choose)
        sublist_ids = [title_to_id[title] for title in movies_selected]
        if st.button('Validate my choice'):
            post_data = {"movieid": sublist_ids, "rating": [5] * len(sublist_ids)}
            res = requests.post(url=f"{baseurl}addRating", json=post_data, headers=headers)
            block_refresh = True

            if block_refresh:
                with open(os.path.join(output_folder, "mapping_username_user_id.json"), "w") as outfile:
                    json.dump(mapping_userid, outfile)
                st.experimental_rerun()


    else:
        msg = None
        userid = mapping_userid[username]
        password = ""  # Laissez le mot de passe vide

        # Encodez le nom d'utilisateur et le mot de passe en Base64
        credentials = f"{userid}:{password}"
        base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        headers = {
            "accept": "application/json",
            "Authorization": f"Basic {base64_credentials}"
        }
        with st.sidebar:
            reminde_me = st.slider('Reminde me my last predictions', 0, 20, 0)
            type_model = st.selectbox(
                "Choose your model",
                ('Movie model', 'User model', 'Random movie'))
            genres = st.multiselect('Choose your genre', genres_list)
            if type_model == 'Movie model':
                movie = st.selectbox(
                    'Choose a movie',
                    movies_list)
            if st.button('Validate my choices'):
                if type_model == 'Movie model':
                    endpoint = 'movie_model'
                    url = build_url(baseurl, endpoint, userid, genres, movie)
                elif type_model == 'User model':
                    endpoint = 'user_model'
                    url = build_url(baseurl, endpoint, userid, genres)
                else:
                    endpoint = 'random'
                    url = build_url(baseurl, endpoint, userid, genres)
                res = get_response(url)
                if res.json()['message'] == 'ok':
                    reco_movie = res.json()["movie"]
                    reco_ids = res.json()["ids"]
                else:
                    msg = "We don't find a movie for you based on your choices"

            if reminde_me > 0:
                res = requests.get(f"{baseurl}remindMe/{reminde_me}", headers=headers)
                reco_movie = res.json()["movie"]
                reco_ids = res.json()["ids"]
            try:
                reco_movie = res.json()["movie"]
                reco_ids = res.json()["ids"]
            except:
                pass


        def data_upload():
            try:
                df = pd.DataFrame({'movie': reco_movie, 'ids': reco_ids, 'rating': ["-"] * len(reco_movie)})
            except:
                df = pd.DataFrame({'movie': [''], 'ids': [''], 'rating': None})
            return df


        def show_grid():
            js_code = JsCode("""
                class UrlCellRenderer {
                  init(params) {
                    this.eGui = document.createElement('a');
                    this.eGui.innerText = params.value.split('/').pop();
                    this.eGui.setAttribute('href', params.value);
                    this.eGui.setAttribute('style', "text-decoration:none");
                    this.eGui.setAttribute('target', "_blank");
                  }
                  getGui() {
                    return this.eGui;
                  }
                }
            """)

            df = data_upload()
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


        def update(grid_table):
            movies_id = grid_table["data"].loc[grid_table["data"]["rating"] != "-"].to_dict(orient="list")
            post_data = {"movieid": movies_id["ids"], "rating": movies_id["rating"]}
            res = requests.post(url=f"{baseurl}addRating", json=post_data, headers=headers)


        if msg:
            st.write(msg)
        else:
            grid_table = show_grid()
            st.button("Update", on_click=update, args=[grid_table])


elif authentication_status == False:
    with st.expander("Register New User"):
        try:
            if authenticator.register_user("Register user", preauthorization=False):
                st.success("User registered successfully")
        except Exception as e:
            st.error(e)

        with open(os.path.join(output_folder, 'config.yaml'), "w") as file:
            yaml.dump(config, file, default_flow_style=False)
    st.error('Username/password is incorrect')
elif authentication_status == None:
    with st.expander("Register New User"):
        try:
            if authenticator.register_user("Register user", preauthorization=False):
                st.success("User registered successfully")
        except Exception as e:
            st.error(e)

        with open(os.path.join(output_folder, 'config.yaml'), "w") as file:
            yaml.dump(config, file, default_flow_style=False)
    st.warning('Please enter your username and password')
