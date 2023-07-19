FROM python:3.9 
WORKDIR /code
COPY requirements_api.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
# #--no-cache-dir --upgrade
COPY /api /code/api
COPY /ml-20m/ /code/ml-20m/
COPY /data/ /code/data/
WORKDIR /code/api
# ?? EXPOSE ${port_authent} 
CMD ["uvicorn", "api:app", "--reload", "--host", "0.0.0.0"]
# # CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]