import os
import json
import sys
import pandas as pd
import requests
import streamlit as st
import streamlit_authenticator as stauth
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import logging
import yaml
from yaml.loader import SafeLoader
from utils.path import output_folder

baseurl = os.environ['api_address']
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
st.set_page_config(layout="wide", page_title="Movie recommender")

res = requests.get(url=f"{baseurl}unique_genres")
genres_list =res.json()["genres"]

res = requests.get(url=f"{baseurl}unique_movies")
movies_list =res.json()["movies"]

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

with open(os.path.join(output_folder, "mapping_username_user_id.json"), "r") as f:
    mapping_userid = json.loads(f.read())

if authentication_status:
    userid = mapping_userid[username]
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    with st.sidebar:
        type_model = st.radio(
            "Choose your model",
            ('User model', 'Movie model', 'Random'))
        genres = st.multiselect(
            'Choose your genre',
        genres_list)
    if type_model == 'Random':
        if genres:
            res = requests.get(
                url=f"{baseurl}random?user_id={userid}&subject={'&subject='.join(genres)}")
        else:
            res = requests.get(
                url=f"{baseurl}random?user_id={userid}")
        st.write(res.json()["movie"])
    elif type_model == 'Movie model':
        movie = st.selectbox(
            'Choose a movie',
            movies_list)
        if genres:
            res = requests.get(
                url=f"{baseurl}movie_model?user_id={userid}&subject={'&subject='.join(genres)}&movie_name={movie}")
        else:
            res = requests.get(
                url=f"{baseurl}movie_model?user_id={userid}&movie_name={movie}")
        st.write(res.json()["movie"])


elif authentication_status == False:
    with st.expander("Register New User"):
        try:
            if authenticator.register_user("Register user", preauthorization=False):
                st.success("User registered successfully")
        except Exception as e:
            st.error(e)

        with open("config.yaml", "w") as file:
            yaml.dump(config, file, default_flow_style=False)
    st.error('Username/password is incorrect')
elif authentication_status == None:
    with st.expander("Register New User"):
        try:
            if authenticator.register_user("Register user", preauthorization=False):
                st.success("User registered successfully")
        except Exception as e:
            st.error(e)

        with open("config.yaml", "w") as file:
            yaml.dump(config, file, default_flow_style=False)
    st.warning('Please enter your username and password')

