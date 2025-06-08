import os
import pika


def connect_rabbit():
    rabbitmq_user = os.environ.get("RABBITMQ_USER")
    rabbitmq_pass = os.environ.get("RABBITMQ_PASS")
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "localhost")
    rabbitmq_port = int(os.environ.get("RABBITMQ_PORT", 5672))

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        credentials=credentials
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    return connection, channel


def publish_message(exchange: str, routing_key: str, message: str):
    connection, channel = connect_rabbit()

    try:
        # Declare or create the exchange if needed.
        channel.exchange_declare(exchange=exchange, exchange_type='direct', durable=True)

        # Publish the message to the exchange with the routing key
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2 # make the message persistent
            )
        )

        print(f"Message published to exchange '{exchange}' with routing key '{routing_key}': {message}", flush=True)

    except Exception as e:
        print(f"[ERROR] Failed to publish message: {e}", flush=True)
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()


