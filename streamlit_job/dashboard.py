import base64
import json
import os

import pandas as pd
import requests
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_utils import genres_list, movies_list, build_url, get_response, update, show_grid

from utils.path import output_folder

baseurl = os.environ['api_address']

st.set_page_config(layout="wide", page_title="Movie recommender")

with open(os.path.join(output_folder, 'config.yaml')) as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')


def call_remind():
    if st.session_state.k_reminde_me > 0:
        res = requests.get(f"{baseurl}remindMe/{st.session_state.k_reminde_me}", headers=headers)
        st.session_state.reco_movie = res.json()["movie"]
        st.session_state.reco_ids = res.json()["ids"]
        st.session_state.msg = None

def call_model():
    if st.session_state.type_model == 'Movie model':
        endpoint = 'movie_model'
        url = build_url(baseurl, endpoint, userid, st.session_state.genre, st.session_state.movie)
    elif st.session_state.type_model == 'User model':
        endpoint = 'user_model'
        url = build_url(baseurl, endpoint, userid, st.session_state.genre)
    else:
        endpoint = 'random'
        url = build_url(baseurl, endpoint, userid,st.session_state.genre)
    res = get_response(url)
    if res.json()['message'] == 'ok':
        st.session_state.reco_movie = res.json()["movie"]
        st.session_state.reco_ids = res.json()["ids"]
        st.session_state.msg = None
    else:
        st.session_state.msg = "We don't find a movie for you based on your choices"
        st.session_state.reco_movie = ['']
        st.session_state.reco_ids = ['']


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
        if "k_reminde_me" not in st.session_state:
            # set the initial default value of the slider widget
            st.session_state.k_reminde_me = 0
        if 'reco_movie' not in st.session_state:
            st.session_state.reco_movie = ['']
        if 'reco_ids' not in st.session_state:
            st.session_state.reco_ids = ['']
        if 'type_model' not in st.session_state:
            st.session_state.type_model = 'Movie model'
        if 'movie' not in st.session_state:
            st.session_state.movie = 'Toy Story (1995)'
        if 'genre' not in st.session_state:
            st.session_state.genre = []
        if 'msg' not in st.session_state:
            st.session_state.msg = None
        with st.sidebar:
            reminde_me = st.slider('Reminde me my last predictions', 0, 20, 0, on_change=call_remind, key="k_reminde_me")
            if st.session_state.k_reminde_me == 0:
                type_model = st.selectbox("Choose your model", ('Movie model', 'User model', 'Random movie'), key="type_model", on_change=call_model)
                genre = st.multiselect('Choose your genre', genres_list, key="genre", on_change=call_model)
                if st.session_state.type_model == 'Movie model':
                    movie = st.selectbox('Choose a movie', movies_list, key='movie', on_change=call_model)

        if st.session_state.msg:
            st.write(st.session_state.msg)

        grid_table = show_grid(st.session_state.reco_movie, st.session_state.reco_ids)
        st.button("Update", on_click=update, args=[grid_table, headers])


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
