import pandas as pd
import os
import gc

class Data:
    def __init__(self):
        self.merged_path = '../ml-20m/merged.csv'
        self.final_path = '../ml-20m/final.csv'
        data = self.load_data()

    def load_data(self):
        if os.path.exists(self.final_path):
            return pd.read_csv(self.final_path)
        else:
            return self.prepare_data()

    def create_data(self):
        mov_df = pd.read_csv('../ml-20m/movies.csv')
        rat_df = pd.read_csv('../ml-20m/ratings.csv')
        gen_tag_df = pd.read_csv('../ml-20m/genome-tags.csv')
        gen_sco_df = pd.read_csv('../ml-20m/genome-scores.csv')
        tag_df = pd.read_csv('../ml-20m/tags.csv')
        link_df = pd.read_csv('../ml-20m/links.csv')
        mov_rat = pd.merge(mov_df, rat_df, on='movieId')
        del mov_df, rat_df
        gc.collect()

        gen_sco_tag = pd.merge(gen_tag_df, gen_sco_df, on='tagId')
        del gen_tag_df, gen_sco_df
        gc.collect()

        tag_link_df = pd.merge(tag_df, link_df, on='movieId')
        del tag_df, link_df
        gc.collect()

        gen_sco_tag = pd.merge(gen_sco_tag, tag_link_df, on='movieId')
        del tag_link_df
        gc.collect()

        # remove tags with less than 10% of relevance
        gen_sco_tag = gen_sco_tag[gen_sco_tag['relevance'] >= 0.15]

        #count number of rating and remove movies with less than 10 rating
        number_rating = mov_rat.groupby('title')['rating'].count().reset_index()
        number_rating.rename(columns={'rating':'number of rating'},inplace=True)
        mov_rat = pd.merge(mov_rat,number_rating)
        mov_rat = mov_rat[mov_rat['number of rating'] >= 50]

        df = pd.merge(mov_rat, gen_sco_tag, on=['movieId', 'userId'])
        df.to_csv(self.merged_path, index=False)
        return df

    def prepare_data(self):
        if os.path.exists(self.merged_path):
            df = pd.read_csv(self.merged_path)
        else:
            df= self.create_data()


        #Split title in title and year
        df['year'] = df['title'].str.extract(r'^.*\((\d{4})\)$')
        df['title'] = df['title'].str.extract(r'^(.*?)\s\(\d{4}\)$')

        df.to_csv(self.final_path, index=False)
        return df
