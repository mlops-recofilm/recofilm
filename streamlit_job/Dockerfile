FROM python:3.9
WORKDIR /code
ADD streamlit_requierements.txt /code/streamlit_job/streamlit_requierements.txt
RUN pip install -r /code/streamlit_job/streamlit_requierements.txt
ADD __init__.py /code/streamlit_job/__init__.py
ADD dashboard.py /code/streamlit_job/dashboard.py
WORKDIR /code/streamlit_job
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]

