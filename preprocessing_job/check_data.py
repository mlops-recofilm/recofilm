import numpy as np
import pandas as pd
import glob
import os
from utils.path import input_data_folder, output_folder


def get_information_data(path: str):
    """
    Load and write information about the data from the specified CSV file to a report file.

    Args:
        path (str): The path to the CSV file containing the data.

    Returns:
        None

    Writes:
        Information about the CSV file to a file named "rapport.txt".
    """
    df = pd.read_csv(path)
    with open(os.path.join(output_folder,"rapport.txt"), "a") as file:
        file.write(f"****** Information for File: {path} ******\n")
        file.write("****** Stat desc ******\n")
        file.write(str(df.describe()) + "\n")
        file.write("****** Correlation ******\n")
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        correlation_matrix = df[numeric_columns].corr()
        file.write(str(correlation_matrix) + "\n")
        file.write("****** NA ******\n")
        file.write(str((df.isna().sum()*100)/df.shape[0]) + "\n")
        file.write("****** Null ******\n")
        file.write(str((df.isnull().sum()*100)/df.shape[0]) + "\n")
        file.write("****** Valeurs uniques ******\n")
        file.write(str(df.nunique()) + "\n")


def get_all_csv_information():
    """
    Load and write information about all the CSV files in the specified csv_path list.

    Args:
        None

    Returns:
        None

    Writes:
        Information about each CSV file to a file named "rapport.txt".
        If the "rapport.txt" file already exists, it will be deleted before writing new information.
    """
    rapport_file = os.path.join(output_folder,"rapport.txt")
    if os.path.exists(rapport_file):
        os.remove(rapport_file)

    for path in glob.glob(os.path.join(input_data_folder, '*.csv')):
        get_information_data(path)

