import pandas as pd
import os
import gc


from utils.path import data_folder, input_data_folder


class Data:
    """
        A class for loading and preparing data.

        Args:
            add_link (bool): Whether to include movie links data. Default is False.
            min_relevance (float): The minimum relevance score for a tag to be included. Default is 0.15.
            min_rating (int): The minimum number of ratings for a movie to be included. Default is 50.
            min_tags (int): The minimum number of tags for a movie to be included. Default is 5.
            parse_date (bool): Whether to parse the release year from movie titles. Default is False.

        Attributes:
            add_link (bool): Whether to include movie links data.
            min_relevance (float): The minimum relevance score for a tag to be included.
            min_rating (int): The minimum number of ratings for a movie to be included.
            min_tags (int): The minimum number of tags for a movie to be included.
            parse_date (bool): Whether to parse the release year from movie titles.
            merged_path (str): The path to the merged CSV file.
            final_path (str): The path to the final CSV file.
            data (pandas.DataFrame): The loaded and prepared data.

        Methods:
            load_data(): Loads the data from the final CSV file or prepares it if the file does not exist.
            create_data(): Creates the data by merging the different csv data.
            prepare_data(): Prepares the data by parsing release years from movie titles and saving it to a CSV file.
        """
    def __init__(self, add_link: bool = False, min_relevance: float = 0.15, min_rating: int = 50, min_tags: int = 5, parse_date: bool = False):
        self.add_link = add_link
        self.min_relevance = max(0.15,min_relevance)
        self.min_rating = max(50, min_rating)
        self.min_tags = max(5, min_tags)
        self.parse_date = parse_date
        self.merged_path = os.path.join(data_folder,f'merged_{self.add_link}_{self.min_relevance}_{self.min_rating}_{self.min_tags}_{self.parse_date}.csv')
        self.final_path = os.path.join(data_folder,f'final_{self.add_link}_{self.min_relevance}_{self.min_rating}_{self.min_tags}_{self.parse_date}.csv')
        self.data = self.load_data()

    def load_data(self) -> pd.DataFrame:
        """
        Loads the data from the final CSV file or prepares it if the file does not exist.

        Returns:
            pandas.DataFrame: The loaded or prepared data.
        """
        if os.path.exists(self.final_path):
            return pd.read_csv(self.final_path)
        else:
            return self.prepare_data()

    def create_data(self) -> pd.DataFrame:
        """
        Creates the data by merging and filtering all csv.

        Returns:
            pandas.DataFrame: The created data.
        """
        mov_df = pd.read_csv(os.path.join(input_data_folder, 'movies.csv'))
        rat_df = pd.read_csv(os.path.join(input_data_folder, 'ratings.csv'))
        gen_tag_df = pd.read_csv(os.path.join(input_data_folder, 'genome-tags.csv'))
        gen_sco_df = pd.read_csv(os.path.join(input_data_folder, 'genome-scores.csv'))
        tag_df = pd.read_csv(os.path.join(input_data_folder, 'tags.csv'))
        if self.add_link:
            link_df = pd.read_csv(os.path.join(input_data_folder, 'links.csv'))
        tag_df.drop(columns=['timestamp'], inplace=True)
        mov_rat = pd.merge(mov_df, rat_df, on='movieId')
        del mov_df, rat_df
        gc.collect()

        gen_sco_tag = pd.merge(gen_tag_df, gen_sco_df, on='tagId')
        del gen_tag_df, gen_sco_df
        gc.collect()

        number_occ_tag = tag_df.groupby('tag')['movieId'].count().reset_index()
        number_occ_tag.rename(columns={'movieId': 'number of tags'}, inplace=True)
        tag_occ = pd.merge(tag_df, number_occ_tag)
        tag_occ = tag_occ[tag_occ['number of tags'] >= self.min_tags]
        tag_occ.drop(columns=['number of tags'], inplace=True)
        tag_occ.rename(columns={'tag': 'user tag'}, inplace=True)

        if self.add_link:
            tag_link_df = pd.merge(tag_occ, link_df, on='movieId')
            del tag_df, link_df, tag_occ
            gc.collect()

            gen_sco_tag = pd.merge(gen_sco_tag, tag_link_df, on='movieId')
            del tag_link_df
        else:
            gen_sco_tag = pd.merge(gen_sco_tag, tag_occ, on='movieId')
            del tag_df, tag_occ
        gc.collect()

        gen_sco_tag = gen_sco_tag[gen_sco_tag['relevance'] >= self.min_relevance]

        number_rating = mov_rat.groupby('title')['rating'].count().reset_index()
        number_rating.rename(columns={'rating':'number of rating'},inplace=True)
        mov_rat = pd.merge(mov_rat,number_rating)
        mov_rat = mov_rat[mov_rat['number of rating'] >= self.min_rating]
        mov_rat.drop(columns=['number of rating'], inplace = True)

        df = pd.merge(mov_rat, gen_sco_tag, on=['movieId', 'userId'])
        df.to_csv(self.merged_path, index=False)
        return df

    def prepare_data(self) -> pd.DataFrame:
        """
        Prepares the data by parsing release years from movie titles and saving it to a CSV file.

        Returns:
            pandas.DataFrame: The prepared data.
        """
        if os.path.exists(self.merged_path):
            df = pd.read_csv(self.merged_path)
        else:
            df = self.create_data()
        if self.parse_date:
            df['year'] = df['title'].str.extract(r'^.*\((\d{4})\)$')
            df['title'] = df['title'].str.extract(r'^(.*?)\s\(\d{4}\)$')

        df.to_csv(self.final_path, index=False)
        df[['movieId', 'rating', 'userId', 'genres','title']].drop_duplicates().to_csv(os.path.join(data_folder,f'data_api.csv'), index = False)
        return df
