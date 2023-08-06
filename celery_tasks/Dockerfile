FROM python:3.8-slim

# layer caching for faster builds
COPY requirements.txt /
RUN pip install -r /requirements.txt

ADD . /celery_tasks
WORKDIR /celery_tasks


ENTRYPOINT celery -A tasks worker -c 4 --loglevel=info
#-Q celery_worker
#ENTRYPOINT ['celery','-A','test_celery', 'worker','-c 4','--loglevel=info']