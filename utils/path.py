import os
from model_job.utils.utils import make_directory

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
DOCKER_VOLUME = os.path.join(ROOT_DIR, "docker_volume")
make_directory(DOCKER_VOLUME)
model_folder = os.path.join(DOCKER_VOLUME, "model_folder")
make_directory(model_folder)
data_folder = os.path.join(DOCKER_VOLUME, "data")
make_directory(data_folder)
input_data_folder = os.path.join(DOCKER_VOLUME, "inputs")
output_folder = os.path.join(DOCKER_VOLUME, "outputs")
make_directory(output_folder)