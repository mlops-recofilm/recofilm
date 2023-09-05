import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


TEST_SIZE = 0.4


def split_data_timestamp(df: pd.DataFrame):
    """
    Split the movie rating data into train and test sets based on timestamps.

    Args:
        df (pd.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', 'userId', and 'timestamp'.

    Returns:
        pd.DataFrame, pd.DataFrame, dict: The train and test DataFrames, and a dictionary mapping movie titles to their corresponding movie IDs.
    """
    df['ranks'] = df.groupby('userId')['timestamp'].rank(method='first')
    df['counts'] = df['userId'].map(df.groupby('userId')['timestamp'].apply(len))
    df['split'] = df['ranks']/df['counts']
    train = df[df['split']<=1-TEST_SIZE]
    test = df[df['split']>1-TEST_SIZE]
    temp = train[['title', 'movieId']].drop_duplicates()
    title_dict = pd.Series(temp.movieId.values, index=temp.title).to_dict()
    return train, test, title_dict


def split_data_random(df: pd.DataFrame):
    """
    Split the movie rating data into train and test sets randomly.

    Args:
        df (pd.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.

    Returns:
        pd.DataFrame, pd.DataFrame, dict: The train and test DataFrames, and a dictionary mapping movie titles to their corresponding movie IDs.
    """
    unique_combinations = df[['movieId', 'userId']].drop_duplicates()

    shuffled_combinations = unique_combinations.sample(frac=1, random_state=42)

    test_size = int(0.2 * len(shuffled_combinations))

    test_combinations = shuffled_combinations.iloc[:test_size]
    train_combinations = shuffled_combinations.iloc[test_size:]

    train_data = df.merge(train_combinations, on=['movieId', 'userId'], how='inner')
    test_data = df.merge(test_combinations, on=['movieId', 'userId'], how='inner')

    temp = train_data[['title', 'movieId']].drop_duplicates()
    title_dict = pd.Series(temp.movieId.values, index=temp.title).to_dict()
    return train_data, test_data, title_dict


def check_overlap(train_data, test_data):
    """
    Check if there is any overlap in movie and user combinations between train and test sets.

    Args:
        train_data (pd.DataFrame): The DataFrame containing the training data with columns 'movieId' and 'userId'.
        test_data (pd.DataFrame): The DataFrame containing the test data with columns 'movieId' and 'userId'.

    Returns:
        None
    """
    train_data = train_data[['movieId', 'userId']].drop_duplicates()
    test_data = test_data[['movieId', 'userId']].drop_duplicates()
    overlap = pd.merge(train_data[['movieId', 'userId']], test_data[['movieId', 'userId']], on=['movieId', 'userId'],
                       how='inner')

    if overlap.empty:
        print("Aucune combinaison 'movieId', 'userId' n'est présente dans les deux ensembles.")
    else:
        print(
            "Certaines combinaisons 'movieId', 'userId' sont présentes à la fois dans les ensembles de train et de test.")
        print(overlap)