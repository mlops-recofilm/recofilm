from preprocessing.create_data import Data
from model.movie_model import MovieModel
from model.utils import split_data_random, check_overlap

TEST_SIZE = 0.3

df = Data(min_relevance=0.3).data
train, test, title_dict = split_data_random(df)
check_overlap(train, test)
MovieModel().fit(df, 10)
title = 'Star Wars: Episode IV - A New Hope (1977)'
recommendations = MovieModel().evaluate(df, title, 10, title_dict)
MovieModel().stability(df, title, 10, title_dict)
MovieModel().prediction_comparaison(df, ['Star Wars: Episode IV - A New Hope (1977)', 'Junior (1994)', 'Interview with the Vampire: The Vampire Chronicles (1994)'], 10, title_dict)
print(recommendations)
