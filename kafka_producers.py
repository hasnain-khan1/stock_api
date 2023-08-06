from kafka import KafkaProducer
import json
import random
import string

bootstrap_servers = 'localhost:9092'
topic = 'stock_data'

# Create a Kafka producer instance
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)


def send_message(message):
    try:
        data = json.dumps(message)
        msg = str(data).encode('utf-8')
        producer.send(topic, msg)
        print(f"Sent: {message}")
        return "ok"
    except Exception as e:
        print(f"Error sending message: {e}")


def random_string(length):
    # Helper function to generate a random string of given length
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_random_stock_data():
    # Function to generate a random stock data dictionary
    symbol = random_string(4)
    company_name = random_string(random.randint(5, 15))
    current_price = round(random.uniform(10, 1000), 2)
    high_volume = random.choice(['Yes', 'No'])
    closing_price = round(random.uniform(10, 1000), 2)

    stock_data = {
        'symbol': symbol,
        'company_name': company_name,
        'current_price': current_price,
        'high_volume': high_volume,
        'closing_price': closing_price
    }

    return stock_data


def generate_random_stock_list(num_stocks):
    stock_list = [generate_random_stock_data() for _ in range(num_stocks)]
    return stock_list


def send_data():
    random_stock_list = generate_random_stock_list(10)
    for data in random_stock_list:
        send_message(data)
