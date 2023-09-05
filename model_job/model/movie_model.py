import pandas as pd
import numpy as np
import os
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from joblib import dump, load
import pickle
from pathlib import Path

from utils.path import model_folder, movie_model_unittest_folder


class MovieModel:
    """
    A class for movie recommendation using collaborative filtering.

    Args:
        df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
        n_neighbors (int): The number of neighbors to consider for recommendation.

    Methods:
        prepare_data(df: pd.DataFrame) -> scipy.sparse.csr.csr_matrix:
            Prepare the movie rating data and return it in a sparse CSR matrix format.

        fit(df: pd.DataFrame, n_neighbors: int) -> None:
            Fit the movie recommendation model using collaborative filtering.

        predict(df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict) -> List[str]:
            Generate movie recommendations based on a given movie title.

        evaluate(df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict) -> Tuple[float, List[str]]:
            Evaluate the model's recommendations by comparing them to actual ratings.

        stability(df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict) -> None:
            Assess the stability of the recommendations for a given movie.

        prediction_comparaison(df: pd.DataFrame, movie_title: list[str], num_recommendations: int, title_dict: dict) -> None:
            Compare movie recommendations for multiple movie titles.

    Example usage:
    ```
    movie_model = MovieModel()
    movie_model.fit(movie_ratings_df, n_neighbors=5)
    movie_title = 'Inception'
    num_recommendations = 10
    title_dict = {'Inception': 1234, 'The Dark Knight': 5678, ...}
    recommendations = movie_model.predict(movie_ratings_df, movie_title, num_recommendations, title_dict)
    print(recommendations)
    ```
    """
    @staticmethod
    def prepare_data(df: pd.DataFrame):
        """
        Prepare the movie rating data and return it in a sparse CSR matrix format.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.

        Returns:
            scipy.sparse.csr.csr_matrix: The sparse CSR matrix representing the movie rating data.
        """
        df = df[['movieId', 'rating', 'userId']].drop_duplicates()
        rating_matrix = df.pivot(index='movieId', columns='userId', values='rating').fillna(0)
        csr_array = csr_matrix(rating_matrix.values)
        return csr_array

    def fit(self, df: pd.DataFrame, n_neighbors: int):
        """
        Fit the movie recommendation model using collaborative filtering.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
            n_neighbors (int): The number of neighbors to consider for recommendation.

        Returns:
            None
        """
        rating_matrix = self.prepare_data(df)
        model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors)
        model.fit(rating_matrix)
        dump(model, os.path.join(model_folder,'movie_model.joblib'))

    def predict(self, df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict):
        """
        Generate movie recommendations based on a given movie title.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
            movie_title (str): The title of the movie for which recommendations are to be generated.
            num_recommendations (int): The number of movie recommendations to generate.
            title_dict (dict): A dictionary mapping movie titles to their corresponding movie IDs.

        Returns:
            List[str]: A list of recommended movie titles.
        """
        model = load(os.path.join(model_folder,'movie_model.joblib'))
        movie_id = title_dict[movie_title]
        rating_matrix = self.prepare_data(df)
        distances, indices = model.kneighbors(rating_matrix[movie_id], n_neighbors=num_recommendations)
        recommendations = df[['movieId', 'rating', 'userId','title']].drop_duplicates().reset_index(drop=True)['title'][indices[0]].to_list()
        return recommendations

    def evaluate(self,df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict):
        """
        Evaluate the model's recommendations by comparing them to actual ratings.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
            movie_title (str): The title of the movie for which recommendations are to be evaluated.
            num_recommendations (int): The number of movie recommendations to generate and evaluate.
            title_dict (dict): A dictionary mapping movie titles to their corresponding movie IDs.

        Returns:
            Tuple[float, List[str]]: A tuple containing the average rating of recommended movies and a list of recommended movie titles.
        """
        recommendations = self.predict(df,movie_title,num_recommendations, title_dict)
        user_eval = df[df['title'] == movie_title]['userId'].unique()
        sub_df = df[(df['userId'].isin(user_eval)) & (df['title'].isin(recommendations))][['movieId', 'rating', 'userId','title']].drop_duplicates()
        score = sub_df.groupby('title').agg({'rating': 'mean', 'userId': 'count'})
        score['rating_times_userId'] = score['rating'] * score['userId']
        cum_sum = score['rating_times_userId'].sum()/score['userId'].sum()
        print(score)
        return cum_sum, score.index

    def stability(self,df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict):
        """
        Assess the stability of the recommendations for a given movie and save results.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
            movie_title (str): The title of the movie for which stability of recommendations is to be assessed.
            num_recommendations (int): The number of movie recommendations to generate for assessing stability.
            title_dict (dict): A dictionary mapping movie titles to their corresponding movie IDs.

        Returns:
            None
        """
        i = 0
        recommendations = []
        while i <100:
            rec = self.predict(df,movie_title,num_recommendations, title_dict)
            recommendations.extend(rec)
            i+=1
        arr, count = np.unique(recommendations, return_counts=True)
        count = count/100
        dict_stability = {k:v for k,v in zip(arr, count)}
        print(dict_stability)

        with open(os.path.join(movie_model_unittest_folder, "dict_stability.pkl"), 'wb') as f:
            pickle.dump(dict_stability, f)

    def prediction_comparaison(self,df: pd.DataFrame, movie_title: list[str], num_recommendations: int, title_dict: dict):
        """
        Compare movie recommendations for multiple movie titles and save results.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
            movie_title (list[str]): A list of movie titles for which recommendations are to be compared.
            num_recommendations (int): The number of movie recommendations to generate and compare for each movie title.
            title_dict (dict): A dictionary mapping movie titles to their corresponding movie IDs.

        Returns:
            None
        """
        i = 0
        recommendations = []
        for m in movie_title:
            rec = self.predict(df,m,num_recommendations, title_dict)
            recommendations.extend(rec)
            i+=1
        arr, count = np.unique(recommendations, return_counts=True)
        count = count/len(movie_title)
        dict_pred_compar = {k:v for k,v in zip(arr, count)}
        print(dict_pred_compar)
        with open(os.path.join(movie_model_unittest_folder, "dict_prediction_comparaison.pkl"), 'wb') as f:
            pickle.dump(dict_pred_compar, f)


