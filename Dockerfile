FROM python:3.9.6-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN pip install psycopg2-binary

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /app
EXPOSE 8000