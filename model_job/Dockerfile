FROM python:3.9
WORKDIR /code
# #--no-cache-dir --upgrade
ADD model_requirements.txt /code/model_job/model_requirements.txt
ADD training_pipeline.py /code/model_job/training_pipeline.py
ADD model_utils.py /code/model_job/model_utils.py
ADD __init__.py /code/model_job/__init__.py
COPY model /code/model_job/model/
RUN pip install -r /code/model_job/model_requirements.txt
WORKDIR /code/model_job
CMD ["python", "training_pipeline.py"]