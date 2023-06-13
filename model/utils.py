import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


TEST_SIZE = 0.1


def split_data(df: pd.DataFrame):
    df['ranks'] = df.groupby('userId')['timestamp'].rank(method='first')
    df['counts'] = df['userId'].map(df.groupby('userId')['timestamp'].apply(len))
    df['split'] = df['ranks']/df['counts']
    train = df[df['split']<=1-TEST_SIZE]
    test = df[df['split']>1-TEST_SIZE]
    temp = train[['title', 'movieId']].drop_duplicates()
    title_dict = pd.Series(temp.movieId.values, index=temp.title).to_dict()
    return train, test, title_dict
