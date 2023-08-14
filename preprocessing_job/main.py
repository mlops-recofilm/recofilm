import sys,os
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path,os.pardir))
sys.path.insert(0,parent_dir_path)


from check_data import get_all_csv_information
from create_data import Data

get_all_csv_information()
df = Data(min_relevance=0.3).data
