import os
import json
import base64
import pandas as pd
import requests
import streamlit as st
import streamlit_authenticator as stauth
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import logging
import yaml
from yaml.loader import SafeLoader
import sys
sys.path.append('..')
from utils.path import output_folder

#baseurl = os.environ['api_address']
baseurl = 'http://localhost:8000/'
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
    password = ""  # Laissez le mot de passe vide

    # Encodez le nom d'utilisateur et le mot de passe en Base64
    credentials = f"{userid}:{password}"
    base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    headers = {
        "accept": "application/json",
        "Authorization": f"Basic {base64_credentials}"
    }
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    with st.sidebar:
        type_model = st.radio(
            "Choose your model",
            ('User model', 'Movie model'))
        genres = st.multiselect(
            'Choose your genre',
        genres_list)
        if st.button('Random movie'):
            if genres:
                res = requests.get(
                    url=f"{baseurl}random?user_id={userid}&subject={'&subject='.join(genres)}")
            else:
                res = requests.get(
                    url=f"{baseurl}random?user_id={userid}")
            reco_movie = res.json()["movie"]
    if type_model == 'Movie model':
        movie = st.selectbox(
            'Choose a movie',
            movies_list)
        if genres:
            res = requests.get(
                url=f"{baseurl}movie_model?user_id={userid}&subject={'&subject='.join(genres)}&movie_name={movie}")
        else:
            res = requests.get(
                url=f"{baseurl}movie_model?user_id={userid}&movie_name={movie}")
        reco_movie = res.json()["movie"]

    def data_upload():
        try:
            df = pd.DataFrame({'movie': [reco_movie], 'rating': None})
        except NameError:
            df = pd.DataFrame({'movie': [''], 'rating': None})
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
            cellEditorParams={"values": ["1", "2", "3", "4", "5"]},
        )
        gb.configure_grid_options(autoSizeColumn=True, autoHeight=True)

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
        data = grid_table["data"]
        st.write(grid_table["data"]
                 .loc[
                     (grid_table["data"]["rating"] != ""),
                     ["id", "tag understandable", "User category"],
                 ]
                 .to_dict(orient="list"))
        res = requests.post(
            url=f"{url}update_{type_perf}_data",
            headers={
                'Content-type': 'application/json'
            },
            json={"data": grid_table["data"]
                .loc[
                (grid_table["data"]["tag understandable"] != "-")
                | (grid_table["data"]["User category"] != "-"),
                ["id", "tag understandable", "User category"],
            ]
                .to_dict(orient="list")
                  }

        )


    grid_table = show_grid()
    st.button("Update", on_click=update, args=[grid_table])


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

