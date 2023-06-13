from preprocessing.create_data import Data
from model.movie_model import MovieModel
from model.utils import split_data

TEST_SIZE = 0.3

df = Data(min_relevance=0.3).data
train, test, title_dict = split_data(df)
MovieModel().fit(train, 10)
title = 'Star Wars: Episode IV - A New Hope (1977)'
recommendations = MovieModel().predict(test, title, 10, title_dict)
print(recommendations)
