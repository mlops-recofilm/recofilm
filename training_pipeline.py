from preprocessing.create_data import Data
from model.movie_model import MovieModel

df = Data()
movie_model = MovieModel(df = df).fit(20)
