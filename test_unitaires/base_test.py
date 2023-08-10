import pandas as pd
from pathlib import Path
import sys,os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path,os.pardir))
sys.path.insert(0,parent_dir_path)

from model_job.model_utils import *
from model_job.model.utils import *

from utils.path import input_data_folder, output_folder
from utils.path import *
from preprocessing_job.create_data import Data


def test_existence_final_csv():
    assert get_last_final_csv(data_folder) != None

def test_existence_data_api_csv():
    """check if the file data_api.csv exist"""
    csv_files = [file for file in os.listdir(data_folder) if file.startswith("data") and file.endswith(".csv")]
    assert len(csv_files) != 0

def test_shape_final_csv():
    """check if final_*.csv is not empty """
    data_path = get_last_final_csv(data_folder)
    df = pd.read_csv(data_path)
    assert df.empty == False

def test_shape_data_api_csv():
    """check if data_api.csv is not empty """
    csv_files = [file for file in os.listdir(data_folder) if file.startswith("data") and file.endswith(".csv")]
    data_api_path = csv_files[0]
    df_api = pd.read_csv(os.path.abspath(data_api_path))
    assert df_api.empty == False

def test_nan_final_csv():
    """ check the Nan of the Dataframe final_*.csv"""
    data_path = get_last_final_csv(data_folder)
    df = pd.read_csv(data_path)
    assert df.isna().sum().all() == False

def test_type_final_csv():
    """check the variable type of the Dataframe final_*csv"""
    data_path = get_last_final_csv(data_folder)
    df = pd.read_csv(data_path)
    assert \
        list(df.select_dtypes(include='int64').columns) == ['movieId', 'userId', 'timestamp', 'tagId'] \
        and\
        list(df.select_dtypes(include='float64').columns) == ['rating', 'relevance']\
        #and\
        #list(df.select_dtypes(include='string').columns) == ['title','genres','tag','user_tag']

