FROM python:3.10
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY weather_project/ /app
CMD [ "python", "manage.py", "runserver", "0:8000" ]