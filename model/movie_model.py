import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from joblib import dump, load


class MovieModel:

    @staticmethod
    def prepare_data(df: pd.DataFrame):
        df = df[['movieId', 'rating', 'userId']].drop_duplicates()
        rating_matrix = df.pivot(index='movieId', columns='userId', values='rating').fillna(0)
        return csr_matrix(rating_matrix.values)

    def fit(self, df: pd.DataFrame, n_neighbors: int):
        rating_matrix = self.prepare_data(df)
        model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors)
        model.fit(rating_matrix)
        dump(model, 'movie_model.joblib')

    def predict(self, df: pd.DataFrame, movie_title: str, num_recommendations: int, title_dict: dict):
        model = load('movie_model.joblib')
        movie_id = title_dict[movie_title]
        rating_matrix = self.prepare_data(df)
        distances, indices = model.kneighbors(rating_matrix[movie_id], n_neighbors=num_recommendations)

        # drop the first index being the movie itself
        #indices = np.delete(indices, 0)

        # print titles of those movies
        recommendations = df[['movieId', 'rating', 'userId','title']].drop_duplicates().reset_index(drop=True)['title'][indices[0]].to_list()
        return recommendations

