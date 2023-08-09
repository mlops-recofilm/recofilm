FROM python:3.9
WORKDIR /code
ADD preprocessing_requirements.txt /code/preprocessing_job/preprocessing_requirements.txt
RUN pip install -r /code/preprocessing_job/preprocessing_requirements.txt
ADD __init__.py /code/preprocessing_job/__init__.py
ADD main.py /code/preprocessing_job/main.py
ADD check_data.py /code/preprocessing_job/check_data.py
ADD create_data.py /code/preprocessing_job/create_data.py
WORKDIR /code
CMD ["python", "preprocessing_job/main.py"]
