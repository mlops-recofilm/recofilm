import pandas as pd
import numpy as np
import os
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from joblib import dump, load
from pathlib import Path
import pickle

from utils.path import model_folder, user_model_unittest_folder


class UserModel:
    """
    A class for user recommendation using collaborative filtering.

    Args:
        df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
        n_neighbors (int): The number of neighbors to consider for recommendation.

    Methods:
        prepare_data(df: pd.DataFrame) -> scipy.sparse.csr.csr_matrix:
            Prepare the user rating data and return it in a sparse CSR matrix format.

        fit(df: pd.DataFrame, n_neighbors: int) -> None:
            Fit the user recommendation model using collaborative filtering.

        predict(df: pd.DataFrame, user_id: int, num_recommendations: int) -> List[str]:
            Generate movie recommendations based on a given user_id.

        evaluate(df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict) -> Tuple[float, List[str]]:
            Evaluate the model's recommendations by comparing them to actual ratings.

        stability(df: pd.DataFrame, movie_title: str, num_recommendations: int) -> None:
            Assess the stability of the recommendations for a given user.

        prediction_comparaison(df: pd.DataFrame, users_id: list[str], num_recommendations: int) -> None:
            Compare recommendations for multiple users.

    Example usage:
    ```
    movie_model = MovieModel()
    movie_model.fit(movie_ratings_df, n_neighbors=5)
    movie_title = 'Inception'
    num_recommendations = 10
    title_dict = {'Inception': 1234, 'The Dark Knight': 5678, ...}
    recommendations = movie_model.predict(movie_ratings_df, movie_title, num_recommendations)
    print(recommendations)
    ```
    """
    @staticmethod
    def prepare_data(df: pd.DataFrame):
        """
        Prepare the user rating data and return it in a sparse CSR matrix format.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.

        Returns:
            scipy.sparse.csr.csr_matrix: The sparse CSR matrix representing the user rating data.
        """
        df = df[['movieId', 'rating', 'userId']].drop_duplicates()
        rating_matrix = df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
        csr_array = csr_matrix(rating_matrix.values)
        return csr_array

    def fit(self, df: pd.DataFrame, n_neighbors: int):
        """
        Fit the user recommendation model using collaborative filtering.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
            n_neighbors (int): The number of neighbors to consider for recommendation.

        Returns:
            None
        """
        rating_matrix = self.prepare_data(df)
        model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors)
        model.fit(rating_matrix)
        dump(model, os.path.join(model_folder,'user_model.joblib'))

    def get_similar_users(self,df, user, num_recommendations=5):
        model = load(os.path.join(model_folder, 'user_model.joblib'))
        distances, indices = model.kneighbors(df[df.index == user], n_neighbors=num_recommendations+1)
        users = []
        for i in range(1, len(distances[0])):
            user = df.index[indices[0][i]]
            users.append(user)
        return users, indices.flatten()[1:] , distances.flatten()[1:]/np.sum(distances.flatten()[1:])

    def predict(self, df: pd.DataFrame, user_id: int, num_recommendations: int):
        """
        Generate movie recommendations based on a given movie title.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
            user_id (int): The user_id for which recommendations are to be generated.
            num_recommendations (int): The number of movie recommendations to generate.

        Returns:
            List[str]: A list of recommended movie titles.
        """
        df = df[['movieId', 'rating', 'userId', 'title']].drop_duplicates()
        df = df.pivot(
            index='userId',
            columns='movieId',
            values='rating').fillna(0)
        similar_user_list,indices, weightage_list = self.get_similar_users(df, user_id, num_recommendations)
        mov_rtngs_sim_users = df.values[indices]
        movies_list = df.columns
        weightage_list = weightage_list[:, np.newaxis] + np.zeros(len(movies_list))
        new_rating_matrix = weightage_list * mov_rtngs_sim_users
        mean_rating_list = new_rating_matrix.sum(axis=0)
        n = min(len(mean_rating_list), num_recommendations)
        return list(movies_list[np.argsort(mean_rating_list)[::-1][:n]]), similar_user_list

    def evaluate(self,df: pd.DataFrame, user_id: int, num_recommendations: int):
        """
        Evaluate the model's recommendations by calculating the average rating of recommended movies.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
            user_id (int): The user_id for which recommendations are to be generated.
            num_recommendations (int): The number of movie recommendations to generate and evaluate.

        Returns:
            Tuple[float, List[str]]: A tuple containing the average rating of recommended movies and a list of recommended movie titles.
        """
        movies_recommendations, similar_users = self.predict(df,user_id,num_recommendations)
        sub_df = df[(df['userId'].isin(similar_users)) & (df['movieId'].isin(movies_recommendations))][['movieId', 'rating', 'userId','title']].drop_duplicates()
        score = sub_df.groupby('title').agg({'rating': 'mean', 'userId': 'count'})
        score['rating_times_userId'] = score['rating'] * score['userId']
        cum_sum = score['rating_times_userId'].sum()/score['userId'].sum()
        print(cum_sum)
        return cum_sum, score.index

    def stability(self,df: pd.DataFrame, user_id: int, num_recommendations: int):
        """
        Assess the stability of the recommendations for a given user.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
            user_id (int): The user_id for which recommendations are to be generated.
            num_recommendations (int): The number of movie recommendations to generate for assessing stability.

        Returns:
            None
        """
        i = 0
        recommendations = []
        while i <100:
            movies_recommendations, similar_users = self.predict(df,user_id,num_recommendations)
            recommendations.extend(similar_users)
            i+=1
        arr, count = np.unique(recommendations, return_counts=True)
        count = count/100
        dict_stability = {k:v for k,v in zip(arr, count)}
        print(dict_stability)
        with open(os.path.join(user_model_unittest_folder, "dict_stability.pkl"), 'wb') as f:
            pickle.dump(dict_stability, f)
        

    def prediction_comparaison(self,df: pd.DataFrame, users_id: list[int], num_recommendations: int):
        """
        Compare user recommendations for multiple users id.

        Args:
            df (pandas.DataFrame): The input DataFrame containing movie ratings data with columns 'movieId', 'rating', and 'userId'.
            users_id (list[str]): A list of user_id for which recommendations are to be compared.
            num_recommendations (int): The number of movie recommendations to generate and compare for each movie title.

        Returns:
            None
        """
        i = 0
        recommendations = []
        for u in users_id:
            movies_recommendations, similar_users = self.predict(df,u,num_recommendations)
            recommendations.extend(similar_users)
            i+=1
        arr, count = np.unique(recommendations, return_counts=True)
        count = count/len(users_id)
        dict_pred_compar = {k:v for k,v in zip(arr, count)}
        print(dict_pred_compar)
        with open(os.path.join(user_model_unittest_folder, "dict_prediction_comparaison.pkl"), 'wb') as f:
            pickle.dump(dict_pred_compar, f)

            



