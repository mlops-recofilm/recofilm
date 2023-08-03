import pandas as pd

from model_utils import get_last_final_csv
from model_job.model.movie_model import MovieModel
from model_job.model.user_model import UserModel
from model_job.model.utils import split_data_random, check_overlap
from utils.path import data_folder

TEST_SIZE = 0.3

last_file = get_last_final_csv(data_folder)
df = pd.read_csv(last_file)
train, test, title_dict = split_data_random(df)
MovieModel().fit(df, 10)
title = 'Star Wars: Episode IV - A New Hope (1977)'
score, recommendations = MovieModel().evaluate(df, title, 10, title_dict)

#MovieModel().prediction_comparaison(df, ['Star Wars: Episode IV - A New Hope (1977)', 'Junior (1994)', 'Interview with the Vampire: The Vampire Chronicles (1994)'], 10, title_dict)
print(recommendations)
print(score)

UserModel().fit(df, 10)
user = 1644
score, recommendations = UserModel().evaluate(df, user, 10)
print(recommendations)
print(score)
#UserModel().stability(df, user, 10)
#UserModel().prediction_comparaison(df, [1644,1741], 10)
