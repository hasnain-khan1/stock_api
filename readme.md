## Fast app with redis, Flower, Kafka and Celery

This app is created using Flask and Celery for the queueing system. RabbitMQ is used as a broker. This app will scrap the data from hacker news API which is a free API and will store the top news data in a local `.db` file.

## Installation

Install the  [Docker](https://docs.docker.com/engine/install/) according to your OS.

## Usage
Set the up the Celery app configurations
```python
celery_app = Celery('celery_worker',
                    broker=f'redis://{rdis_url}:{port}/db',
                    backend='rpc://')

```
Go to the main directory of the project and run the command
```bash
docker-compose up --build
```
This set up the docker container and You can access the app on Following URL for the fast api:
```
htpp://localhost:8000/docs
```

## Run the Tests

To run the pytests go to the main project directory and run the following command.
```bash
pytest tests/
```
## Run the Kafka Consumer and Producer

To run the producer run the command
```bash
python -m kafka_producer.py
```
This will insert the data in kafka topic

To start the consumer run the following command
```bash
python -m kafka_consumer.py
```
This will post the data to Fast api and then it will send to celery for data processing.