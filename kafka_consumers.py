import json

from kafka import KafkaConsumer
import requests

bootstrap_servers = 'localhost:29092'

topic = 'stock_data'
url = 'http://127.0.0.1:8000/stocks/'

consumer = KafkaConsumer(topic, bootstrap_servers=bootstrap_servers, group_id=topic,
                         enable_auto_commit=True,
                         auto_offset_reset='latest',
                         )


def consume_messages():
    try:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        for message in consumer:
            message_value = message.value.decode('utf-8')
            print(f"Received: {message_value}")
            requests.post(url, headers=headers, json=json.loads(message_value))
            consumer.commit()

    except Exception as e:
        print(f"Error consuming message: {e}")


if __name__ == "__main__":
    consume_messages()
