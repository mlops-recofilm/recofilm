import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


class MovieModel:
    def __init__(self, df:pd.DataFrame):
        self.data = df[['movieId','rating', 'userId']]
        self.model = None
        self.rating_matrix = None

    def prepare_data(self):
        rating_matrix = self.data.pivot(index='movieId', columns='userId', values='rating').fillna(0)
        return csr_matrix(rating_matrix.values)

    def fit(self, n_neighbors: int):
        self.rating_matrix = self.prepare_data()
        self.model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors)
        self.model.fit(self.rating_matrix)

    def predict(self, df, movie_title: str, num_recommendations: int):
        movie_id = df[df['title'] == movie_title]['movieId'].unique()
        distances, indices = self.model.kneighbors(self.rating_matrix[movie_id], n_neighbors=num_recommendations)

        # drop the first index being the movie itself
        indices = np.delete(indices, 0)

        # print titles of those movies
        recommendations = []
        for i in indices:
            recommendations.append(df['title'][i])
        return recommendations

