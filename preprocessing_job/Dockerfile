FROM python:3.9
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
COPY /preprocessing_job /code/preprocessing_job
COPY /utils /code/utils
WORKDIR /code
CMD ["python", "preprocessing_job/main.py"]
