import pandas as pd
import numpy as np
import os
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from joblib import dump, load


from model_job.utils.path import model_folder

class MovieModel:

    @staticmethod
    def prepare_data(df: pd.DataFrame):
        df = df[['movieId', 'rating', 'userId']].drop_duplicates()
        rating_matrix = df.pivot(index='movieId', columns='userId', values='rating').fillna(0)
        csr_array = csr_matrix(rating_matrix.values)
        return csr_array

    def fit(self, df: pd.DataFrame, n_neighbors: int):
        rating_matrix = self.prepare_data(df)
        model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors)
        model.fit(rating_matrix)
        dump(model, os.path.join(model_folder,'movie_model.joblib'))

    def predict(self, df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict):
        model = load(os.path.join(model_folder,'movie_model.joblib'))
        movie_id = title_dict[movie_title]
        rating_matrix = self.prepare_data(df)
        distances, indices = model.kneighbors(rating_matrix[movie_id], n_neighbors=num_recommendations)
        recommendations = df[['movieId', 'rating', 'userId','title']].drop_duplicates().reset_index(drop=True)['title'][indices[0]].to_list()
        return recommendations

    def evaluate(self,df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict):
        recommendations = self.predict(df,movie_title,num_recommendations, title_dict)
        user_eval = df[df['title'] == movie_title]['userId'].unique()
        sub_df = df[(df['userId'].isin(user_eval)) & (df['title'].isin(recommendations))][['movieId', 'rating', 'userId','title']].drop_duplicates()
        score = sub_df.groupby('title').agg({'rating': 'mean', 'userId': 'count'})
        score['rating_times_userId'] = score['rating'] * score['userId']
        cum_sum = score['rating_times_userId'].sum()/score['userId'].sum()
        print(score)
        return cum_sum, score.index

    def stability(self,df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict):
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

    def prediction_comparaison(self,df: pd.DataFrame, movie_title: list[str], num_recommendations: int, title_dict: dict):
        i = 0
        recommendations = []
        for m in movie_title:
            rec = self.predict(df,m,num_recommendations, title_dict)
            recommendations.extend(rec)
            i+=1
        arr, count = np.unique(recommendations, return_counts=True)
        count = count/len(movie_title)
        dict_stability = {k:v for k,v in zip(arr, count)}
        print(dict_stability)


