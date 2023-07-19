import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from joblib import dump, load


class MovieModel:

    @staticmethod
    def prepare_data(df: pd.DataFrame):
        df = df[['movieId', 'rating', 'userId']].drop_duplicates()
        rating_matrix = df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
        return csr_matrix(rating_matrix.values)

    def fit(self, df: pd.DataFrame, n_neighbors: int):
        rating_matrix = self.prepare_data(df)
        model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors)
        model.fit(rating_matrix)
        dump(model, 'user_model.joblib')

    def predict(self, df: pd.DataFrame, user_id: str, num_recommendations: int):
        model = load('user_model.joblib')
        rating_matrix = self.prepare_data(df)
        distances, indices = model.kneighbors(rating_matrix[user_id], n_neighbors=num_recommendations)

        # drop the first index being the movie itself
        indices = np.delete(indices, 0)

        # print titles of those movies
        recommendations = []
        for i in indices:
            recommendations.append(df['title'][i])
        return recommendations

