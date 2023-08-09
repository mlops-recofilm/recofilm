from check_data import get_all_csv_information
from create_data import Data


get_all_csv_information()
df = Data(min_relevance=0.3).data
