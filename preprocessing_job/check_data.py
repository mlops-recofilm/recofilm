import numpy as np
import pandas as pd
import glob

csv_path = glob.glob('../ml-20m/*csv')


def get_information_data(path:str):
    df = pd.read_csv(path)
    print(path)
    print("****** Stat desc ******")
    print(df.describe())
    print("****** Correlation ******")
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    correlation_matrix = df[numeric_columns].corr()
    print(correlation_matrix)
    print("****** NA ******")
    print((df.isna().sum()*100)/df.shape[0])
    print("****** Null ******")
    print((df.isnull().sum()*100)/df.shape[0])
    print("****** Valeurs uniques ******")
    print(df.nunique())


for path in csv_path:
    get_information_data(path)