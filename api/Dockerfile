FROM python:3.9
WORKDIR /code
# #--no-cache-dir --upgrade
ADD api_requirements.txt /code/api/api_requirements.txt
ADD api.py /code/api/api.py
ADD api_utils /code/api/api_utils/
RUN pip install -r /code/api/api_requirements.txt
EXPOSE 8000
WORKDIR /code/api

CMD ["uvicorn", "api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]