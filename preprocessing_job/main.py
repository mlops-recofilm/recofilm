from preprocessing_job.create_data import Data
from preprocessing_job.check_data import get_all_csv_information

get_all_csv_information()
df = Data(min_relevance=0.3).data
